# 指标目录

先按业务问题选择主题，再查看指标的观察窗口、统计单位和计算方法。

## 人群与标签

[展示次数](audience/impressions.md)、[触达](audience/reach.md)、活跃（[V2](audience/acticity_V2.md)、[V1](audience/activity.md)）。

[标签人数](audience/tag-size.md)、[人群合并人数](audience/union.md)、[人群重叠人数](audience/overlap.md)、[人群独有人数](audience/exclusive.md)。

[强作者偏好用户占比](audience/strong-creator-affinity-rate.md)衡量观看集中在少数作者身上的用户有多少。

## 观看与内容表现

[获得展示的视频数](viewing/observed-videos.md)、[观看次数](viewing/positive-watches.md)、[有效观看次数](viewing/effective-views.md)、[有效观看人数](viewing/effective-viewers.md)、[深度观看](viewing/deep-viewing.md)。

[总观看时长](viewing/watch-time.md)、[人均观看时长](viewing/watch-time-per-user.md)、[次均观看时长](viewing/watch-time-per-exposure.md)。

[可判定完播展示数](viewing/measurable-exposures.md)、[完播次数](viewing/completions.md)、[内容完播率](viewing/completion-rate.md)。

[周爆款视频（Demo 试用口径）](viewing/weekly-breakout-video.md)用于统计达到观看和互动门槛的作品、产出爆款的作者，以及作者当周有展示作品的爆款率。

## 互动反馈

| 行为 | 发生次数 | 参与人数 |
| --- | --- | --- |
| 点赞 | [次数](feedback/like-count.md) | [人数](feedback/like-users.md) |
| 点踩 | [次数](feedback/dislike-count.md) | [人数](feedback/dislike-users.md) |
| 分享 | [次数](feedback/share-count.md) | [人数](feedback/share-users.md) |
| 收藏 | [次数](feedback/bookmark-count.md) | [人数](feedback/bookmark-users.md) |
| 打开作者主页 | [次数](feedback/author-click-count.md) | [人数](feedback/author-click-users.md) |
| 打开评论区 | [次数](feedback/comment-open-count.md) | [人数](feedback/comment-open-users.md) |

[内容收藏率](feedback/bookmark-rate.md)用于比较视频、作者或时长段的收藏表现。

## 回访与留存

[回访人数](retention/returning-users.md)、[连续留存人数](retention/continuous-users.md)、[周留存率](retention/retention-rate.md)、[沉默核心用户有效回流率](retention/dormant-core-user-reactivation-rate.md)。

## 有序漏斗

[有序漏斗各步人数](funnels/step-users.md)、[相邻步骤转化率](funnels/step-conversion-rate.md)、[漏斗整体转化率](funnels/overall-conversion-rate.md)。

## 趋势与相关性

[有效观看率与次周收藏分享率的变化相关性](trends/viewing-feedback-lag-correlation.md)衡量同一用户先后两段变化的关联。

## 活动指标

[三周收藏活动](../campaigns/three-week-bookmark.md)按历史日志回溯圈选和后续表现。

[活动有效观看次数](campaigns/effective-views.md)、[三周收藏活动原名单人数](campaigns/standard-audience.md)、[三周收藏活动放宽名单人数](campaigns/expanded-audience.md)、[三周收藏活动净新增人数](campaigns/incremental-audience.md)。

[活动后续收藏人数](campaigns/converted-users.md)、[活动后续收藏率](campaigns/conversion-rate.md)用于比较各份名单的后续收藏表现。

## 维护方式

新增指标时，在所属主题下建一个英文命名的 Markdown 文件，并在本页加入链接。文件里写明适用场景、观察窗口、统计单位和计算方法。人数要交代如何去重，比率要写清分子和分母。活动临时调整口径时，在活动指标中引用常规定义并说明改动，周报继续引用常规定义。
