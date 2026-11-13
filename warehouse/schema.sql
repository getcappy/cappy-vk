CREATE TABLE IF NOT EXISTS ods_vk_interactions (
    week_no TINYINT NOT NULL COMMENT '入仓时从 week_XX 文件名提取的相对周序号，也是按周分区的键',
    user_id INT NOT NULL COMMENT '匿名用户 ID，跨数据文件保持一致',
    item_id INT NOT NULL COMMENT '匿名短视频 ID，跨数据文件保持一致',
    source_row_no BIGINT NOT NULL COMMENT '入仓时记录的源周文件行号，从 1 开始，按展示时间先后排列',
    `place` SMALLINT NOT NULL COMMENT '展示入口的匿名编码，例如信息流、搜索或群组，共 24 种编码',
    `platform` SMALLINT NOT NULL COMMENT '展示所在平台的匿名编码，例如 Android、Web 或 TV，共 11 种编码',
    `agent` SMALLINT NOT NULL COMMENT '浏览器或应用等客户端的匿名编码，共 29 种编码',
    `timespent` SMALLINT NOT NULL COMMENT '用户在本次展示中观看视频的时长，单位为秒，记录范围为 0 至 255',
    `like` BOOLEAN NOT NULL COMMENT '本次展示中用户是否点赞',
    `dislike` BOOLEAN NOT NULL COMMENT '本次展示中用户是否点踩',
    `share` BOOLEAN NOT NULL COMMENT '本次展示中用户是否分享视频',
    `bookmark` BOOLEAN NOT NULL COMMENT '本次展示中用户是否收藏视频',
    `click_on_author` BOOLEAN NOT NULL COMMENT '本次展示中用户是否打开作者主页',
    `open_comments` BOOLEAN NOT NULL COMMENT '本次展示中用户是否打开评论区'
) DUPLICATE KEY(week_no,user_id,item_id)
COMMENT 'VK-LSVD 原始交互日志，每行表示向一名用户展示一个视频及其观看和反馈'
PARTITION BY LIST(week_no) (
    PARTITION p00 VALUES IN ("0"), PARTITION p01 VALUES IN ("1"), PARTITION p02 VALUES IN ("2")
)
DISTRIBUTED BY HASH(user_id) BUCKETS 16 PROPERTIES ("replication_num" = "1");

CREATE TABLE IF NOT EXISTS ods_vk_items (
    item_id INT NOT NULL COMMENT '匿名短视频 ID，跨数据文件保持一致',
    author_id INT NOT NULL COMMENT '视频所属作者的匿名 ID，跨数据文件保持一致',
    `duration` SMALLINT NOT NULL COMMENT '视频时长，单位为秒',
    `train_interactions_rank` INT NOT NULL COMMENT '按整个训练期的交互次数对视频排序，用于抽样，排名数值越小表示交互越多'
) DUPLICATE KEY(item_id)
COMMENT 'VK-LSVD 原始视频元数据快照，每行一个视频'
DISTRIBUTED BY HASH(item_id) BUCKETS 16 PROPERTIES ("replication_num" = "1");

CREATE TABLE IF NOT EXISTS ods_vk_users (
    user_id INT NOT NULL COMMENT '匿名用户 ID，跨数据文件保持一致',
    `age` SMALLINT NOT NULL COMMENT '用户年龄，单位为岁，数据卡给出的范围为 18 至 70 岁',
    `gender` SMALLINT NOT NULL COMMENT '用户性别编码',
    `geo` SMALLINT NOT NULL COMMENT '用户最常出现的地理位置的匿名编码，数据集共有 80 种位置编码',
    `train_interactions_rank` INT NOT NULL COMMENT '按整个训练期的交互次数对用户排序，用于抽样，排名数值越小表示交互越多'
) DUPLICATE KEY(user_id)
COMMENT 'VK-LSVD 原始用户元数据快照，每行一名用户'
DISTRIBUTED BY HASH(user_id) BUCKETS 16 PROPERTIES ("replication_num" = "1");

