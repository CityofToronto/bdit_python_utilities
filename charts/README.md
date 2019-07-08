# README

## Regular Information Charts Kit

This module was inspired by charts created for the VFH Bylaw Review Report. There was a need to develop a standardized brand and design language for everything BDITTO produces, so this module aims to produce a regularized set of charts and maps that are consistent with previous charts we create. All of the chart/map producing functions returns a matplotlib `fig` and `ax` object so that the figure can be furthere modified using matplotlib functions.

### `geo.ttc(con)`

Returns a geopandas dataframe of the TTC subway network.

### `geo.island(con)`

Returns a geopandas dataframe of the Toronto Island.

### `charts.chloro_map(con, df, lower, upper, title, **kwargs)`

This function creates a chloropleth map.

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

### `charts.line_chart(data, ylab, xlab, **kwargs)`

Produces a simple line chart. The xaxis is not formatted by this function and requires further manipulation with matplotlib. In addition, annotation boxes must be added on manually with a something like this:

```python
fig.text(0.94, 0.96, '176,000', transform=ax.transAxes, wrap = True, fontsize=9, fontname = 'Libre Franklin',
         verticalalignment='top', ha = 'center', bbox=props, color = purple)
```

The function defines the styling with the `props` variable, so the only manipulations needed is the positioning and the text itself.

The following arguments must be passed in order for the function to run.

|argument|variable type|description|
|-----|-----|-----|
data|Series or list|Data for the chart
ylab|str|Label for the yaxis
xlab|str|Label for the xaxis

Additionally, there are optional arguments that can be passed to the function

|argument|variable type|default|description|
|-----|-----|-----|-----|
ymin|int|0|Lower bound for the yaxis
ymax|int|The maximum value of the dataset|Upper bound for the yaxis
yinc|int|One-third of the range of the data|Interval for the yaxis ticks

### `charts.tow_chart(data, ylab, **kwargs)`

Produces a 7-Day time of week chart that shows data points for each hour during one week. The xaxis is fixed to the 168 hours that produces the week, and the data must be ordered so that the first entry represents Monday at midnight.

The following arguments must be passed in order for the function to run.

|argument|variable type|description|
|-----|-----|-----|
data|Series or list|Data for the chart
ylab|str|Label for the yaxis

Additionally, there are optional arguments that can be passed to the function

|argument|variable type|default|description|
|-----|-----|-----|-----|
ymin|int|0|Lower bound for the yaxis
ymax|int|The maximum value of the dataset|Upper bound for the yaxis
yinc|int|One-third of the range of the data|Interval for the yaxis ticks