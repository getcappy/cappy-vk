INSERT OVERWRITE TABLE dwd_vk_video_exposure PARTITION (p{week:02d}) (
    week_no, user_id, item_id, source_row_no, author_id, duration_seconds, place_code,
    platform_code, agent_code, watch_seconds, observed_complete, liked, disliked, shared,
    bookmarked, clicked_author, opened_comments
)
SELECT e.week_no, e.user_id, e.item_id, e.source_row_no, v.author_id, v.duration_seconds,
       e.place, e.platform, e.agent, e.timespent,
       CASE WHEN v.duration_seconds BETWEEN 1 AND 254 THEN e.timespent >= v.duration_seconds END,
       e.`like`, e.dislike, e.share, e.bookmark, e.click_on_author, e.open_comments
FROM ods_vk_interactions e
LEFT JOIN dim_vk_video v ON v.item_id = e.item_id
WHERE e.week_no = {week}
