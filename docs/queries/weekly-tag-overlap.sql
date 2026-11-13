-- W1 点击作者主页且发生分享的用户。替换周、标签及规则版本可复用。
WITH audiences AS (
    SELECT
        BITMAP_UNION(IF(tag_code = 'author_visitor', members, BITMAP_EMPTY())) AS visitors,
        BITMAP_UNION(IF(tag_code = 'shared', members, BITMAP_EMPTY())) AS sharers
    FROM ads_vk_user_tag_week
    WHERE week_no = 1 AND rule_version = 1
      AND tag_code IN ('author_visitor', 'shared')
)
SELECT BITMAP_AND_COUNT(visitors, sharers) AS users_in_both
FROM audiences;
