WITH qualifying_users AS (
    SELECT user_id FROM dwd_vk_video_exposure
    WHERE week_no = 1 AND (watch_seconds >= 10 OR (duration_seconds BETWEEN 1 AND 9 AND observed_complete))
    GROUP BY user_id HAVING COUNT(*) >= 3
), temporary_rule AS (
    SELECT BITMAP_UNION(TO_BITMAP(user_id)) AS members FROM qualifying_users
), eligibility AS (
    SELECT BITMAP_ANDNOT(
               BITMAP_UNION(IF(week_no = 0 AND tag_code = 'reached', members, BITMAP_EMPTY())),
               BITMAP_UNION(IF(week_no IN (0, 1) AND tag_code = 'bookmarked', members, BITMAP_EMPTY()))
           ) AS eligible,
           BITMAP_UNION(IF(week_no = 1 AND tag_code = 'deep_viewer', members, BITMAP_EMPTY())) AS standard,
           BITMAP_UNION(IF(week_no = 2 AND tag_code = 'bookmarked', members, BITMAP_EMPTY())) AS outcome
    FROM ads_vk_user_tag_week WHERE rule_version = 1
), cohorts AS (
    SELECT BITMAP_AND(e.eligible, e.standard) AS standard,
           BITMAP_AND(e.eligible, t.members) AS expanded,
           BITMAP_AND(e.eligible, BITMAP_ANDNOT(t.members, e.standard)) AS added, e.outcome
    FROM eligibility e CROSS JOIN temporary_rule t
), counts AS (
    SELECT BITMAP_COUNT(standard) AS standard_users, BITMAP_AND_COUNT(standard, outcome) AS standard_converted,
           BITMAP_COUNT(expanded) AS expanded_users, BITMAP_AND_COUNT(expanded, outcome) AS expanded_converted,
           BITMAP_COUNT(added) AS added_users, BITMAP_AND_COUNT(added, outcome) AS added_converted
    FROM cohorts
)
SELECT counts.*,
       ROUND(100.0 * standard_converted / NULLIF(standard_users, 0), 4) AS standard_bookmark_pct,
       ROUND(100.0 * expanded_converted / NULLIF(expanded_users, 0), 4) AS expanded_bookmark_pct,
       ROUND(100.0 * added_converted / NULLIF(added_users, 0), 4) AS added_bookmark_pct
FROM counts
