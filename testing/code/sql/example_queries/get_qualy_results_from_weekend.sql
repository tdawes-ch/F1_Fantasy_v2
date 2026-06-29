/*
Generates a unified leaderboard for a specific Grand Prix weekend (by race name)
showing each driver's performance across all three Qualifying sessions (Q1-Q3) 
alongside their final race finishing position.
*/
SELECT rr2.name,
       rr2.circuit,
       rs.session_type,
       rdch.code,
       q1.lap_time AS Q1,
       q2.lap_time AS Q2,
       q3.lap_time AS Q3,
       rr1.pos AS "Final Position"
  FROM race_results rr1
  -- Start from race_results or sessions to anchor the drivers
  LEFT JOIN race_sessions rs ON rr1.session_id = rs.session_id
  LEFT JOIN race_races rr2 ON rs.race_id = rr2.race_id
  LEFT JOIN race_driver_code_history rdch ON rr1.driver_id = rdch.driver_id
                                         AND rr2.season = rdch.season
  -- Join qualifying 3 distinct times
  LEFT JOIN qualifying_times q1 ON rr1.session_id = q1.session_id AND rr1.driver_id = q1.driver_id AND q1.qualifying_round = 1
  LEFT JOIN qualifying_times q2 ON rr1.session_id = q2.session_id AND rr1.driver_id = q2.driver_id AND q2.qualifying_round = 2
  LEFT JOIN qualifying_times q3 ON rr1.session_id = q3.session_id AND rr1.driver_id = q3.driver_id AND q3.qualifying_round = 3
 WHERE rr2.name = "Monaco"
   AND rr2.season = 2026
   AND rs.session_type LIKE "%Qualifying%"
 ORDER BY q3.lap_time DESC;