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

**Attributes:**
 - `logger`: logging.logger object for logging messages
 - `dbsettings`: dictionary of database connection string parameters
 - `stylepath`: string filepath to load the metric layer's style 
 - `templatepath`: string filepath to load the print composer template
 - `projectfile`: (optional) if using standalone script string filepath to load the project
 - `console`: (optional) boolean value indicating whether QGIS Python console is used
 - `iface`: (optional) qgis.utils.iface object, used in QGIS Python console
 
**Public functions:**
 - `get_background_layers(layernamelist = BACKGROUND_LAYERNAMES)`: Return background layers
 - `update_labels(labels_dict = None, labels_update = None)`: Change the labels in the QgsComposition using a dictionary of update values
 - `update_canvas(iface = None)`: Update canvas with the new layer + background layers
 - `print_map(printpath, filetype = 'png')`: Print the map to the specified location
 - `clear_layer()`: Remove added layer
 - `close_project()`: Close the project, if loaded

##### congestion_mapper

Inherits from `iteration_mapper`. 

**Attributes:**  
 - `SQL`: base `sql` scripts for each metric type
 - `COMPOSER_LABELS`: content to change in the QGIS composer labels
 - `METRICS`: dictionary of metric attributes
 - `BACKGROUND_LABELS`: background layer names
 - `agg_level`: string representing the aggregation level
 - `metric`: dictionary of metric attributes derived from METRICS

**Additional functions:**  
 - `load_agg_layer()`: loads a layer of metrics based on the specific metric, aggregation level, timeperiod, and aggregation period
 - `set_metric()`: Set the metric for mapping based on the provided key
 - `update_table()`: Update the table in the composition to use current metric layer


##### parsing_utils

Parsing utilities for `map_metric.py` includign parsing command-line arguments. 

**Public Functions**:
 - `parse_args(args, prog = None, usage = None)`:
        Parse command line argument
 - `get_yyyymmdd(yyyy, mm, **kwargs)`:
        Combine integer yyyy and mm into a string date yyyy-mm-dd. 
 - `fullmatch(regex, string, flags=0)`:
        Emulate python-3.4 re.fullmatch().
 - `format_fromto_hr(hour1, hour2)`:
        Format hour1-hour2 as a string and append AM/PM
 - `validate_multiple_yyyymm_range(years_list, agg_level)`:
        Validate a list of pairs of yearmonth strings
 - `get_timerange(time1, time2)`:
        Validate provided times and create a timerange string to be inserted into PostgreSQL

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