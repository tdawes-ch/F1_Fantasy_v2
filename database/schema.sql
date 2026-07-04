/*

Creates all of the tables for the F1 fantasy program.
1. DRIVERS (id, forename, surname, other info?)
    - DRIVER_NUMBER_HIS (driver_id, number, season)
    - DRIVER_CONSTRUCTOR_HIS (driver_id, constructor_id, season)
2. CONSTRUCTORS (id, name) (1, Mercedes) - no need for driver id
3. RACES (id, name, season) (1, miami, 2026)
4. SESSIONS (id, race_id, session_type, date)
5. RESULTS (id, session_id, driver_id, position, points, status?)

*/

-- SCRAPER DATA TABLES
-- Master scraper table (all)
CREATE TABLE IF NOT EXISTS scrape_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT, -- www.url/to/page
    filepath TEXT, -- path/to/saved.html
    last_scraped TIMESTAMP -- dd/mm/yyy HH:MM:SS
);

-- season data
CREATE TABLE IF NOT EXISTS scrape_seasons (
    year INTEGER PRIMARY KEY,
    url TEXT, -- www.url/to/season.html
    filepath TEXT UNIQUE, -- path/to/year.html
    expected_races INTEGER, -- 24
    scraped_races INTEGER DEFAULT 0, -- 20
    has_races BOOLEAN DEFAULT 0, -- 1
    scraped BOOLEAN DEFAULT 0, -- 1
    last_scraped TIMESTAMP, -- dd/mm/yyy HH:MM:SS,
    FOREIGN KEY (url) REFERENCES scrape_log(url)
);

-- weekend data
CREATE TABLE IF NOT EXISTS scrape_race_weekends (
    race_id INTEGER PRIMARY KEY, -- 1258
    year INTEGER, -- 2021
    round INTEGER, -- 3
    race_name TEXT, -- Spain
    circuit TEXT, -- Circuit De Catalunya
    city TEXT, -- Barcelona
    from_date TEXT, -- Store as 'YYYY-MM-DD'
    to_date TEXT, -- Store as 'YYYY-MM-DD'
    url TEXT UNIQUE, -- www.f1.com
    filepath TEXT UNIQUE, -- path/to/html
    scraped BOOLEAN DEFAULT 0, -- 0
    has_sessions BOOLEAN DEFAULT 0,
    last_scraped TIMESTAMP, -- dd/mm/yyy HH:MM:SS
    FOREIGN KEY (year) REFERENCES seasons(year),
    FOREIGN KEY (url) REFERENCES scrape_log(url)
);

-- session data
CREATE TABLE IF NOT EXISTS scrape_sessions (
    session_id INTEGER PRIMARY KEY,
    race_id INTEGER, -- 1144
    year INTEGER, -- 2020
    session_type TEXT, -- FP1, FP2, FP3, Quali, Race
    url TEXT UNIQUE, -- www.url/to/session
    filepath TEXT UNIQUE, -- path/to/session.html
    scraped BOOLEAN DEFAULT 0,
    has_data BOOLEAN DEFAULT 0, 
    last_scraped TIMESTAMP, -- dd/mm/yyy HH:MM:SS
    FOREIGN KEY (year) REFERENCES scrape_seasons(year),
    FOREIGN KEY (race_id) REFERENCES scrape_race_weekends(round),
    FOREIGN KEY (url) REFERENCES scrape_log(url)
);

-- f1 data tables
-- 1. CONSTRUCTORS
CREATE TABLE IF NOT EXISTS race_constructors (
    constructor_id TEXT PRIMARY KEY, -- mercedes
    name TEXT NOT NULL UNIQUE -- Mercedes
);

-- 2. DRIVERS
CREATE TABLE IF NOT EXISTS race_drivers (
    driver_id TEXT PRIMARY KEY, -- lewis_hamilton
    forename TEXT NOT NULL, -- Lewis
    surname TEXT NOT NULL, -- Hamilton
    dob DATE, -- 28/10/2000
    nationality TEXT, -- British
    FOREIGN KEY (driver_id) REFERENCES race_drivers (driver_id) ON DELETE CASCADE
);

