# 点赞次数

统计指定窗口内 `liked` 为真的展示记录数，单位为次。周汇总取 `likes` 的总和。

```sql
SELECT week_no, SUM(likes) AS event_count
FROM dws_vk_user_week
GROUP BY week_no
ORDER BY week_no;
```
