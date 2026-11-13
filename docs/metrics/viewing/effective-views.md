# 有效观看次数

常规周报中，一次展示的观看时长达到或超过 **10 秒**，计一次有效观看。同一用户可贡献多次。三周活动放宽时单独使用[活动有效观看次数](../campaigns/effective-views.md)。

```sql
SELECT week_no, SUM(watches_10s) AS effective_views
FROM dws_vk_user_week
GROUP BY week_no
ORDER BY week_no;
```
