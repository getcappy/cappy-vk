# 次均观看时长

窗口内[总观看秒数](watch-time.md)除以[展示次数](../audience/impressions.md)，单位为秒/次。按入口、作者或视频比较时，分子和分母需来自同一批展示。

```sql
SELECT week_no, SUM(watch_seconds) / NULLIF(SUM(exposures), 0) AS seconds_per_exposure
FROM dws_vk_user_week
GROUP BY week_no
ORDER BY week_no;
```
