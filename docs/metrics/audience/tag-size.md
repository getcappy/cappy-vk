# 标签人数

在指定周、标签和版本下，统计成员集合中的去重用户数。跨周求覆盖人数时先对目标周的集合取并集。下面按原标签版本展示每周人数。

```sql
SELECT week_no, tag_code, rule_version, BITMAP_COUNT(members) AS tag_users
FROM ads_vk_user_tag_week
ORDER BY week_no, tag_code, rule_version;
```
