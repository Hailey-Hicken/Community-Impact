# Import necessary libraries
import os  # For handling file paths and directory operations
import arcpy  # For ArcGIS geoprocessing and spatial analysis
import re  # For sanitizing file names

# Function to sanitize file names by replacing invalid characters with underscores
def sanitize_name(name):
    # Replace any character that is not a word character (alphanumeric or underscore) with an underscore
    return re.sub(r'[^\w]', '_', name)

# --- Parameters for Part 1: Service Area Source Point Extraction ---
lines = arcpy.GetParameterAsText(0)  # Trail (line) data as input
searchDistance = arcpy.GetParameter(2)  # Search distance in meters for selecting junctions
junctions = arcpy.GetParameterAsText(4)  # Input junctions feature layer
field_name = arcpy.GetParameterAsText(1)  # Field used for naming outputs
point_output = arcpy.GetParameterAsText(7)  # Folder for saving output source point shapefiles

# --- Parameters for Part 2: Service Area Analysis ---
ND = arcpy.GetParameterAsText(3)  # Network dataset for the analysis
Cutoffs = arcpy.GetParameter(6)  # Cutoff values (time or distance) for service area generation
travel_modes = arcpy.GetParameterAsText(5)  # Travel modes as a semicolon-separated string
travel_modes_list = travel_modes.split(';')  # Convert travel modes into a list
SA_output = arcpy.GetParameterAsText(8)  # Output folder for geodatabase results

# --- PART 1: Extract Junction Points Along Trails ---

# Create a layer from the junctions if it does not already exist
if not arcpy.Exists("junctions_layer"):
    junctions_layer = arcpy.management.MakeFeatureLayer(junctions, "junctions_layer")
else:
    junctions_layer = "junctions_layer"

# Use a search cursor to iterate over each trail segment
with arcpy.da.SearchCursor(lines, ['Shape@', field_name]) as searcher:
    for row in searcher:
        x = row[0]  # Geometry of the trail segment
        name = row[1]  # Value of the field used for naming

        # Select junctions intersecting the trail segment within the search distance
        selection = arcpy.management.SelectLayerByLocation(
            in_layer=junctions_layer,
            overlap_type='INTERSECT',
            select_features=x,
            search_distance=f"{searchDistance} Meters"
        )

        # Sanitize the name and prepare the output file name
        sanitized_name = sanitize_name(str(name)).replace('__', '_').replace('___', '_')
        filename = f"{sanitized_name}_source.shp"

        # Export selected features to a shapefile
        arcpy.conversion.FeatureClassToFeatureClass(
            in_features=selection,
            out_path=point_output,
            out_name=filename
        )

    arcpy.AddMessage(f"Successfully added points to {point_output}.")

# --- PART 2: Service Area Analysis ---

# Check out the Network Analyst extension
arcpy.CheckOutExtension('network')

# Iterate over each travel mode in the list
for mode in travel_modes_list:
    # Retrieve available travel modes from the network dataset
    travel = arcpy.nax.GetTravelModes(ND)
    travelmode = travel[mode]  # Get the current travel mode configuration

    # Create a geodatabase for storing results for this travel mode
    gdb_name = f"{sanitize_name(mode)}Results.gdb"
    output_gdb = os.path.join(SA_output, gdb_name)

    # Create the geodatabase if it doesn't already exist
    if not arcpy.Exists(output_gdb):
        arcpy.management.CreateFileGDB(SA_output, gdb_name)
        print(f"Geodatabase {gdb_name} created.")
    else:
        print(f"Geodatabase {gdb_name} already exists.")

    # Get all shapefiles in the output folder for source points
    files = [os.path.join(point_output, f) for f in os.listdir(point_output) if f.endswith('.shp')]

    # List to hold exported service area files for merging
    export_list = []

    # Process each source point shapefile
    for file in files:
        # Create a Service Area solver object
        SA = arcpy.nax.ServiceArea(ND)

        # Set properties for the service area solver
        SA.timeUnits = arcpy.nax.TimeUnits.Minutes
        SA.defaultImpedanceCutoffs = Cutoffs
        SA.travelMode = travelmode
        SA.outputType = arcpy.nax.ServiceAreaOutputType.Polygons
        SA.geometryAtOverlap = arcpy.nax.ServiceAreaOverlapGeometry.Dissolve

        # Sanitize file name for use in outputs
        file_name = os.path.splitext(os.path.basename(file))[0]
        sanitized_name = sanitize_name(file_name)

        # Load the facilities into the Service Area solver
        SA.load(arcpy.nax.ServiceAreaInputDataType.Facilities, file)

        # Solve the Service Area
        result = SA.solve()

        # Export results if the solve succeeded
        if result.solveSucceeded:
            sanitized_name = sanitized_name.replace('_source', '')
            output = f"ServiceArea_{sanitized_name}"
            exported_fc = os.path.join(output_gdb, output)
            result.export(arcpy.nax.ServiceAreaOutputDataType.Polygons, exported_fc)
            export_list.append(exported_fc)

    # Merge all service areas and perform a spatial join with the input lines
    merge = arcpy.management.Merge(export_list, f'{mode}_ServiceArea_noData')
    join = arcpy.analysis.SpatialJoin(
        target_features=merge,
        join_features=lines,
        out_feature_class=f'{mode}_ServiceArea',
        match_option='LARGEST_OVERLAP'
    )

    # Remove unnecessary fields from the join result
    arcpy.management.DeleteField(join, ['Name', 'Join_Count', 'FromBreak', 'ToBreak', 'FacilityOID', 'FacilityID', 'Target_FID'])

    # Save the final feature class to the output folder
    arcpy.management.CopyFeatures(join, os.path.join(SA_output, f'{mode}_ServiceArea'))

arcpy.AddMessage('Done!')