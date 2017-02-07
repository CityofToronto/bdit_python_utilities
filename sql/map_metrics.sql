/*
Author: Raphael Dumas
Inputs: aggregation level, aggregation period, timeperiod starttime, timeperiod end time, metric column, "Metric Name"
Grabs Top 50 Worst Segments in a format appropriate for mapping in QGIS
*/

CREATE OR REPLACE FUNCTION congestion.map_metric(agg_lvl varchar(9), agg_period DATE, starttime TIME, endtime TIME, metric TEXT, metric_name TEXT)
RETURNS SETOF congestion.map_metrics
AS $$
BEGIN 

	/*Value checks on inputs*/
	
	
	 IF agg_lvl NOT IN (SELECT agg_level FROM congestion.aggregation_levels) THEN
		RAISE EXCEPTION 'Incorrect agg_lvl'; 
	 END IF;
	 
	RETURN QUERY EXECUTE format($x$
		SELECT row_number() OVER (PARTITION BY metrics.agg_period ORDER BY metrics.%I DESC) AS "Rank",
			tmc_from_to_lookup.street_name::TEXT AS "Street",
			gis.twochar_direction(inrix_tmc_tor.direction) AS "Dir",
			tmc_from_to_lookup.from_to::TEXT AS "From - To",
			to_char(metrics.%I, '0D99'::text) AS %I,
			inrix_tmc_tor.geom
		 FROM congestion.metrics
		 JOIN congestion.aggregation_levels USING (agg_id)
		 JOIN gis.inrix_tmc_tor USING (tmc)
		 JOIN gis.tmc_from_to_lookup USING (tmc)
		 WHERE inrix_tmc_tor.sum_miles > 0.124274 AND aggregation_levels.agg_level = %L
		 AND metrics.timeperiod = timerange(%L::time, %L::time) AND metrics.agg_period = %L::DATE
		 ORDER BY metrics.%I DESC LIMIT 50 
		 $x$, metric, metric, metric_name, agg_lvl, starttime, endtime, agg_period, metric);
END;
$$
LANGUAGE plpgsql;
