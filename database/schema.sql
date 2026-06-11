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
    url TEXT,
    filepath TEXT,
    last_scraped TIMESTAMP
);

-- season data
CREATE TABLE IF NOT EXISTS scrape_seasons (
    year INTEGER PRIMARY KEY,
    url TEXT,
    filepath TEXT UNIQUE,
    expected_races INTEGER,
    scraped_races INTEGER DEFAULT 0,
    has_races BOOLEAN DEFAULT 0,
    scraped BOOLEAN DEFAULT 0,
    last_scraped TIMESTAMP
);

-- weekend data
CREATE TABLE IF NOT EXISTS scrape_race_weekends (
    race_id INTEGER PRIMARY KEY, -- 1258
    year INTEGER, -- 2021
    round INTEGER, -- 3
    race_name TEXT, -- Spain
    circuit TEXT, -- Circuit De Catalunya
    city TEXT, -- Barcelona
    url TEXT UNIQUE, -- www.f1.com
    filepath TEXT UNIQUE, -- path/to/html
    scraped BOOLEAN DEFAULT 0, -- 0
    has_sessions BOOLEAN DEFAULT 0,
    last_scraped TIMESTAMP,
    FOREIGN KEY (year) REFERENCES seasons(year)
);

-- session data
CREATE TABLE IF NOT EXISTS scrape_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    race_id INTEGER,
    year INTEGER,
    session_type TEXT,   -- FP1, FP2, FP3, Quali, Race
    url TEXT UNIQUE,
    filepath TEXT UNIQUE,
    scraped BOOLEAN DEFAULT 0,
    has_data BOOLEAN DEFAULT 0,
    last_scraped TIMESTAMP,
    FOREIGN KEY (year) REFERENCES scrape_seasons(year),
    FOREIGN KEY (race_id) REFERENCES scrape_race_weekends(round)
);

-- f1 data tables
-- 1. CONSTRUCTORS
CREATE TABLE IF NOT EXISTS race_constructors (
    constructor_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    nationality TEXT
);

-- 2. DRIVERS
CREATE TABLE IF NOT EXISTS race_drivers (
    driver_id INTEGER PRIMARY KEY AUTOINCREMENT,
    forename TEXT NOT NULL,
    surname TEXT NOT NULL,
    dob DATE,
    nationality TEXT,
    code TEXT UNIQUE -- e.g., 'HAM', 'VER', 'LEC'
);

-- 3. DRIVER NUMBER HISTORY
CREATE TABLE IF NOT EXISTS race_driver_number_history (
    driver_id INTEGER,
    number INTEGER NOT NULL,
    season INTEGER NOT NULL,
    PRIMARY KEY (driver_id, season),
    FOREIGN KEY (driver_id) REFERENCES race_drivers (driver_id) ON DELETE CASCADE
);

-- 4. DRIVER CONSTRUCTOR HISTORY
CREATE TABLE IF NOT EXISTS race_driver_constructor_history (
    driver_id INTEGER,
    constructor_id INTEGER,
    season INTEGER NOT NULL,
    PRIMARY KEY (driver_id, constructor_id, season),
    FOREIGN KEY (driver_id) REFERENCES race_drivers (driver_id) ON DELETE CASCADE,
    FOREIGN KEY (constructor_id) REFERENCES race_constructors (constructor_id) ON DELETE CASCADE
);

-- 5. RACES (Links to your existing scrape_seasons log table)
CREATE TABLE IF NOT EXISTS race_races (
    race_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    circuit TEXT NOT NULL,
    city TEXT NOT NULL,
    season INTEGER NOT NULL,
    round INTEGER, -- Helps sort the races in chronological calendar order
    FOREIGN KEY (season) REFERENCES scrape_seasons (year)
);

-- 6. SESSIONS
CREATE TABLE IF NOT EXISTS race_sessions (
    session_id INTEGER PRIMARY KEY AUTOINCREMENT,
    race_id INTEGER NOT NULL,
    session_type TEXT NOT NULL, -- 'FP1', 'FP2', 'FP3', 'Qualifying', 'Sprint', 'Race'
    date TEXT, -- Store as 'YYYY-MM-DD HH:MM:SS'
    FOREIGN KEY (race_id) REFERENCES race_races (race_id) ON DELETE CASCADE
);

-- 7. RESULTS
CREATE TABLE IF NOT EXISTS race_results (
    result_id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL,
    driver_id INTEGER NOT NULL,
    constructor_id INTEGER NOT NULL, -- Captured at the time of the race
    position INTEGER, -- Can be NULL if DNF before classification
    points REAL DEFAULT 0.0, -- REAL handles half-points (e.g., Spa 2021)
    status TEXT, -- 'Finished', 'DNF', 'DSQ', 'DNS', '+1 Lap'
    q1_time TEXT, 
    q2_time TEXT,
    q3_time TEXT,
    FOREIGN KEY (session_id) REFERENCES race_sessions (session_id) ON DELETE CASCADE,
    FOREIGN KEY (driver_id) REFERENCES race_drivers (driver_id),
    FOREIGN KEY (constructor_id) REFERENCES race_constructors (constructor_id)
);