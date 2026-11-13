# 点踩人数

统计窗口内至少发生一次[点踩](dislike-count.md)的去重用户数，单位为人。下例按周计算。跨周合计先筛选 `dislikes > 0`，再对 `user_id` 去重。

```sql
SELECT week_no, SUM(IF(dislikes > 0, 1, 0)) AS event_users
FROM dws_vk_user_week
GROUP BY week_no
ORDER BY week_no;
```
