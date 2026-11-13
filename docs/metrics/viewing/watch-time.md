# 总观看时长

对窗口内各次展示的观看秒数求和，单位为秒。源字段最多记录 255 秒，因此累计值描述的是可观测时长。

```sql
SELECT week_no, SUM(watch_seconds) AS watch_seconds
FROM dws_vk_user_week
GROUP BY week_no
ORDER BY week_no;
```
