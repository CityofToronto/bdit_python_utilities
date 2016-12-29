# Congestion Mapping 
*Automating the creation of maps of congestion and reliability metrics for different time periods and time aggregations (year, quarter, month)*

## Purpose
Automate the generation of maps in QGIS so that looking at multiple metrics over time doesn't require a lot of manual layer creation and composer editing.

You can follow progress at [this Github milestone](https://github.com/CityofToronto/bdit_congestion/milestone/1).
## How to Use

### sql
This folder contains `sql` scripts to create the `congestion` schema ([`new_tables.sql`](sql/new_tables.sql)). From there [`aggregation_levels`](sql/aggregation_levels.sql) inserts aggregation levels into that table. [`process_congestion_metrics.sql`](sql/process_congestion_metrics.sql) creates functions for aggregating the congestion metrics (bti, tti) from the `inrix.agg_extract_hour` table and inserting them into `congestion.metrics`.

### python
This folder contains a python command-line application to iterate over a range of dates and metrics and print maps from QGIS.

#### Usage

## Challenges Solved

### Programming in PyQGIS

## Next Steps and How to Contribute
