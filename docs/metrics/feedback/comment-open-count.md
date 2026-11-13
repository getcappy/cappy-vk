# 打开评论区次数

统计指定窗口内 `opened_comments` 为真的展示记录数，单位为次。该动作表示打开评论区。发表评论需要评论事件日志。周汇总取 `comment_opens` 的总和。

```sql
SELECT week_no, SUM(comment_opens) AS event_count
FROM dws_vk_user_week
GROUP BY week_no
ORDER BY week_no;
```
