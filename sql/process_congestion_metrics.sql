/*
Author: Raphael Dumas
Inputs: aggregation level, from month, to month
Processes aggregate Inrix data into Travel Time Index and Buffer Time Index over the specified period and using the specified aggregation level. The aggregation level is used in the date_trunc() function in order to do a GROUP BY the dates truncated to that particular period. 
*/

CREATE OR REPLACE FUNCTION congestion.process_metrics(agg_lvl varchar(9), from_mon DATE, to_mon DATE)
RETURNS int
AS $$
BEGIN 
	/*Value checks on inputs*/
	
	 IF agg_lvl NOT IN (SELECT agg_level FROM congestion.aggregation_levels) THEN
		RAISE EXCEPTION 'Incorrect agg_lvl'; 
	 END IF;
	 
	 IF from_mon > to_mon THEN 
		RAISE EXCEPTION '% after % ', from_mon, to_mon; 
	 END IF;

	 IF extract('day' FROM from_mon) <> 1 OR extract('day' FROM to_mon) <> 1 THEN
		RAISE EXCEPTION 'Month parameters must be at the start of the month';
	 END IF;
	/*END Value checks on inputs*/

	 /*Actual aggregation function*/
	 INSERT INTO congestion.metrics 
	 SELECT tmc, 
	 timerange(	time_15_continuous/10*interval '1 hour' + '00:00'::TIME,
			time_15_continuous/10*interval '1 hour' + CASE WHEN time_15_continuous >=230 THEN '00:59:59.99'::TIME ELSE '01:00'::TIME END
		) as timeperiod, --Transform time15 into hour range
	 agg_id, 
	 date_trunc(agg_lvl, dt) as period,	  --Truncates the date to a given period based on the specified aggregation level
	 AVG(GREATEST( ITT.speed_overnight/AEH.avg_speed,1.0)) AS tti,
	 percentile_cont(0.5) WITHIN GROUP (ORDER BY avg_speed)/(percentile_cont(0.05) WITHIN GROUP (ORDER BY avg_speed)) - 1 as bti -- (T95-T50)/T50 = s_50/s_05 - 1 
	 
	 FROM inrix.agg_extract_hour AEH
	 INNER JOIN (SELECT * FROM gis.inrix_tmc_tor WHERE speed_overnight > 0) ITT USING (tmc)
	 CROSS JOIN congestion.aggregation_levels
	 WHERE agg_level = agg_lvl 
		AND dt >= from_mon AND dt < to_mon 
		AND extract('isodow' FROM dt) < 6 --weekdays
	 GROUP BY tmc, hh, agg_id, period;

	RETURN 1;
 END;
$$LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION congestion.process_metrics(agg_lvl varchar(9), from_mon DATE, to_mon DATE, timeperiod timerange)
RETURNS int
AS $$
BEGIN 
	/*Value checks on inputs*/
	
	 IF agg_lvl NOT IN (SELECT agg_level FROM congestion.aggregation_levels) THEN
		RAISE EXCEPTION 'Incorrect agg_lvl'; 
	 END IF;
	 
	 IF from_mon > to_mon THEN 
		RAISE EXCEPTION '% after % ', from_mon, to_mon; 
	 END IF;

	 IF extract('day' FROM from_mon) <> 1 OR extract('day' FROM to_mon) <> 1 THEN
		RAISE EXCEPTION 'Month parameters must be at the start of the month';
	 END IF;
	/*END Value checks on inputs*/

	 /*Actual aggregation function*/
	 INSERT INTO congestion.metrics 
	 SELECT tmc, 
	 timeperiod, --Transform time15 into hour range
	 agg_id, 
	 date_trunc(agg_lvl, dt) as period,	  --Truncates the date to a given period based on the specified aggregation level
	 AVG(GREATEST( ITT.speed_overnight/AEH.avg_speed,1.0)) AS tti,
	 percentile_cont(0.5) WITHIN GROUP (ORDER BY avg_speed)/(percentile_cont(0.05) WITHIN GROUP (ORDER BY avg_speed)) - 1 as bti -- (T95-T50)/T50 = s_50/s_05 - 1 
	 
	 FROM inrix.agg_extract_hour AEH
	 INNER JOIN (SELECT * FROM gis.inrix_tmc_tor WHERE speed_overnight > 0) ITT USING (tmc)
	 CROSS JOIN congestion.aggregation_levels
	 WHERE agg_level = agg_lvl 
		AND dt >= from_mon AND dt < to_mon 
		AND extract('isodow' FROM dt) < 6 --weekdays
		AND time_15_continuous/10*interval '1 hour' + '00:00'::TIME <@ timeperiod
	 GROUP BY tmc, timeperiod, agg_id, period;

	RETURN 1;
 END;
$$LANGUAGE plpgsql;
