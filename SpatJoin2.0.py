# Import necessary libraries
import os			# Allows interaction with operating system
import arcpy			# ArcGIS Python library
import tempfile			# Used for creating temporary files

# Allow script to overwrite existing outputs
arcpy.env.overwriteOutput = True


# Defines input parameters
poly_in = arcpy.GetParameterAsText(0)
InField = arcpy.GetParameterAsText(1)
point_in = arcpy.GetParameterAsText(2)
PivotField = arcpy.GetParameterAsText(3)

#Sets Temporary File Aliases
out = "in_memory\\SpatJoin"	# Temp output for spatial join
out2 = "in_memory\\Stats"	# Temp output for summary stats
out3 = "in_memory\\PivotTable"	# Temp output for Pivot Table

# Perform a spatial join between the input polygons and points
# This creates an intermediate layer where attributes of points are joined to polygons
join = arcpy.analysis.SpatialJoin(
    target_features = poly_in,
    join_features = point_in,
    out_feature_class = out,
    join_operation = 'JOIN_ONE_TO_MANY'
    )

# Calculate summary statistics on the joined data
# This step aggregates data by counting the number of joined points
arcpy.analysis.Statistics(
    in_table=join,
    out_table=out2,
    statistics_fields="JOIN_COUNT COUNT",
    case_field=f"{PivotField};{InField}",
)

# Create a pivot table from the summary statistics
# This reorganizes the data for easier analysis
arcpy.management.PivotTable(
    in_table=out2,
    fields=InField,
    pivot_field=PivotField,
    value_field="FREQUENCY",
    out_table=out3
)

# Removes <Null> fields if any (don't name a field "F" >:( Threat
if "F" in [field.name for field in arcpy.ListFields(out3)]:
    arcpy.management.DeleteField(out3, "F")

# Join the pivot table back to the original polygon layer
arcpy.management.JoinField(poly_in,InField,out3,InField)

# Clean up: Delete any duplicate or intermediary fields created during the join process
arcpy.management.DeleteField(poly_in,f'{InField}_1')
