-- Query 1: Current breaches — readings above the WHO 24-hour PM2.5 guideline
SELECT
    city,
    reading_time,
    pm2_5,
    is_outlier,
    source
FROM readings
WHERE pm2_5 > 15
ORDER BY pm2_5 DESC;

-- Query 2: Cities where air quality is trending worse (this week vs last week)
SELECT
    city,
    ROUND(AVG(CASE WHEN reading_time >= DATETIME('now', '-7 days') THEN pm2_5 END), 1) AS avg_this_week,
    ROUND(AVG(CASE WHEN reading_time < DATETIME('now', '-7 days')
                   AND reading_time >= DATETIME('now', '-14 days') THEN pm2_5 END), 1) AS avg_last_week
FROM readings
WHERE is_missing = 0
  AND is_outlier = 0
GROUP BY city
HAVING avg_this_week > avg_last_week;

-- Query 3: City ranking by average PM2.5 (worst to best)

SELECT city, ROUND(AVG(pm2_5), 1) AS avg_pm2_5,
    RANK() OVER(ORDER BY AVG(pm2_5) DESC) AS rank_byavg,
    DENSE_RANK() OVER (ORDER BY AVG(pm2_5) DESC) AS denserank_byavg
FROM readings
WHERE is_missing = 0 AND is_outlier = 0
GROUP BY city
ORDER BY avg_pm2_5 DESC;