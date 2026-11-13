-- W1 触达 → 有效观看 → 同一用户在更晚的一次展示中收藏。
WITH per_user AS (
    SELECT user_id,
           MIN(IF(watch_seconds >= 10, source_row_no, NULL)) AS first_watch,
           MAX(IF(bookmarked, source_row_no, NULL)) AS last_bookmark
    FROM dwd_vk_video_exposure WHERE week_no = 1 GROUP BY user_id
), counts AS (
    SELECT COUNT(*) AS reached,
           COUNT(first_watch) AS watched_at_least_10s,
           SUM(IF(last_bookmark > first_watch, 1, 0)) AS bookmarked_on_later_exposure
    FROM per_user
)
SELECT counts.*,
       ROUND(100.0 * watched_at_least_10s / NULLIF(reached, 0), 4) AS reach_to_watch_pct,
       ROUND(100.0 * bookmarked_on_later_exposure / NULLIF(watched_at_least_10s, 0), 4) AS watch_to_later_bookmark_pct,
       ROUND(100.0 * bookmarked_on_later_exposure / NULLIF(reached, 0), 4) AS reach_to_later_bookmark_pct
FROM counts;
