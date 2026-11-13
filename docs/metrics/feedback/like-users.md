# 点赞人数

统计窗口内至少发生一次[点赞](like-count.md)的去重用户数，单位为人。下例按周计算。跨周合计先筛选 `likes > 0`，再对 `user_id` 去重。

```sql
SELECT week_no, SUM(IF(likes > 0, 1, 0)) AS event_users
FROM dws_vk_user_week
GROUP BY week_no
ORDER BY week_no;
```