CREATE VIEW IF NOT EXISTS dim_vk_user (
    user_id COMMENT '匿名用户 ID，跨数据文件保持一致',
    age_years COMMENT '用户年龄，单位为岁，数据卡给出的范围为 18 至 70 岁',
    gender_code COMMENT '用户性别编码',
    geo_code COMMENT '用户最常出现的地理位置的匿名编码，数据集共有 80 种位置编码',
    training_activity_rank COMMENT '按整个训练期的交互次数对用户排序，用于抽样，排名数值越小表示交互越多'
)
COMMENT '用户维度，来自 VK-LSVD 用户快照，每行一名用户'
AS
SELECT user_id, age AS age_years, gender AS gender_code, geo AS geo_code,
       train_interactions_rank AS training_activity_rank
FROM ods_vk_users;

CREATE VIEW IF NOT EXISTS dim_vk_video (
    item_id COMMENT '匿名短视频 ID，跨数据文件保持一致',
    author_id COMMENT '视频所属作者的匿名 ID，跨数据文件保持一致',
    duration_seconds COMMENT '视频时长，单位为秒',
    training_popularity_rank COMMENT '按整个训练期的交互次数对视频排序，用于抽样，排名数值越小表示交互越多'
)
COMMENT '视频维度，来自 VK-LSVD 视频快照，每行一个视频'
AS
SELECT item_id, author_id, duration AS duration_seconds,
       train_interactions_rank AS training_popularity_rank
FROM ods_vk_items;

CREATE TABLE IF NOT EXISTS dwd_vk_video_exposure (
    week_no TINYINT NOT NULL COMMENT '入仓时从 week_XX 文件名提取的相对周序号，也是按周分区的键',
    user_id INT NOT NULL COMMENT '匿名用户 ID，跨数据文件保持一致',
    item_id INT NOT NULL COMMENT '匿名短视频 ID，跨数据文件保持一致',
    source_row_no BIGINT NOT NULL COMMENT '入仓时记录的源周文件行号，从 1 开始，按展示时间先后排列',
    author_id INT NULL COMMENT '视频所属作者的匿名 ID，跨数据文件保持一致',
    duration_seconds SMALLINT NULL COMMENT '视频时长，单位为秒',
    place_code SMALLINT NOT NULL COMMENT '展示入口的匿名编码，例如信息流、搜索或群组，共 24 种编码',
    platform_code SMALLINT NOT NULL COMMENT '展示所在平台的匿名编码，例如 Android、Web 或 TV，共 11 种编码',
    agent_code SMALLINT NOT NULL COMMENT '浏览器或应用等客户端的匿名编码，共 29 种编码',
    watch_seconds SMALLINT NOT NULL COMMENT '用户在本次展示中观看视频的时长，单位为秒，记录范围为 0 至 255',
    observed_complete BOOLEAN NULL COMMENT '视频时长为 1 至 254 秒时，观看时长达到视频时长为真，未达到为假。视频时长缺失或超出该范围为 NULL',
    liked BOOLEAN NOT NULL COMMENT '本次展示中用户是否点赞',
    disliked BOOLEAN NOT NULL COMMENT '本次展示中用户是否点踩',
    shared BOOLEAN NOT NULL COMMENT '本次展示中用户是否分享视频',
    bookmarked BOOLEAN NOT NULL COMMENT '本次展示中用户是否收藏视频',
    clicked_author BOOLEAN NOT NULL COMMENT '本次展示中用户是否打开作者主页',
    opened_comments BOOLEAN NOT NULL COMMENT '本次展示中用户是否打开评论区'
) DUPLICATE KEY(week_no,user_id,item_id)
COMMENT '视频展示明细，每行一次展示及其反馈，可通过相对周序号和源文件行号追溯'
PARTITION BY LIST(week_no) (
    PARTITION p00 VALUES IN ("0"), PARTITION p01 VALUES IN ("1"), PARTITION p02 VALUES IN ("2")
)
DISTRIBUTED BY HASH(user_id) BUCKETS 16 PROPERTIES ("replication_num"="1");

