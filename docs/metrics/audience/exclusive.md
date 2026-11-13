# 人群独有人数

A 独有人数为属于 A 且不属于 B 的去重人数。方向会影响结果，报告时写出保留哪份名单。下面计算 W1 打开作者主页但没有分享的用户数。

```sql
WITH audiences AS (
    SELECT BITMAP_UNION(IF(tag_code = 'author_visitor', members, BITMAP_EMPTY())) AS a,
           BITMAP_UNION(IF(tag_code = 'shared', members, BITMAP_EMPTY())) AS b
    FROM ads_vk_user_tag_week
    WHERE week_no = 1 AND rule_version = 1 AND tag_code IN ('author_visitor', 'shared')
)
SELECT BITMAP_COUNT(BITMAP_ANDNOT(a, b)) AS author_visitors_only
FROM audiences;
```
