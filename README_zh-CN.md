# MySQL 电商用户行为数据分析

[English](README.md) | [中文](README_zh-CN.md)

> 一个以 SQL 为核心的求职作品集：在 **MySQL 8** 中把可复现电商行为数据转化为漏斗、留存、RFM、复购和商品分析结论。

`MySQL 8` · `SQL` · `CTE` · `窗口函数` · `RFM` · `转化漏斗` · `Cohort 留存` · `查询优化` · `Python`

![项目流水线](reports/figures/01_project_pipeline.png)

## 项目概览与业务问题

项目完整覆盖：关联模拟数据、关系建模、约束和索引、批量导入、数据质量门禁、业务 SQL、结果导出、可视化、测试与 CI。Python 只负责生成、编排、导出和制图；核心业务指标全部由 MySQL 计算。

业务目标是统一回答：用户在哪个漏斗步骤流失、哪些渠道和商品创造价值、哪些 Cohort 持续活跃、哪些客户群值得重点运营。所有指标口径集中在 SQL 中，避免重复分析出现冲突。

## 实际验收结果

以下数字全部来自 MySQL 8.0.46 最终实跑：`--users 50000 --seed 42`，日期范围为 2025-01-01 至 2025-12-31。

| 指标 | 结果 |
|---|---:|
| 用户 / 商品 | 50,000 / 1,500 |
| 行为事件 | 1,400,993 |
| 订单 / 明细 / 支付 | 139,705 / 224,865 / 124,505 |
| 成功订单 / 付费用户 | 117,593 / 21,364 |
| 收入 / 客单价 | 46,655,349.36 / 396.75 |
| 退款率 | 4.95% |
| 浏览到支付总体转化 | 43.57% |
| 复购率 | 83.50% |
| 平均第二次购买间隔 | 35.90 天 |
| Cohort 平均 M1 / M2 / M3 | 56.79% / 57.50% / 57.53% |
| 收入最高品类 | Electronics（21,441,390.67） |

复购率较高是因为生成逻辑把订单集中在高价值和常规用户，而总体流量仍包含大量不购买用户。所有结论仅用于展示分析能力，不代表真实企业表现。

## 项目架构

```mermaid
flowchart LR
  A["固定种子关联数据"] --> B["CSV 校验"] --> C["MySQL 8 建库与批量导入"]
  C --> D["质量门禁"] --> E["SQL 业务分析"] --> F["结果 CSV"] --> G["Matplotlib 图片与双语 README"]
  E --> H["VIEW 与 EXPLAIN ANALYZE"]
```

## 数据集与数据库结构

生成器体现渠道/用户类型购买倾向、品类价格与毛利差异、多事件 Session、弃购、取消和退款。内部用户类型只用于生成，最终 RFM 完全由 SQL 重新计算。

![数据库结构](reports/figures/00_database_schema.png)

```mermaid
erDiagram
  users ||--o{ user_events : generates
  users ||--o{ orders : places
  orders ||--|{ order_items : contains
  products ||--o{ order_items : appears_in
  products ||--o{ user_events : viewed_in
  orders ||--o| payments : has
```

金额采用 `DECIMAL(12,2)`，日期使用 `DATE/DATETIME`；主键、外键、唯一、非空和 MySQL 8 `CHECK` 约束见 [`sql/01_create_tables.sql`](sql/01_create_tables.sql)。

## 数据质量

[`sql/03_data_quality.sql`](sql/03_data_quality.sql) 检查主键重复、NULL、孤立外键、注册前事件、非法金额/数量、退款状态冲突和订单金额对账。最终所有检查的异常数均为 **0**。

## 核心 KPI 与转化漏斗

Revenue 只统计 `paid/completed` 订单；GMV、Revenue、Paid Orders、Paying Users、AOV、ARPU、ARPPU、付费率、退款率及日/月/渠道拆分见 [`sql/04_basic_kpis.sql`](sql/04_basic_kpis.sql)。

![月度收入](reports/figures/02_monthly_gmv.png)

漏斗按用户去重：分析期内每位用户在每个阶段最多计数一次，允许合法跳步，避免把重复事件误算成多个用户。

![转化漏斗](reports/figures/03_conversion_funnel.png)

| 阶段 | 用户数 | 单步转化率 |
|---|---:|---:|
| 浏览 | 49,496 | — |
| 加购 | 23,599 | 47.68% |
| 购买 | 21,942 | 92.98% |
| 支付 | 21,567 | 98.29% |

