# 准备 VK-LSVD 三周数仓

在运行导数脚本的机器上安装 Python 3.11 或更新版本，准备一个已有可用 BE 的 Apache Doris 集群。此模型使用 Doris 4.1.5、单副本表和三个周分区。五个输入文件共 2.88 GiB，导入阶段还需要临时 Parquet 空间，校验大表时 DuckDB 也会使用内存和临时磁盘。库名固定为 `cappy_vk_lsvd_3w`，使用这个专用 Demo 库；ETL 重跑会覆盖指定周的派生分区。

## 从仓库根目录开始

```sh
python3 -m venv warehouse/.venv
. warehouse/.venv/bin/activate
python -m pip install -r warehouse/requirements.txt
cp warehouse/.env.example warehouse/.env
```

编辑 `warehouse/.env`。SQL 主机和端口指向 Doris FE，`VK_DORIS_BE_URL` 指向导数机器可直接访问的 BE HTTP 地址（通常为 8040）。两者可以在不同主机。导数账号需要建库、建表和视图、导入、覆盖分区和查询的权限。密码包含 shell 特殊字符时请使用适当的 shell 引号。

```sh
set -a
. warehouse/.env
set +a
python warehouse/prepare.py all
```

完整流程会创建数据库、三张 ODS 表和六个派生对象。已有相同来源文件时，可用 `python warehouse/prepare.py all --source /path/to/parquet` 复用；每个文件都要通过[固定版本和哈希清单](source.json)校验。若管理员已经建好同名库且账号只有库内 DDL 权限，可直接运行 `python warehouse/apply_sql.py warehouse/schema.sql` 建表，然后执行下面的导入、ETL 和核验步骤。

## 单独执行与重试

| 阶段 | 从仓库根目录运行 | 过程 |
| --- | --- | --- |
| 下载 | `python warehouse/prepare.py download` | 下载到 `warehouse/data/`。逐文件验证大小和 SHA-256 后替换，重跑会复用已通过校验的文件。 |
| 建库建表 | `python warehouse/prepare.py schema` | 执行[建库 SQL](create-database.sql)和[完整 DDL](schema.sql)。ODS 保留原始字段，DWD 保留周、源行号和用户行为。 |
| 导入 | `python warehouse/prepare.py load` | 通过 BE Stream Load 导入三个周文件和两份维表源文件，检查过滤行数与 ODS 行数。同一文件的加载标签固定。 |
| ETL | `python warehouse/prepare.py etl` | 逐周构建[展示明细](detail.sql)、[用户和视频周汇总](aggregate_week.sql)及[人群 Bitmap](materialize_bitmaps.sql)。如只需重建 W1，运行 `python warehouse/build.py --week 1`。 |
| 核验 | `python warehouse/prepare.py verify` | DuckDB 从原始 Parquet 独立计算，再与 Doris 的周数据、跨周人群、漏斗、内容表现等逐项核对。 |

下载、导入和核验都支持相同的 `--source` 参数。执行过程、实际 SQL、输入快照及 Stream Load 回执按次存放于 `warehouse/runs/`。核验成功后，`warehouse/verified.json` 中三周展示数应分别为 85,386,270、104,792,375、108,511,774，跨周去重触达为 7,368,206 人。

## 在 Cappy 中连接

[根配置](../config.yaml)从 Cappy 运行环境读取相同的四个 SQL 连接变量。上面的 `set -a` 只作用于当前终端及其子进程。Cappy 服务如果运行在另一台机器或容器，请在 Cappy 的“设置 → 项目 → 环境变量”中填入该服务可访问的 FE 地址、端口、查询账号和密码。准备完成后回到[项目首页](../README.md)开始提问。

本目录的脚本、SQL 和指引随 Git 分发，`.cappyignore` 中的 `warehouse/` 让 Cappy 项目文件工具跳过整个目录。原始数据、运行日志、虚拟环境和本地凭据由 `.gitignore` 排除。
