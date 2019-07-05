<<<<<<< HEAD
# vfh_charts

## `geo.ttc(con)`

Returns a geopandas dataframe of the TTC subway network.

## `geo.island(con)`

Returns a geopandas dataframe of the Toronto Island.
=======
# README
>>>>>>> 901293dbb0c6c346e29b1e476ee64ade19bc6de9

## `charts.chloro_map(con, df, lower, upper, title, **kwargs)`

This function creates a chloropleth map. It returns a matplotlib `fig` and `ax` object so that the map can continued be annotated and modified. 

The following arguments must be passed in order for the function to run.

|argument|variable type|description|
|-----|-----|-----|
con|SQL Connection Object|Used to additional layers from the SQL database.
df|GeoPandas DataFrame|Data for the chloropleth map. The data must only contain 2 columns; the first column has to be the `geom` column and the second has to be the data that needs to be mapped.
lower|int|Lower bound for the colourmap
upper|int|Upper bound for the colourmap
title|str|Text string for the title text

Additionally, there are optional arguments that can be passed to the function

|argument|variable type|default|description|
|-----|-----|-----|-----|
subway|boolean|`False`|Flag to plot the subway network on the map. False indicates the subway network does not show up.
island|boolean|`True`|Flag to plot the Toronto Islands as having no data. True indicates the islands are coloured the same as the Waterfront neighbourhood.
cmap|str|`YlOrRd`|String to specify colourmap for the map.
unit|str|`None`|Specifies if a unit should be added to the legend box. The automatic placement of the unit only works if the upper or lower are whole numbers.
nbins|int|`2`|Number of ticks in the colourmap 
<<<<<<< HEAD

=======
>>>>>>> 901293dbb0c6c346e29b1e476ee64ade19bc6de9
