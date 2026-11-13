# 内容完播率

[完播次数](completions.md)除以[可判定完播展示数](measurable-exposures.md)。按时长段或作者汇总时，先分别累加各视频的分子与分母，再计算比率。分母为零时返回 NULL。示例以百分比输出。

```sql
SELECT week_no, 100.0 * SUM(observed_completions) / NULLIF(SUM(measurable_completions), 0) AS completion_pct
FROM dws_vk_user_week
GROUP BY week_no
ORDER BY week_no;
```
