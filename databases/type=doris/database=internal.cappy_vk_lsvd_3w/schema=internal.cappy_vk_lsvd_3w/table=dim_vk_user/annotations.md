---
type: manual
comment: These are manual notes you want the agent to keep in mind, safe to edit.
---

按年龄或地域拆分人群时，先按观察窗口圈出实际用户，再按 `user_id` 关联本表。全量发布快照也包含窗口内无展示的人。

`training_activity_rank` 的排序使用整个训练期。分析过去某一周时，直接用它作当时的预测特征会引入该周之后的信息。
