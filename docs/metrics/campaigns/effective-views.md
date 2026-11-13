# 活动有效观看次数

当三周活动明确采用“短片看完也算”时，W1 同时接受[常规有效观看](../viewing/effective-views.md)和完整看完时长为 1 至 9 秒的短片。对一次展示取两个条件的并集。比如时长 8 秒、观看 12 秒的短片同时满足两个条件，只计一次。

```sql
SELECT COUNT(*) AS campaign_effective_views
FROM dwd_vk_video_exposure
WHERE week_no = 1
  AND (watch_seconds >= 10 OR (duration_seconds BETWEEN 1 AND 9 AND observed_complete));
```