CREATE TABLE IF NOT EXISTS dws_vk_user_week (
    week_no TINYINT NOT NULL COMMENT '入仓时从 week_XX 文件名提取的相对周序号，也是按周分区的键',
    user_id INT NOT NULL COMMENT '匿名用户 ID，跨数据文件保持一致',
    exposures BIGINT NOT NULL COMMENT '展示次数，每条展示明细计一次',
    positive_watches BIGINT NOT NULL COMMENT '观看时长大于 0 秒的展示次数',
    watch_seconds BIGINT NOT NULL COMMENT '各次展示的观看时长之和，单位为秒',
    watches_10s BIGINT NOT NULL COMMENT '观看时长达到或超过 10 秒的展示次数',
    observed_completions BIGINT NOT NULL COMMENT '视频时长为 1 至 254 秒且观看时长达到或超过视频时长的展示次数',
    measurable_completions BIGINT NOT NULL COMMENT '视频时长为 1 至 254 秒的展示次数，用作可判定完播率的分母',
    likes BIGINT NOT NULL COMMENT '发生点赞的展示次数',
    dislikes BIGINT NOT NULL COMMENT '发生点踩的展示次数',
    shares BIGINT NOT NULL COMMENT '发生分享的展示次数',
    bookmarks BIGINT NOT NULL COMMENT '发生收藏的展示次数',
    author_clicks BIGINT NOT NULL COMMENT '打开作者主页的展示次数',
    comment_opens BIGINT NOT NULL COMMENT '打开评论区的展示次数'
) UNIQUE KEY(week_no,user_id)
COMMENT '用户周行为汇总，每行一名用户在一个相对周内的展示、观看和反馈计数'
PARTITION BY LIST(week_no) (
    PARTITION p00 VALUES IN ("0"), PARTITION p01 VALUES IN ("1"), PARTITION p02 VALUES IN ("2")
)
DISTRIBUTED BY HASH(user_id) BUCKETS 16 PROPERTIES ("replication_num"="1");

CREATE TABLE IF NOT EXISTS dws_vk_video_week (
    week_no TINYINT NOT NULL COMMENT '入仓时从 week_XX 文件名提取的相对周序号，也是按周分区的键',
    item_id INT NOT NULL COMMENT '匿名短视频 ID，跨数据文件保持一致',
    exposures BIGINT NOT NULL COMMENT '展示次数，每条展示明细计一次',
    positive_watches BIGINT NOT NULL COMMENT '观看时长大于 0 秒的展示次数',
    watch_seconds BIGINT NOT NULL COMMENT '各次展示的观看时长之和，单位为秒',
    watches_10s BIGINT NOT NULL COMMENT '观看时长达到或超过 10 秒的展示次数',
    observed_completions BIGINT NOT NULL COMMENT '视频时长为 1 至 254 秒且观看时长达到或超过视频时长的展示次数',
    measurable_completions BIGINT NOT NULL COMMENT '视频时长为 1 至 254 秒的展示次数，用作可判定完播率的分母',
    likes BIGINT NOT NULL COMMENT '发生点赞的展示次数',
    dislikes BIGINT NOT NULL COMMENT '发生点踩的展示次数',
    shares BIGINT NOT NULL COMMENT '发生分享的展示次数',
    bookmarks BIGINT NOT NULL COMMENT '发生收藏的展示次数',
    author_clicks BIGINT NOT NULL COMMENT '打开作者主页的展示次数',
    comment_opens BIGINT NOT NULL COMMENT '打开评论区的展示次数'
) UNIQUE KEY(week_no,item_id)
COMMENT '视频周表现汇总，每行一个视频在一个相对周内的展示、观看和反馈计数'
PARTITION BY LIST(week_no) (
    PARTITION p00 VALUES IN ("0"), PARTITION p01 VALUES IN ("1"), PARTITION p02 VALUES IN ("2")
)
DISTRIBUTED BY HASH(item_id) BUCKETS 16 PROPERTIES ("replication_num"="1");

CREATE TABLE IF NOT EXISTS ads_vk_user_tag_week (
    week_no TINYINT NOT NULL COMMENT '入仓时从 week_XX 文件名提取的相对周序号，也是按周分区的键',
    tag_code VARCHAR(48) NOT NULL COMMENT '用户标签代码',
    rule_version SMALLINT NOT NULL COMMENT '生成此标签时使用的规则版本号',
    members BITMAP BITMAP_UNION NOT NULL COMMENT '本周满足指定标签及版本条件的去重用户 ID 集合，以 Doris Bitmap 存储'
) AGGREGATE KEY(week_no,tag_code,rule_version)
COMMENT '周用户标签集合，每行对应一个相对周、一个标签和一个规则版本'
PARTITION BY LIST(week_no) (
    PARTITION p00 VALUES IN ("0"), PARTITION p01 VALUES IN ("1"), PARTITION p02 VALUES IN ("2")
)
DISTRIBUTED BY HASH(tag_code) BUCKETS 3 PROPERTIES ("replication_num"="1");
