-- 以 W0 的站内触达人群为起点，分别观察 W1、W2 和连续三周。
WITH audience AS (
    SELECT BITMAP_UNION(IF(week_no = 0, members, BITMAP_EMPTY())) AS base,
           BITMAP_UNION(IF(week_no = 1, members, BITMAP_EMPTY())) AS w1,
           BITMAP_UNION(IF(week_no = 2, members, BITMAP_EMPTY())) AS w2
    FROM ads_vk_user_tag_week WHERE tag_code = 'reached' AND rule_version = 1
), counts AS (
    SELECT BITMAP_COUNT(base) AS reached_w0,
           BITMAP_AND_COUNT(base, w1) AS returned_w1,
           BITMAP_AND_COUNT(base, w2) AS returned_w2,
           BITMAP_AND_COUNT(BITMAP_AND(base, w1), w2) AS present_all_weeks
    FROM audience
)
SELECT counts.*,
       ROUND(100.0 * returned_w1 / NULLIF(reached_w0, 0), 4) AS w1_retention_pct,
       ROUND(100.0 * returned_w2 / NULLIF(reached_w0, 0), 4) AS w2_retention_pct,
       ROUND(100.0 * present_all_weeks / NULLIF(reached_w0, 0), 4) AS continuous_retention_pct
FROM counts;
