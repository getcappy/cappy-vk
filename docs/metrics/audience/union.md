# 人群合并人数

给定两份或多份名单，统计至少出现在一份名单中的去重用户数。同一用户命中多个标签只计一次。下面计算 W1 打开作者主页或分享过视频的用户数。

```sql
SELECT BITMAP_UNION_COUNT(members) AS visitors_or_sharers
FROM ads_vk_user_tag_week
WHERE week_no = 1 AND rule_version = 1
  AND tag_code IN ('author_visitor', 'shared');
```
