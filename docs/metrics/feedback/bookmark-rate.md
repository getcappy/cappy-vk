# 内容收藏率

内容报表以展示为单位。[收藏次数](bookmark-count.md)除以同一内容范围的[展示次数](../audience/impressions.md)。按作者、视频或时长段汇总时先加总分子和分母。运营问“名单中多少人后来收藏”时，使用[活动后续收藏率](../campaigns/conversion-rate.md)。示例以百分比输出。

```sql
SELECT week_no, 100.0 * SUM(bookmarks) / NULLIF(SUM(exposures), 0) AS bookmark_pct
FROM dws_vk_user_week
GROUP BY week_no
ORDER BY week_no;
```
