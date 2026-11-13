# 连续留存人数

把起始周至目标周之间**每一周**的[触达名单](../audience/reach.md)取交集，结果按用户去重。W0 和 W2 有展示、W1 缺席的用户计入 W2 [回访人数](returning-users.md)，连续三周的名单会排除这名用户。

[W0 起始人群的周留存示例](../../queries/weekly-retention.sql)中的 `present_all_weeks` 为 W0、W1、W2 均有展示的人数。
