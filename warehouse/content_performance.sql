WITH classified AS (
    SELECT CASE WHEN v.duration_seconds BETWEEN 1 AND 9 THEN '01-09'
                WHEN v.duration_seconds BETWEEN 10 AND 29 THEN '10-29'
                WHEN v.duration_seconds BETWEEN 30 AND 59 THEN '30-59'
                WHEN v.duration_seconds BETWEEN 60 AND 254 THEN '60-254'
                ELSE 'outside_measurement' END AS duration_band,
           w.exposures, w.observed_completions, w.measurable_completions, w.bookmarks
    FROM dws_vk_video_week w JOIN dim_vk_video v ON w.item_id = v.item_id
    WHERE w.week_no = 1
)
SELECT duration_band, SUM(exposures) AS exposures, SUM(observed_completions) AS completions,
       SUM(measurable_completions) AS measurable, SUM(bookmarks) AS bookmarks,
       ROUND(100.0 * SUM(observed_completions) / NULLIF(SUM(measurable_completions), 0), 4) AS completion_pct,
       ROUND(100.0 * SUM(bookmarks) / NULLIF(SUM(exposures), 0), 4) AS bookmark_pct
FROM classified GROUP BY duration_band ORDER BY duration_band
