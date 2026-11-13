# 有效观看人数

统计窗口内至少有一次[常规有效观看](effective-views.md)的去重用户数。分周可使用用户周表。跨周合计按用户重新去重。

```sql
SELECT week_no, SUM(IF(watches_10s > 0, 1, 0)) AS effective_viewers
FROM dws_vk_user_week
GROUP BY week_no
ORDER BY week_no;
```
