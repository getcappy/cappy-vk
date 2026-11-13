# 打开作者主页次数

统计指定窗口内 `clicked_author` 为真的展示记录数，单位为次。该动作表示从本次展示进入作者主页。周汇总取 `author_clicks` 的总和。

```sql
SELECT week_no, SUM(author_clicks) AS event_count
FROM dws_vk_user_week
GROUP BY week_no
ORDER BY week_no;
```
