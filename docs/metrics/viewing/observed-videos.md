# 获得展示的视频数

统计指定窗口内至少有一次展示的不同视频数。视频周表中每行对应该周获得展示的一个视频。计算跨周总数时，按整个窗口的 `item_id` 去重。

```sql
SELECT week_no, COUNT(*) AS observed_videos
FROM dws_vk_video_week
GROUP BY week_no
ORDER BY week_no;
```
