INSERT OVERWRITE TABLE ads_vk_user_tag_week PARTITION (p{week:02d}) (
    week_no, tag_code, rule_version, members
)
SELECT week_no, 'reached', 1, BITMAP_UNION(IF(exposures > 0, TO_BITMAP(user_id), BITMAP_EMPTY()))
FROM dws_vk_user_week WHERE week_no = {week} GROUP BY week_no
UNION ALL
SELECT week_no, 'bookmarked', 1, BITMAP_UNION(IF(bookmarks > 0, TO_BITMAP(user_id), BITMAP_EMPTY()))
FROM dws_vk_user_week WHERE week_no = {week} GROUP BY week_no
UNION ALL
SELECT week_no, 'deep_viewer', 1, BITMAP_UNION(IF(watches_10s >= 3, TO_BITMAP(user_id), BITMAP_EMPTY()))
FROM dws_vk_user_week WHERE week_no = {week} GROUP BY week_no
UNION ALL
SELECT week_no, 'author_visitor', 1, BITMAP_UNION(IF(author_clicks > 0, TO_BITMAP(user_id), BITMAP_EMPTY()))
FROM dws_vk_user_week WHERE week_no = {week} GROUP BY week_no
UNION ALL
SELECT week_no, 'shared', 1, BITMAP_UNION(IF(shares > 0, TO_BITMAP(user_id), BITMAP_EMPTY()))
FROM dws_vk_user_week WHERE week_no = {week} GROUP BY week_no
UNION ALL
SELECT week_no, 'negative_feedback', 1, BITMAP_UNION(IF(dislikes > 0, TO_BITMAP(user_id), BITMAP_EMPTY()))
FROM dws_vk_user_week WHERE week_no = {week} GROUP BY week_no
