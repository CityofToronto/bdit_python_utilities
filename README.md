# Congestion Mapping 
*Automating the creation of maps of congestion and reliability metrics for different time periods and time aggregations (year, quarter, month)*

## Purpose
Automate the generation of maps in QGIS so that looking at multiple metrics over time doesn't require a lot of manual layer creation and composer editing.

You can follow progress at [this Github milestone](https://github.com/CityofToronto/bdit_congestion/milestone/1).
## How to Use

### sql
This folder contains `sql` scripts to create the `congestion` schema ([`new_tables.sql`](sql/new_tables.sql)) including the creation of a custom `timerange` type to contain timeperiods. From there [`aggregation_levels`](sql/aggregation_levels.sql) inserts aggregation levels into that table. [`process_congestion_metrics.sql`](sql/process_congestion_metrics.sql) creates functions for aggregating the congestion metrics (bti, tti) from the `inrix.agg_extract_hour` table and inserting them into `congestion.metrics`.

### python
This folder contains a python command-line application to iterate over a range of dates and metrics and print maps from QGIS.
This application is currently only tested with QGIS `2.14.X`

#### Contents:

##### iteration_mapper

Base object for iterating map creation with PyQGIS. 

##### congestion_mapper

Inherits from `iteration_mapper`. Includes:  
 - `SQL`: base `sql` scripts for each metric type
 - `COMPOSER_LABELS`: content to change in the QGIS composer labels
 - `BACKGROUND_LABELS`: background layer names

Additional methods:  
 - `load_agg_layer()`: loads a layer of metrics based on the specific metric, aggregation level, timeperiod, and aggregation period
 - `set_metric()`: Set the metric for mapping based on the provided key
 - `update_table()`: Update the table in the composition to use current metric layer


##### parsing_utils

##### map_metric




## Usage

### Setup
1. Run the files in the [`sql` folder](#sql) to set up the congestion schema.
2. Process congestion metrics in the database using the `process_congestion_metrics` function
3. The Python element requires a working [QGIS installation](http://www.qgis.org/en/site/forusers/download.html)
4. Set up a Python virtual environment for developing with QGIS based on [these instructions](http://gis.stackexchange.com/a/223325/36886).

### Using the Python application

#### In the QGIS Python Console

#### Command-line Application

## Challenges Solved

### Programming in PyQGIS
What a killer

## Next Steps and How to Contribute
This project is currently a work in progress. Have a look at the [project kanban board](https://github.com/CityofToronto/bdit_congestion/projects/1) and the [opened issues in the milestone](https://github.com/CityofToronto/bdit_congestion/milestone/1)