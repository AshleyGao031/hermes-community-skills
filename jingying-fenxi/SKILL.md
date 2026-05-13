---
name: jingying-fenxi
version: 6.6.0
last_updated: 2026-04-09
description: >
  经营周报数据分析与报告生成。
  典型触发："帮我分析本周的经营数据"、"刷新周报"、"分析 W6 的数据"、"经营分析"、"月度分析"。
---

> **适用场景：** 用户提到"经营分析"、"周报"、"刷新周报"、"GMV分析"、"营收分析"、"月度分析"时触发。

# 经营周报分析 Skill

从 GMV 全量数据 Excel 中读取营收、SMROI、进度等多维度指标，生成结构化周报和项目组画像卡。

## 输入要求

用户需提供：
- `GMV全量数据_*_*.xlsx` — 本周数据（必须）
- `GMV全量数据_*_*.xlsx` — 上周数据（环比计算需要，可选）
- 工作目录下的 `分析规则与模板.md`、`项目组画像卡.md`（如有）

## 文件结构

```
jingying-fenxi/
├── SKILL.md                          ← 本文件：入口+流程+防编数+经验总结
├── config.yaml                       ← 阈值参数
├── references/
│   ├── indicators.md                 ← 指标定义+计算公式+精度+🟢🟡🔴+[待BP确认]
│   ├── analysis-rules.md             ← 分析模块规则+风险识别+升降级+画像卡
│   └── data-source-mapping.md        ← 数据源映射（每个指标从哪个Sheet取）
├── templates/
│   ├── weekly-report.md              ← 周报结构+Wording规则
│   ├── monthly-report.md             ← 月度分析六章节框架
│   ├── lct-module.md                 ← LCT课程业务模板
│   └── spot-check.md                 ← 抽检清单模板
├── examples/
│   └── W9-report-format-reference.md ← 格式基准
└── scripts/
    ├── read_excel.py                 ← 读数据+生成data_snapshot
    ├── generate_report.py            ← 模型无关报告生成+模块6 Excel+抽检清单
    ├── validate_report.py            ← 数字校验
    ├── desensitize.py                ← 脱敏（保留备用，流水线不再调用）
    ├── resensitize.py                ← 解敏（保留备用，流水线不再调用）
    ├── name_compat.py                ← 名称兼容层（保留备用）
    └── test_skill.py                 ← 自动化测试
```

---

## 🚨 模型无关性要求（最高优先级）

### 核心原则
**模型无关 = 数字由脚本，分析由模型**

1. **Python只算数字，AI只写分析**
   - Python（read_excel.py + generate_report.py）：提取原始数据、计算环比/同比/占比/排名/风险扫描，输出骨架报告
   - AI（模型）：读取骨架报告，根据数据写分析判断
   - **两者严格分离**：Python不写分析，AI不算数字

2. **骨架报告结构**
   - 所有数字由Python填写，格式模板保持不变
   - 分析部分用 `[待分析]` 占位，由模型填入
   - 模型填入分析时，数字从骨架报告复制，不自行计算

3. **双流程（必须按顺序执行）**
   - Step 1-3：Python读Excel → 生成骨架（含所有数字）
   - Step 4：模型读骨架 → 写分析 → 输出完整报告
   - 任何模型按步骤执行都能得到相同的数字结果

### 防编数铁律
1. **data_snapshot.md 是唯一真相** — 报告中每个数字必须在快照中有出处
2. **找不到就标 `[数据缺失-请补充]`** — 不推算、不编造
3. **不要用百分比反推绝对值** — 环比列是百分比，不能用来计算绝对变动额
4. **不要从记忆中引用上周数据** — 必须从上周Excel重新读取
5. **validate_report.py 必须返回 PASS** — FAIL则报告不可发布

### 自检清单（每个模块生成后执行）
```
□ 本模块所有数字都能在 data_snapshot.md 中找到？
□ 环比变动是用原始值相减计算的？
□ SMROI 数据来源正确？（详见 references/data-source-mapping.md）
□ 没有使用"约""大约""估计"等模糊词修饰数据？
```

---

## 执行流程（5步）

> ⚠️ **禁止跳步！必须按 Step 0→1→2→3→4 顺序执行。**

### Step 0：更新数据（可选 — 有看板时）
```bash
python3 scripts/update_dashboard.py  # 如工作目录下有此脚本则执行
```

### Step 1：加载上下文（必做）
按顺序读取：
1. `examples/W9-report-format-reference.md` — ⚠️ **格式基准，必须首先读取**
2. `references/indicators.md` — 指标定义和标注规则
3. `references/analysis-rules.md` — 分析规则和风险识别
4. `references/data-source-mapping.md` — 数据源映射
5. 工作目录下的 `分析规则与模板.md`（如存在）
6. 工作目录下的 `项目组画像卡.md`（如存在）

