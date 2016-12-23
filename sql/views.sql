DROP VIEW IF EXISTS congestion.least_reliable_annual_am;

CREATE OR REPLACE VIEW congestion.least_reliable_annual_am AS
SELECT row_number() OVER (PARTITION BY agg_period ORDER BY bti DESC) AS "Rank",
 street_name AS "Street",
 direction AS "Dir", 
 from_to AS "From - To",
 to_char(bti, '9D99') as "Buffer Time Index", 
 agg_period AS "Year",
 geom,
 gid

FROM congestion.metrics 
INNER JOIN congestion.aggregation_levels USING (agg_id)
INNER JOIN gis.inrix_tmc_tor USING (tmc)
INNER JOIN gis.tmc_from_to_lookup USING (tmc)
WHERE sum_miles > 0.124274 AND agg_level = 'year' AND timeperiod = timerange('08:00'::TIME, '09:00'::TIME) 
ORDER BY bti DESC;

DROP VIEW IF EXISTS congestion.least_reliable_annual_pm;
CREATE OR REPLACE VIEW congestion.least_reliable_annual_pm AS
SELECT row_number() OVER (PARTITION BY agg_period ORDER BY bti DESC) AS "Rank",
 street_name AS "Street",
 direction AS "Dir", 
 from_to AS "From - To",
 to_char(bti, '9D99') as "Buffer Time Index", 
 agg_period AS "Year",
 geom,
 gid

FROM congestion.metrics 
INNER JOIN congestion.aggregation_levels USING (agg_id)
INNER JOIN gis.inrix_tmc_tor USING (tmc)
INNER JOIN gis.tmc_from_to_lookup USING (tmc)
WHERE sum_miles > 0.124274 AND agg_level = 'year' AND timeperiod = timerange('17:00'::TIME, '18:00'::TIME)
ORDER BY bti DESC