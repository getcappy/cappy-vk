# 点踩次数

统计指定窗口内 `disliked` 为真的展示记录数，单位为次。v1 标签 `negative_feedback` 对应发生过点踩的用户。周汇总取 `dislikes` 的总和。

```sql
SELECT week_no, SUM(dislikes) AS event_count
FROM dws_vk_user_week
GROUP BY week_no
ORDER BY week_no;
```
