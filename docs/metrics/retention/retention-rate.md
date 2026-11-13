# 周留存率

在起始周触达的人群中，计算目标周的[回访人数](returning-users.md)占起始周[触达人数](../audience/reach.md)的比例。起始分母固定，包含之后没有回来的用户。起始人群为空时返回 NULL。业务指定连续留存时，分子改用[连续留存人数](continuous-users.md)。

[W0 起始人群的周留存示例](../../queries/weekly-retention.sql)分别给出次周留存率、隔周留存率和连续三周留存率，单位为百分比。
