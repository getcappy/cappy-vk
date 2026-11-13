# 展示平台

平台描述一次视频展示使用的端。同一人可以跨端，本字典不把平台作为用户的固定属性。以下名称是 Cappy Demo 自定的业务约定，适用于 W0、W1、W2。VK 团队举过 Android、iOS、Web 和 Smart TV 的例子，公开材料没有给出它们的编号。[VK 团队字段说明](https://habr.com/ru/companies/vk/articles/970350/) · [VK-LSVD 匿名化说明](https://arxiv.org/html/2602.04567#S3.SS1)

| DWD `platform_code`（ODS `platform`） | Demo 平台名称 | 查询时常用的说法 |
| --- | --- | --- |
| 0 | Android 端 | 安卓、Android App |
| 1 | iOS 端 | iOS、iOS App |
| 4 | Web 端 | 网页端、Web |
| 10 | TV 端 | 电视端、Smart TV、大屏电视 |

其余非空值显示为“其他平台（编码 N）”，保留原编号以便下钻。“其他平台”合计包含所有未单独命名的非空编码。`NULL` 单列为“平台未知”。本项目将“移动 App 端”定义为 `platform_code IN (0, 1)`。Web 端可能来自不同设备，数据没有区分电脑浏览器和手机浏览器的已确认映射。

使用 `dwd_vk_video_exposure.platform_code` 筛选展示。`agent_code` 是客户端或浏览器的另一套匿名编码。“在 Android 端从搜索入口触达”要求平台和[入口](place.md)两个条件落在同一次展示，然后按用户去重。“同时用过 Android 和 iOS”则要求同一用户在窗口内的不同展示中用过这两个端。

按平台输出有业务名称的结果时，在标题或注释标明“按 Demo 映射”。用户明确询问 VK 真实编号含义时，说明官方发布的匿名化范围。
