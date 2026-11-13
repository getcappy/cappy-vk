# 收藏次数

统计指定窗口内 `bookmarked` 为真的展示记录数，单位为次。数据记录展示上的收藏反馈，无法据此判断之后是否取消收藏。周汇总取 `bookmarks` 的总和。

```sql
SELECT week_no, SUM(bookmarks) AS event_count
FROM dws_vk_user_week
GROUP BY week_no
ORDER BY week_no;
```
