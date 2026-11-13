# 观看次数

一次展示记录的观看时长大于 0 秒，计一次观看。单位为次，同一用户的多次观看可以累加。

```sql
SELECT week_no, SUM(positive_watches) AS positive_watches
FROM dws_vk_user_week
GROUP BY week_no
ORDER BY week_no;
```
