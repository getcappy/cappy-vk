# 人均观看时长

目标人群的[总观看秒数](watch-time.md)除以这份人群的去重人数，单位为秒/人。下例以当周[触达用户](../audience/reach.md)为人群。如果题目指定预先圈定的名单，要保留名单中当期没有观看的人，其观看时长计零。

```sql
SELECT week_no, SUM(watch_seconds) / NULLIF(COUNT(*), 0) AS seconds_per_reached_user
FROM dws_vk_user_week
GROUP BY week_no
ORDER BY week_no;
```
