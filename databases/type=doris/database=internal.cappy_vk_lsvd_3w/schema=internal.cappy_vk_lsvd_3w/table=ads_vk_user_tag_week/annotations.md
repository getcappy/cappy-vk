---
type: manual
comment: These are manual notes you want the agent to keep in mind, safe to edit.
---

一行对应一个 `(week_no, tag_code, rule_version)`，`members` 是用户 ID 的 Bitmap。选择标签时限定周和版本。v1 标签对应以下指标文件。

| 标签编码 | 成员口径 |
| --- | --- |
| `reached` | [触达](../../../../../docs/metrics/audience/reach.md) |
| `bookmarked` | [收藏人数](../../../../../docs/metrics/feedback/bookmark-users.md) |
| `deep_viewer` | [深度观看](../../../../../docs/metrics/viewing/deep-viewing.md) |
| `author_visitor` | [打开作者主页人数](../../../../../docs/metrics/feedback/author-click-users.md) |
| `shared` | [分享人数](../../../../../docs/metrics/feedback/share-users.md) |
| `negative_feedback` | [点踩人数](../../../../../docs/metrics/feedback/dislike-users.md) |

集合计数见[标签人数](../../../../../docs/metrics/audience/tag-size.md)、[合并](../../../../../docs/metrics/audience/union.md)、[重叠](../../../../../docs/metrics/audience/overlap.md)和[独有](../../../../../docs/metrics/audience/exclusive.md)。临时条件超出现有标签和周汇总的粒度时，从展示明细圈选，再与现有集合组合。
