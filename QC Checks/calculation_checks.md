# Walkthrough Congestion Metrics from Access Database: TMC C09-04848

Apologies for how ugly this is, but in any case here's a rundown. I am going to trace the calculations through foor TMC C09-04848 (Lake Shore Blvd WB, Yonge St - York St)

## Step 1A: Average Speed by Month
Constraints:

- Weekday (Monday-Friday)
- 17:00 - 18:00
- Arterials only (`INRIX_speed85.type<3`, `INRIX_speed85.HwyArt=2`)

```SQL
SELECT DAY_MONTH.Month, DAY_MONTH.tmc, [Miles]*1.60934 AS Length, [speed85]/Avg([speed_wtd]) AS TTI, Avg(DAY_MONTH.speed_wtd) AS AvgOfspeed_wtd, Sum(DAY_MONTH.Count) AS SumOfcount, Avg(DAY_MONTH.speed) AS AvgOfspeed, INRIX_speed85.speed85, INRIX_speed85.nightspeed INTO [Average Speed TTI Monthly AM]
FROM (INRIX_speed85 INNER JOIN DAY_MONTH ON INRIX_speed85.tmc = DAY_MONTH.tmc) INNER JOIN [Toronto City Inrix with Steeles] ON DAY_MONTH.tmc = [Toronto City Inrix with Steeles].Tmc
WHERE (((INRIX_speed85.Type)<3) AND ((DAY_MONTH.weekday)>1 And (DAY_MONTH.weekday)<7) AND ((DAY_MONTH.time15)>170 And (DAY_MONTH.time15)<180) AND ((INRIX_speed85.HwyArt)=2) AND (DAY_MONTH.tmc)="C09-04848"))
GROUP BY DAY_MONTH.Month, DAY_MONTH.tmc, [Miles]*1.60934, INRIX_speed85.speed85, INRIX_speed85.nightspeed
ORDER BY [speed85]/Avg([speed_wtd]) DESC;
```

Output:

| Month | Length      | TTI         | AvgOfspeed_wtd | SumOfcount | AvgOfspeed  | speed85 | nightspeed | 
|-------|-------------|-------------|----------------|------------|-------------|---------|------------| 
| 1     | 0.361915879 | 3.044252118 | 16.29300008    | 1115       | 16.88899989 | 49.6    | 34         | 
| 2     | 0.361915879 | 3.165486    | 15.66899996    | 1124       | 15.67350006 | 49.6    | 34         | 
| 3     | 0.361915879 | 3.496035266 | 14.1874999     | 1195       | 14.30849996 | 49.6    | 34         | 
| 4     | 0.361915879 | 3.298859324 | 15.03550019    | 1196       | 15.4295002  | 49.6    | 34         | 
| 5     | 0.361915879 | 3.52510572  | 14.07049999    | 999        | 14.17749996 | 49.6    | 34         | 
| 6     | 0.361915879 | 4.254406637 | 11.65850005    | 1122       | 11.60049996 | 49.6    | 34         | 
| 7     | 0.361915879 | 4.540669194 | 10.92350001    | 1173       | 11.1085001  | 49.6    | 34         | 
| 8     | 0.361915879 | 4.030717962 | 12.30550003    | 1032       | 12.30699992 | 49.6    | 34         | 
| 9     | 0.361915879 | 4.556310852 | 10.88600001    | 1105       | 11.13150001 | 49.6    | 34         | 
| 10    | 0.361915879 | 4.777269453 | 10.38249998    | 1164       | 10.54900002 | 49.6    | 34         | 
| 11    | 0.361915879 | 5.493105969 | 9.029499936    | 1009       | 8.980000091 | 49.6    | 34         | 
| 12    | 0.361915879 | 3.572457526 | 13.88399992    | 963        | 14.03099992 | 49.6    | 34         | 

## Step 1B: Average Speed by Quarter
Constraints:

- Weekday (Monday-Friday)
- 17:00 - 18:00
- Arterials only (`INRIX_speed85.type<3`, `INRIX_speed85.HwyArt=2`)