-- 2.a Driver code history (verstappen: VES -> VER when vergne left)
CREATE TABLE IF NOT EXISTS race_driver_code_history (
    driver_id TEXT, -- max_verstappen, vos_verstappen
    code TEXT, -- VER, HAM, LEC
    season INTEGER,  -- 2020
    PRIMARY KEY (driver_id, season),
    FOREIGN KEY (driver_id) REFERENCES race_drivers (driver_id) ON DELETE CASCADE,
    FOREIGN KEY (season) REFERENCES race_seasons (season)
);

-- 3. DRIVER NUMBER HISTORY
CREATE TABLE IF NOT EXISTS race_driver_number_history (
    driver_id TEXT, -- max_verstappen, jos_verstappen
    number INTEGER NOT NULL, -- 33
    season INTEGER NOT NULL, -- 2021
    PRIMARY KEY (driver_id, season),
    FOREIGN KEY (driver_id) REFERENCES race_drivers (driver_id) ON DELETE CASCADE,
    FOREIGN KEY (season) REFERENCES race_seasons (season) 
);

-- 4. DRIVER CONSTRUCTOR HISTORY
CREATE TABLE IF NOT EXISTS race_driver_constructor_history (
    driver_id TEXT, -- lewis_hamilton
    constructor_id INTEGER, -- mercedes
    season INTEGER NOT NULL, -- 2020
    PRIMARY KEY (driver_id, constructor_id, season),
    FOREIGN KEY (driver_id) REFERENCES race_drivers (driver_id) ON DELETE CASCADE,
    FOREIGN KEY (constructor_id) REFERENCES race_constructors (constructor_id) ON DELETE CASCADE
);

-- 5. RACES (Links to your existing scrape_seasons log table)
CREATE TABLE IF NOT EXISTS race_races (
    race_id INTEGER PRIMARY KEY AUTOINCREMENT, -- 1202
    name TEXT NOT NULL, -- Azerbaijan
    circuit TEXT, -- Baku City Circuit
    city TEXT, -- Baku
    season INTEGER NOT NULL, -- 2020
    from_date TEXT, -- Store as 'YYYY-MM-DD'
    to_date TEXT, -- Store as 'YYYY-MM-DD'
    round INTEGER, -- Helps sort the races in chronological calendar order
    FOREIGN KEY (season) REFERENCES race_seasons (season)
);

-- 6. SESSIONS
CREATE TABLE IF NOT EXISTS race_sessions (
    session_id INTEGER PRIMARY KEY AUTOINCREMENT, -- 12472
    race_id INTEGER NOT NULL, -- 1247
    session_type TEXT NOT NULL, -- 'FP1', 'FP2', 'FP3', 'Qualifying', 'Sprint', 'Race'
    date TEXT, -- Store as 'YYYY-MM-DD HH:MM:SS'
    FOREIGN KEY (race_id) REFERENCES race_races (race_id) ON DELETE CASCADE
);

-- 7. RESULTS
-- a. Keep race_results focused on the classification
CREATE TABLE IF NOT EXISTS race_results (
    session_id INTEGER, -- 12821
    driver_id TEXT, -- lewis_hamilton
    pos INTEGER, -- 1
    points REAL DEFAULT 0.0, -- 25.0
    status TEXT, -- NULL (DNF, DNS, DSQ, NC, etc.)
    PRIMARY KEY (session_id, driver_id)
    FOREIGN KEY (session_id) REFERENCES race_sessions(session_id),
    FOREIGN KEY (driver_id) REFERENCES race_drivers (driver_id)
);

