# 分享次数

统计指定窗口内 `shared` 为真的展示记录数，单位为次。同一展示的反馈只有一个分享标记。周汇总取 `shares` 的总和。

```sql
SELECT week_no, SUM(shares) AS event_count
FROM dws_vk_user_week
GROUP BY week_no
ORDER BY week_no;
```
