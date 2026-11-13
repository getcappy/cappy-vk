# 展示次数

在给定窗口内，每条视频展示计一次，单位为次。同一用户看到多个视频会累计多次。按用户属性或视频属性拆分时选对应粒度的周表。

```sql
SELECT week_no, SUM(exposures) AS impressions
FROM dws_vk_user_week
GROUP BY week_no
ORDER BY week_no;
```
