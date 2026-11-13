# Cappy 短视频用户画像 Demo

把这个项目导入 Cappy，可以用自然语言分析短视频的触达、观看、收藏和跨周回访。数据来自 VK-LSVD，数仓使用 Apache Doris。三周样本共有 298,690,419 条展示记录和 7,368,206 名去重用户。

## 开始使用

1. 克隆此仓库，在可访问 Doris 的机器上按[数仓准备指南](warehouse/README.md)下载五个源文件、建表、导入并执行 ETL。
2. 在自己的 Cappy 实例中选择“从 GitHub 导入”，使用此仓库并配置分析模型。在“设置 → 项目 → 环境变量”填入 [config.yaml](config.yaml) 使用的四项连接参数：`VK_DORIS_HOST`、`VK_DORIS_PORT`、`VK_DORIS_USER`、`VK_DORIS_PASSWORD`。分析账号需要能查询 `cappy_vk_lsvd_3w`。
3. 在项目对话中提问，例如“W1 在 Android 端通过搜索结果入口触达了多少人？” 也可以问“以 W2 为回流周，沉默核心用户的有效回流率是多少？”

[指标目录](docs/metrics/README.md)按业务主题组织。入口和平台名称使用本项目的[入口字典](docs/dimensions/place.md)及[平台字典](docs/dimensions/platform.md)。时间和抽样口径见[样本说明](docs/data-scope.md)。

## 数据来源

项目使用 VK 团队公开的 VK-LSVD 训练子集 `up-0.9_ip-0.9` 的 W0、W1、W2 和用户、视频元数据。数据卡标注 Apache-2.0。复现使用的版本、文件路径和 SHA-256 见[源文件清单](warehouse/source.json)。[VK-LSVD 数据卡](https://huggingface.co/datasets/deepvk/VK-LSVD) · [数据集论文](https://arxiv.org/abs/2602.04567)
