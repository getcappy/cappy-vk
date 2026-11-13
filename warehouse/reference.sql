WITH users AS (
    SELECT user_id,
           MAX(CASE WHEN week_no = 0 THEN 1 ELSE 0 END) AS reached_w0,
           SUM(CASE WHEN week_no IN (0, 1) THEN bookmarks ELSE 0 END) AS prior_bookmarks,
           SUM(CASE WHEN week_no = 1 THEN standard_views ELSE 0 END) AS standard_views,
           SUM(CASE WHEN week_no = 1 THEN expanded_views ELSE 0 END) AS expanded_views,
           SUM(CASE WHEN week_no = 2 THEN bookmarks ELSE 0 END) AS future_bookmarks
    FROM source_week GROUP BY user_id
)
SELECT user_id, standard_views, expanded_views, future_bookmarks
FROM users
WHERE reached_w0 = 1 AND prior_bookmarks = 0 AND expanded_views >= 3
