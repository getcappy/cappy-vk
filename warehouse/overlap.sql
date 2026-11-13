WITH audiences AS (
    SELECT BITMAP_UNION(IF(tag_code = 'deep_viewer', members, BITMAP_EMPTY())) AS deep,
           BITMAP_UNION(IF(tag_code = 'bookmarked', members, BITMAP_EMPTY())) AS saved
    FROM ads_vk_user_tag_week WHERE week_no = 1 AND rule_version = 1
)
SELECT BITMAP_COUNT(deep) AS deep_users, BITMAP_COUNT(saved) AS bookmark_users,
       BITMAP_AND_COUNT(deep, saved) AS both_users,
       BITMAP_COUNT(BITMAP_ANDNOT(deep, saved)) AS deep_only,
       BITMAP_COUNT(BITMAP_ANDNOT(saved, deep)) AS bookmark_only FROM audiences