### Step 2：读取数据（必做）

> **注意：脚本接受的是工作目录路径，不是Excel文件路径。** 直接读原始Excel（无需脱敏）。

```bash
python3 scripts/read_excel.py "<工作目录>" [--output <data_snapshot.md>]
```
自动生成 `data_snapshot.md`。确认数据完整后继续。

### Step 3：生成报告（必做）
```bash
python3 scripts/generate_report.py <data_snapshot.md> [--output <报告.md>]
```
- 接受 data_snapshot.md 路径（也兼容旧的工作目录路径）
- 周报 → 按 `templates/weekly-report.md` 格式输出
- LCT模块 → 按 `templates/lct-module.md` 格式输出
- **模块6 Excel** → 自动生成 `W{周次}周报分析_{日期}_模块6.xlsx`（Ashley需粘贴到石墨文档，必须单独保存）
- 自动生成抽检清单 `W{周次}周报分析_{日期}_抽检清单.md`

### Step 3.5：更新项目组画像卡（必做）
```bash
python3 scripts/update_profile_card.py "<工作目录>" [--week W17] [--date 2026-05-03]
```
- 读取本周生成的 `data_snapshot.md`，解析各项目组总营收、拉新GMV、SMROI等指标
- 自动更新工作目录下的 `项目组画像卡.md`：
  - 追加本周到更新记录
  - 刷新项目组状态总览（风险等级、趋势、连续周数）
  - 更新分项目组画像（最新数据摘要）
  - 追加滚动趋势数据（保留最近8周，超出自动淘汰）
- **无需Ashley确认**，自动执行
- 如工作目录下尚无画像卡，自动初始化（首次需确认内容格式，后续全自动）

> ⚠️ 当前画像卡仅支持**课程业务**。广告/词典业务需各自建独立画像卡。

### Step 4：写分析（模型层）
骨架报告中标注 `[待分析]` 的位置，由模型读取骨架数据后填入分析。

**工作方式：**
- Python生成骨架（Step 3）→ 模型读取骨架 → 写分析 → 输出完整报告
- 分析写完后，报告中不应残留任何 `[待分析]` 占位符

**分析判断规则（每个位置的分析要点）：**

| 位置 | 分析要点 |
|------|---------|
| 整体趋势 | 判断"量增效增/量增效降/量跌效升/量跌效跌"，结合Q1结算尾款和Q2自然增量说明原因 |
| 拉新Top3"说明"列 | 根据SMROI环比变化判断：>10%→效率提升，<-10%→效率下滑，否则→效率稳定 |
| 素养定性 | 判断市场获客和辅导转化的变化方向，给出定性描述 |
| 积极信号 | 找出本周最值得关注的正面变化（2-3个），结合数字说明 |
| 风险关注 | 找出本周最需要关注的风险点（2-3个），结合数字说明 |
| 下周重点 | 基于数据给出1-2个下周重点观察项 |
| 同比分析 | 区分季节性因素和真实业务变化，不把Q1结算尾款误认为Q2自然增量 |

**分析判断原则：**
- 趋势判断要结合环比+同比+达成率综合看
- 不确定的业务原因标 `[待BP确认]`
- 分析中引用的数字必须从骨架报告中复制，不自行计算

### Step 5：校验（必做）
```bash
python3 scripts/validate_report.py <报告.md> <data_snapshot.md>
```
也兼容旧用法：`python3 scripts/validate_report.py <报告.md> <工作目录>`

---

## Gotchas（踩坑记录）

> 以下都是真实踩过的坑，务必认真阅读。

