WITH audience AS (
    SELECT BITMAP_UNION(IF(week_no = 0, members, BITMAP_EMPTY())) AS base,
           BITMAP_UNION(IF(week_no = 1, members, BITMAP_EMPTY())) AS w1,
           BITMAP_UNION(IF(week_no = 2, members, BITMAP_EMPTY())) AS w2
    FROM ads_vk_user_tag_week WHERE tag_code = 'reached' AND rule_version = 1
)
SELECT BITMAP_COUNT(base) AS reached_w0,
       BITMAP_AND_COUNT(base, w1) AS returned_w1,
       BITMAP_AND_COUNT(base, w2) AS returned_w2,
       BITMAP_AND_COUNT(BITMAP_AND(base, w1), w2) AS present_all_weeks
FROM audience