![渠道转化](reports/figures/04_channel_conversion.png)

## 行为路径分析

使用 `LEAD()` 按 Session 构造相邻行为转移，条件聚合分析 Session 深度与支付转化，详见 [`sql/06_user_behavior.sql`](sql/06_user_behavior.sql)。

![行为转移](reports/figures/11_user_behavior_transition.png)

## RFM 用户分层

R/F/M 只基于成功订单；`NTILE(5)` 分位打分，并对 Recency 反向赋分，再映射为业务分层。

![RFM 用户分布](reports/figures/06_rfm_segments.png)
![RFM 收入](reports/figures/07_rfm_revenue.png)

Champions 是收入最高分层：4,222 人、收入 19,984,860.61。完整结果见 [`reports/tables/rfm_segments.csv`](reports/tables/rfm_segments.csv)。

## 留存与复购

月度 Cohort 定义：注册月为 `cohort_month`，事件发生月为 `activity_month`，当月活跃人数除以 Cohort 初始人数。M0 含注册行为，M1+ 衡量回访。复购分析使用 `ROW_NUMBER()` 和 `LAG()` 识别首次/二次购买及间隔。

![Cohort 留存](reports/figures/05_retention_cohort.png)
![复购](reports/figures/08_repeat_purchase.png)

## 商品分析

SQL 计算买家数、销量、收入、基于成本的粗略毛利/毛利率，并用 `DENSE_RANK() OVER(PARTITION BY category ...)` 完成各品类 Top-N。

![品类收入](reports/figures/09_category_revenue.png)
![Top 商品](reports/figures/10_top_products.png)

## 窗口函数

[`sql/10_window_functions.sql`](sql/10_window_functions.sql) 实际使用：`ROW_NUMBER()` 购买次序、`RANK/DENSE_RANK()` 商品排名、`LAG()` 购买间隔、`LEAD()` 下一行为、`SUM() OVER()` 累计/滚动收入、`AVG() OVER()` 移动均值、`NTILE()` RFM 打分。

```sql
SELECT user_id, order_time,
       ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY order_time) AS purchase_number,
       LAG(order_time) OVER (PARTITION BY user_id ORDER BY order_time) AS previous_order
FROM orders
WHERE order_status IN ('paid', 'completed');
```

## 查询优化

复合索引遵循最左前缀原则，匹配“等值用户/状态 + 时间范围”查询。实际 `EXPLAIN` 中两条查询均为 `type=range`，命中 `idx_events_user_time` 与 `idx_orders_user_time`，预计扫描 16 行和 1 行，而非全表扫描。未编造毫秒级耗时。

![查询优化](reports/figures/12_query_optimization.png)

## 目录结构

```text
src/               生成、校验、MySQL 导入、导出、制图、Pipeline
sql/               建表、索引、质量、KPI、漏斗、RFM、留存、视图、EXPLAIN
reports/tables/    可提交的 SQL 查询结果
reports/figures/   180 DPI README 图片
notebooks/         只展示结果的 Notebook
tests/             数据、业务指标、MySQL 集成测试
.github/workflows/ CI
```

## 快速开始与 MySQL/Docker

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
docker compose up -d
python -m src.pipeline --users 5000 --seed 42
pytest -q
```

作品集正式规模：`python -m src.pipeline --users 50000 --seed 42`。Docker 把 MySQL 8 映射到 `3307`；Compose 密码仅为本地 Demo。使用现有服务器时修改 `.env`。连接失败会明确停止，绝不偷偷改用 SQLite。

## 测试、复现与限制

最终本地测试 **6 passed**，其中包含真实 MySQL 8 连接测试（`RUN_MYSQL_TESTS=1`）。固定 seed=42、固定 2025 日期、`pathlib`、集中 SQL 口径保证复现。大型原始 CSV 和 `.env` 不提交。

项目使用模拟数据，渠道效果和因果关系仅为展示；执行耗时依赖硬件和统计信息。未来可增加定时快照和 BI Dashboard，但不把 SQL 核心分析迁移到 pandas。预测型机器学习刻意不在范围内。

## 技术栈与许可证

MySQL 8、SQL、Python 3.10+、pandas、NumPy、PyMySQL、SQLAlchemy、Matplotlib、pytest、Jupyter、Docker、GitHub Actions。采用 [MIT License](LICENSE)。