```SQL
SELECT [Lookup_Month Quarter].Quarter, DAY_MONTH.tmc, [Miles]*1.60934 AS Length, [speed85]/Avg([speed_wtd]) AS TTI, Avg(DAY_MONTH.speed_wtd) AS AvgOfspeed_wtd, Sum(DAY_MONTH.Count) AS SumOfcount, Avg(DAY_MONTH.speed) AS AvgOfspeed, INRIX_speed85.speed85, INRIX_speed85.nightspeed INTO [Average Speed TTI Quarterly AM]
FROM ((INRIX_speed85 INNER JOIN DAY_MONTH ON INRIX_speed85.tmc = DAY_MONTH.tmc) INNER JOIN [Toronto City Inrix with Steeles] ON DAY_MONTH.tmc = [Toronto City Inrix with Steeles].Tmc) INNER JOIN [Lookup_Month Quarter] ON DAY_MONTH.month = [Lookup_Month Quarter].Month
WHERE (((INRIX_speed85.Type)<3) AND ((DAY_MONTH.weekday)>1 And (DAY_MONTH.weekday)<7) AND ((DAY_MONTH.time15)>170 And (DAY_MONTH.time15)<180) AND ((INRIX_speed85.HwyArt)=2) AND (DAY_MONTH.tmc)="C09-04848")
GROUP BY [Lookup_Month Quarter].Quarter, DAY_MONTH.tmc, [Miles]*1.60934, INRIX_speed85.speed85, INRIX_speed85.nightspeed
ORDER BY [speed85]/Avg([speed_wtd]) DESC;
```

| Quarter | Length      | TTI         | AvgOfspeed_wtd | SumOfcount | AvgOfspeed  | speed85 | nightspeed | 
|---------|-------------|-------------|----------------|------------|-------------|---------|------------| 
| 1       | 0.361915879 | 3.224303626 | 15.38316665    | 3434       | 15.62366664 | 49.6    | 34         | 
| 2       | 0.361915879 | 3.650234865 | 13.58816675    | 3317       | 13.73583337 | 49.6    | 34         | 
| 3       | 0.361915879 | 4.361717712 | 11.37166669    | 3310       | 11.51566668 | 49.6    | 34         | 
| 4       | 0.361915879 | 4.469005308 | 11.09866661    | 3136       | 11.18666668 | 49.6    | 34         | 

## Step 1C: Average Speed by Year
Constraints:

- Weekday (Monday-Friday)
- 17:00 - 18:00
- Arterials only (`INRIX_speed85.type<3`, `INRIX_speed85.HwyArt=2`)

```SQL
SELECT DAY_MONTH.tmc, [Miles]*1.60934 AS Length, [speed85]/Avg([speed_wtd]) AS TTI, Avg(DAY_MONTH.speed_wtd) AS AvgOfspeed_wtd, Sum(DAY_MONTH.Count) AS SumOfcount, Avg(DAY_MONTH.speed) AS AvgOfspeed, INRIX_speed85.speed85, INRIX_speed85.nightspeed INTO [Average Speed TTI Annual AM]
FROM (INRIX_speed85 INNER JOIN DAY_MONTH ON INRIX_speed85.tmc = DAY_MONTH.tmc) INNER JOIN [Toronto City Inrix with Steeles] ON DAY_MONTH.tmc = [Toronto City Inrix with Steeles].Tmc
WHERE (((INRIX_speed85.Type)<3) AND ((DAY_MONTH.weekday)>1 And (DAY_MONTH.weekday)<7) AND ((DAY_MONTH.time15)>170 And (DAY_MONTH.time15)<180) AND ((INRIX_speed85.HwyArt)=2) AND (DAY_MONTH.tmc)="C09-04848")
GROUP BY DAY_MONTH.tmc, [Miles]*1.60934, INRIX_speed85.speed85, INRIX_speed85.nightspeed
ORDER BY [speed85]/Avg([speed_wtd]) DESC;
```

| Length      | TTI         | AvgOfspeed_wtd | SumOfcount | AvgOfspeed  | speed85 | nightspeed | 
|-------------|-------------|----------------|------------|-------------|---------|------------| 
| 0.361915879 | 3.856795722 | 12.86041667    | 13197      | 13.01545834 | 49.6    | 34         | 
