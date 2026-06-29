/*
Generates a unified leaderboard for a specific Grand Prix weekend (by race name)
showing each driver's performance across all three Qualifying sessions (Q1-Q3) 
alongside their final race finishing position.
*/
SELECT rr2.name,
       rr2.circuit,
       rs.session_type,
       rdch.code,
       -- Pivot the rows into columns
       MAX(CASE WHEN qt.qualifying_round = 1 THEN qt.lap_time END) AS Q1,
       MAX(CASE WHEN qt.qualifying_round = 2 THEN qt.lap_time END) AS Q2,
       MAX(CASE WHEN qt.qualifying_round = 3 THEN qt.lap_time END) AS Q3,
       rr1.pos AS "Final Position"
  FROM qualifying_times qt
  LEFT JOIN race_sessions rs ON qt.session_id = rs.session_id
  LEFT JOIN race_results rr1 ON qt.session_id = rr1.session_id
                            AND qt.driver_id = rr1.driver_id
  LEFT JOIN race_races rr2 ON rs.race_id = rr2.race_id
  LEFT JOIN race_driver_code_history rdch ON qt.driver_id = rdch.driver_id
                                         AND rr2.season = rdch.season
 WHERE rr2.name = "Monaco"
 GROUP BY qt.driver_id, rr2.name, rr2.circuit, rs.session_type, rdch.code, rr1.pos
 ORDER BY session_type ASC, rr1.pos ASC;