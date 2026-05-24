/*

Creates all of the tables for the F1 fantasy program.
1. DRIVERS (id, forename, surname, other info?)
    - DRIVER_NUMBER_HIS (driver_id, number, season)
    - DRIVER_CONSTRUCTOR_HIS (driver_id, constructor_id, season)
2. CONSTRUCTORS (id, name) (1, Mercedes) - no need for driver id
3. RACES (id, name, season) (1, miami, 2026)
4. SESSIONS (id, race_id, session_type, date)
5. RESULTS (id, session_id, driver_id, position, points, status?)

I can add other data later on e.g. driver details like DOB once the tables have been populated. (UPDATE DRIVERS SET DOB = 28/10/2000 WHERE NAME = 'TOM DAWES'
*/