-- b. Separate Qualifying times
CREATE TABLE IF NOT EXISTS qualifying_times (
    session_id INTEGER, -- 12821
    driver_id TEXT, -- lewis_hamilton
    qualifying_round INTEGER, -- 1 for Q1, 2 for Q2, 3 for Q3
    lap_time REAL, -- 1:22.210 (stored in seconds.milliseconds though)
    PRIMARY KEY (session_id, driver_id, qualifying_round),
    FOREIGN KEY (session_id) REFERENCES race_sessions(session_id),
    FOREIGN KEY (driver_id) REFERENCES race_drivers(driver_id)
);

-- c. Scalable Lap times table
CREATE TABLE IF NOT EXISTS lap_times (
    session_id INTEGER, -- 12821
    driver_id TEXT, -- lewis_hamilton
    is_total BOOLEAN, -- used to distinguish if lap_number is the number that the event ocurred on (e.g. fastest lap) or the number of laps in a session for prac sessions
    lap_number INTEGER, -- 3 (number of total laps in practice sessions) NOTE TO SELF: USE LAP NUMBER TO ESTIMATE RELIABILITY / DNF PROBABILITY
    lap_time REAL, -- Time in seconds
    UNIQUE (session_id, driver_id, lap_number, is_total) NULLS NOT DISTINCT,
    FOREIGN KEY (driver_id) REFERENCES race_drivers(driver_id),
    FOREIGN KEY (session_id) REFERENCES race_sessions(session_id)
);

-- d. Scalable Pit stops table
CREATE TABLE IF NOT EXISTS pit_stops (
    session_id INTEGER, -- 2020
    driver_id TEXT, -- lewis_hamilton
    stop_number INTEGER, -- 2
    lap_number INTEGER, -- 15
    duration REAL, -- Duration in seconds
    PRIMARY KEY (session_id, driver_id, stop_number),
    FOREIGN KEY (driver_id) REFERENCES race_drivers(driver_id),
    FOREIGN KEY (session_id) REFERENCES race_sessions(session_id)
);

-- e. Race duration
CREATE TABLE IF NOT EXISTS race_duration (
    session_id INTEGER, -- 2020
    driver_id TEXT, -- lewis_hamilton
    n_laps INTEGER, -- 44
    time_type TEXT, -- TOTAL, GAP, LAPPED, STATUS
    duration REAL, -- actual time value (full val for TOTAL, gap value (e.g. 1.82) for GAP, no. of laps (e.g. 1, 3) for LAPPED)
    PRIMARY KEY (session_id, driver_id),
    FOREIGN KEY (driver_id) REFERENCES race_drivers(driver_id),
    FOREIGN KEY (session_id) REFERENCES race_sessions(session_id)
);

-- 8. SEASONS
CREATE TABLE IF NOT EXISTS race_seasons (
    season INTEGER PRIMARY KEY, -- 2020
    total_sessions INTEGER, -- 22
    actual_sessions INTEGER -- 22
);


/*FANTASY SCRAPED DATA TABLES*/
CREATE TABLE IF NOT EXISTS fantasy_driver_prices (
    driver_id TEXT,
    price INTEGER, -- Dollar price amount e.g. 24500000
    date TEXT,
    PRIMARY KEY (driver_id, date),
    FOREIGN KEY (driver_id) REFERENCES race_drivers(driver_id)
);

CREATE TABLE IF NOT EXISTS fantasy_constructor_prices (
    constructor_id TEXT,
    price INTEGER, -- Dollar price amount e.g. 24500000
    date TEXT,
    PRIMARY KEY (constructor_id, date),
    FOREIGN KEY (constructor_id) REFERENCES race_constructors(constructor_id)
);

CREATE TABLE IF NOT EXISTS fantasy_scraping (
    url TEXT,
    date TEXT,
    is_processed BOOLEAN DEFAULT 0,
    filepath TEXT, -- path/to/saved.html
    PRIMARY KEY (url, date),
    FOREIGN KEY (url) REFERENCES scrape_log(url)
);