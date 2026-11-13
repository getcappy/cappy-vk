# 完播次数

在[可判定完播展示](measurable-exposures.md)中，观看时长达到或超过该视频时长，计一次完播。单位为展示次数。

```sql
SELECT week_no, SUM(observed_completions) AS completions
FROM dws_vk_user_week
GROUP BY week_no
ORDER BY week_no;
```
