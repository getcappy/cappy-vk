# 可判定完播展示数

展示关联的视频时长在 1 至 254 秒（含边界）时，进入完播率分母。视频时长缺失、为零或超出该范围时，从完播统计中排除。

```sql
SELECT week_no, SUM(measurable_completions) AS measurable_exposures
FROM dws_vk_user_week
GROUP BY week_no
ORDER BY week_no;
```
