DROP TABLE IF EXISTS readings;

CREATE TABLE readings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_reading_id INT NOT NULL,
    city TEXT NOT NULL,
    reading_time DATETIME,
    pm2_5 REAL,
    is_missing INT NOT NULL DEFAULT 0,
    is_outlier INT NOT NULL DEFAULT 0,
    source TEXT NOT NULL
);

