# 触达

“触达人数”指指定观察窗口内至少收到过一次**站内视频展示**的去重用户数。看到多个视频、多次展示都只计一人。这里衡量的是样本内的站内触达，推送送达需要推送日志。

用户周表每个有展示的用户每周恰好一行，可直接按周计数。

```sql
SELECT week_no, COUNT(*) AS reached_users
FROM dws_vk_user_week
GROUP BY week_no
ORDER BY week_no;
```

求多周合计触达时，在整个窗口按 `user_id` 去重。把各周人数相加会重复计算回访用户。需要名单时，使用指定周的 `reached` v1 标签，可先对多周集合取并集再计数。
