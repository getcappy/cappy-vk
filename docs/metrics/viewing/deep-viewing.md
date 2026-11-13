# 深度观看

周报中的“深度观看人数”指同一相对周内，至少有 **3 次**[常规有效观看](effective-views.md)的去重用户数。恰好 3 次即可入选。

先在每个 `(week_no, user_id)` 内累计有效观看次数，再按周统计合格用户。跨周查询时仍逐周判定资格。例如，同一用户 W0 有 2 次、W1 有 1 次，两周都没有达到门槛。

```sql
SELECT week_no, SUM(IF(watches_10s >= 3, 1, 0)) AS deep_viewers
FROM dws_vk_user_week
GROUP BY week_no
ORDER BY week_no;
```

圈选常规名单可取同周 `deep_viewer` 标签的 v1 集合。运营要求“短片看完也算”时，按[活动放宽名单](../campaigns/expanded-audience.md)的口径从展示明细重算。
