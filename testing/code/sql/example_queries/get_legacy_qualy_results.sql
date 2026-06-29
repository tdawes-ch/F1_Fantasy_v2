/*
Generates a leaderboard for a specific Grand Prix weekend (by race name) showing the lap times in the qualifying sessions
*/
SELECT rr2.name,
       rr2.circuit,
       rs.session_type,
       rdch.code,
       qt.qualifying_round,
       qt.lap_time,
       rr1.pos
  FROM qualifying_times qt
  LEFT JOIN race_results rr1 ON qt.session_id = rr1.session_id
                            AND qt.driver_id = rr1.driver_id
  LEFT JOIN race_sessions rs ON qt.session_id = rs.session_id
    LEFT JOIN race_races rr2 ON rs.race_id = rr2.race_id
    LEFT JOIN race_drivers rd ON qt.driver_id = rd.driver_id
        LEFT JOIN race_driver_code_history rdch ON rd.driver_id = rdch.driver_id
                                               AND rr2.season = rdch.season
 WHERE rr2.season = 1986
   AND rr2.name = "Monaco"
 ORDER BY rs.session_type ASC, rr1.pos ASC;