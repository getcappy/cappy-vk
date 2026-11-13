WITH per_user AS (
    SELECT user_id,
           MIN(IF(watch_seconds >= 10, source_row_no, NULL)) AS first_watch,
           MAX(IF(bookmarked, source_row_no, NULL)) AS last_bookmark
    FROM dwd_vk_video_exposure WHERE week_no = 1 GROUP BY user_id
)
SELECT COUNT(*) AS reached,
       COUNT(first_watch) AS watched_at_least_10s,
       SUM(IF(last_bookmark > first_watch, 1, 0)) AS bookmarked_on_later_exposure
FROM per_user