- ❌ 踩坑1：用环比百分比反推绝对变动额（得到697万）
- ✅ 正确：用原始值相减（正确1228万）
- ❌ 踩坑2：拉新Top3用团队口径SMROI
- ✅ 正确：必须用财务口径SMROI（详见 `references/data-source-mapping.md`）
- ❌ 踩坑3：一口气生成7个模块（后半段容易编数）
- ✅ 正确：分模块生成，逐模块校验
- ❌ 踩坑4：缺字段时继续写"完整"结论
- ✅ 正确：标 `[数据缺失-请补充]`，宁可空着不编
- ❌ 踩坑5：Excel重复列名直接用dict存（4个"环比"列只剩最后一个）
- ✅ 正确：read_excel.py已自动去重（拉新GMV_环比、续报GMV_环比等）
- ❌ 踩坑6：AI模型自己计算GMV合计，编出错误数字
- ✅ 正确：所有数字由脚本预计算，AI只填分析文字。generate_report.py读data_snapshot.md的JSON块而非Excel
- ❌ 踩坑7（v6.1修复）：desensitize.py输出文件名为`desensitized_data.xlsx`，但read_excel.py只认`GMV全量数据_*.xlsx`
- ✅ 正确：read_excel.py已增加对`desensitized_data.xlsx`和`desensitized_GMV全量数据_*.xlsx`的文件名识别
- ❌ 踩坑8（v6.1修复）：脱敏时对金额做等比缩放（×0.7），导致合计行与明细行求和不一致
- ✅ 正确：脱敏仅替换项目组名称和业务线名称，金额保持原值不变，彻底避免缩放精度问题
- ❌ 踩坑9（v6.3.3修复）：模块6 Excel数字写成了字符串类型，千分位number_format不生效
- ✅ 正确：写入Excel时确保数值类型是float/int；对>=100的数字应用`#,##0.0`千分位格式
- ❌ 踩坑10（v6.3.3修复+v6.5.1再修复）：resensitize.py只解敏md报告，不处理模块6 Excel附件，导致产品线名称停留在脱敏代号。v6.3.3加了--auto-xlsx参数，但默认值是False，调用时不传参数就不生效。
- ✅ 正确（v6.5.1）：`auto_xlsx` 参数默认值改为 `True`，不传参数也会自动扫描同目录xlsx解敏
- ❌ 踩坑11（v6.3.3修复）：SMROI行的达成率写的是"-"，且ROI类指标用了百分比公式而非减差
- ✅ 正确：GMV类达成率=实际/预算（百分比）；ROI/SMROI类达成率=实际-预算（数值，如-0.02）
- ❌ 踩坑12（v6.4修复）：模块6 Excel中SMROI达成率列使用`cell_val(val, decimals=1)`，导致1.35和1.37四舍五入成1.4，减差变0.00
- ✅ 正确：SMROI行用`decimals=2`，保留两位小数，达成率-0.02正确显示
- ❌ 踩坑15（v6.5.1修复）：`smroi_row_indices = {4, 5}` 错误，`enumerate(rows_data, 2)` 使 Excel 行号从2开始（GMV=2,拉新=3,续报=4,市场SMROI=5,项目SMROI=6），应为 `{5, 6}` 才能正确匹配SMROI行使用 `decimals=2`
- ✅ 正确（v6.5.1）：改为 `smroi_row_indices = {5, 6}`
- ❌ 踩坑13（v6.4.1修复）：跳过Step 1~3直接让AI生成报告，导致数字不准确
- ✅ 正确：**禁止跳步！** 必须严格按 Step 0→1→2→3→4→5 顺序执行：先读数据快照（Step 2）→再生成报告（Step 3）→最后AI填充分析（Step 4）。Step 1~3是模型无关的确定性步骤，不可省略
- ❌ 踩坑14（v6.5.0修复）：Q1累计同比Sheet中SMROI取值用了`_col_1`（指标名字段如"平均SMROI"），导致报告中Q1累计SMROI列显示文字而非数字
- ✅ 正确：改用`_col_2`（2026年Q1列），可正确获取SMROI数值如"1.33"
- ❌ 踩坑16（v6.6.0发现）：generate_report.py生成的同比亮点表，所有项目组都标记为🟢"稳健增长"，即使同比增长为负（如-87.7%也标🟢）
- ✅ 正确：Step 4模型填充时必须重新检查同比标注——负增长标🔴，正增长标🟢，同时替换千篇一律的"稳健增长"为具体分析

---

## ⚠️⚠️⚠️ 交付物清单（必须全部发给Ashley）⚠️⚠️⚠️

> **执行完成后，以下3个文件必须全部发送给Ashley，缺一不可！**

| # | 文件 | 说明 | 是否发送 |
|---|------|------|----------|
| 1 | `W{周次}周报分析_{日期}.md` | 主报告 | ✅ **必须发送** |
| 2 | `W{周次}周报分析_{日期}_抽检清单.md` | 抽检清单（校验数字用） | ✅ **必须发送** |
| 3 | `W{周次}周报分析_{日期}_模块6.xlsx` | 模块6 LCT Excel（Ashley粘贴到石墨文档用） | ✅ **必须发送** |
| 4 | `data_snapshot.md` | 数据快照（留档备查） | ❌ 不发送 |

**⚠️ 只发了主报告不算完成！抽检清单和模块6 Excel同样必须发送！**

---

## 依赖
- Python 3.8+
- openpyxl（`pip install openpyxl`）
- pandas（部分脚本使用）
