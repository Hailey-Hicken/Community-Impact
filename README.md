# Community-Impact
This code aims to automate the process of assessing how trails connect people to nearby community assets, such as grocery stores, schools, parks, and healthcare facilities.

The project is broken into two tools, each detailed below.

## 1. Service Area Solver  

This tool performs a service area network analysis using a line input and a network dataset, iterating through each record in the input feature layer.

----

### Data Requirements:

*Inputs are listed in the order they appear in the tool:*<br>  

- Trail: A line feature layer used to identify source points that will act as facilities in the Service Area Analysis.
- Field to Name Outputs After: A field used to name the output files, including the points and service areas.
- Search Distance: The distance (in meters) for selecting trail junction points; at least 10 meters is recommended.<br>  

- Network Dataset: The network dataset for the service area analysis. Ensure travel modes are defined and named without spaces (e.g., PedAndTransit, not Ped And Transit).
- Junctions: Junction points from the network feature dataset.
- Travel Modes: Modes of travel to analyze (e.g., driving, biking, walking).
- Cutoffs: The time or distance (in minutes) used to generate areas around a trail.<br>  

- Point Output Folder: An empty folder where the source points will be saved.
- Service Area Output Location: Specify a location to save outputs.<br>  
    
### Outputs

The tool generates:
1. Source points shapefiles in the designated folder.
2. A geodatabase for each travel mode, containing service areas for each trail.
3. A shapefile for each travel mode, merging all service areas.

## 2. Spatial Join (New and Improved)

This tool streamlines the process of attaching community asset data to service areas by counting the number of assets within each area.

---

### Data Description:

*Inputs are listed in the order they appear in the tool:*<br>

- Input Polygon: The polygon feature layer to which the information will be joined.  
- Input Field: A unique field used to organize the output table, ideally a primary key.<br>

- Join Feature: The feature layer to be joined (can be any input).  
- Pivot Field: The field used for pivoting data.  

### Outputs

This tool appends data to the input polygon’s attribute table, it does not create a new feature layer.
