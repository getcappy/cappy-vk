INSERT OVERWRITE TABLE {table} PARTITION (p{week:02d}) (
    week_no, {entity}, exposures, positive_watches, watch_seconds, watches_10s,
    observed_completions, measurable_completions, likes, dislikes, shares, bookmarks,
    author_clicks, comment_opens
)
SELECT week_no, {entity}, COUNT(*), SUM(IF(watch_seconds > 0, 1, 0)), SUM(watch_seconds),
       SUM(IF(watch_seconds >= 10, 1, 0)),
       SUM(IF(observed_complete, 1, 0)), COUNT(observed_complete),
       SUM(IF(liked, 1, 0)), SUM(IF(disliked, 1, 0)), SUM(IF(shared, 1, 0)),
       SUM(IF(bookmarked, 1, 0)), SUM(IF(clicked_author, 1, 0)), SUM(IF(opened_comments, 1, 0))
FROM dwd_vk_video_exposure
WHERE week_no = {week}
GROUP BY week_no, {entity}
