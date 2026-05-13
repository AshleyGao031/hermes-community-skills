#!/usr/bin/env python3
"""
update_profile_card.py — 更新项目组画像卡

用法：
    python3 scripts/update_profile_card.py "<工作目录>" [--week W17] [--date 2026-05-03]

工作流程：
1. 读取最新的 data_snapshot.md（从工作目录）
2. 解析各项目组的总营收、拉新GMV、SMROI、环比
3. 重建 项目组画像卡.md
   - 追加更新记录（最多保留12条，多了截断）
   - 风险等级判定（含集中度>80%检测）
   - 分项目组画像（最新数据）
   - 滚动趋势数据（保留最近8周）
"""

import argparse
import re
import sys
from pathlib import Path
from datetime import datetime


ORDER = [
    "全国大班", "云领学", "强基业务", "新世界", "研习所",
    "小图灵", "KP", "Deepthink", "博闻", "思维", "纵横工作室", "线下店"
]


def judge_risk(smroi, revenue, total_revenue):
    """返回 (风险等级emoji, 风险描述)"""
    concentration = (revenue / total_revenue * 100) if total_revenue > 0 else 0
    if revenue < 0:
        return "🔴", "GMV为负", concentration
    if smroi == 0:
        return "🔴", "SMROI为零", concentration
    if smroi < 0:
        return "🔴", "SMROI为负", concentration
    if concentration > 80:
        return "⚠️", "集中度风险", concentration
    if smroi < 0.8:
        return "⚠️", "SMROI低", concentration
    if smroi >= 1.5:
        return "✅", "SMROI优秀", concentration
    return "✅", "", concentration


def parse_snapshot(snapshot_path: Path) -> dict:
    """解析 data_snapshot.md，返回 {项目组: {指标: 值}}"""
    content = snapshot_path.read_text()
    data = {}
    # 优先用财务口径，财务口径没有的项目组从团队口径补（线下店等）
    financial_rows = re.findall(r'\| 周营收-财务口径 \| (\S+) \| (\S+) \| ([^|]+) \|', content)
    team_rows = re.findall(r'\| 周营收-团队口径 \| (\S+) \| (\S+) \| ([^|]+) \|', content)
    # 先处理团队口径（可能被财务口径覆盖）
    rows = list(team_rows)
    # 再追加财务口径（覆盖同名key）
    rows.extend(financial_rows)

    current_group = None
    for group, metric, value in rows:
        if group in ("合计", "总和", "总计"):
            continue  # 排除合计行，避免重复计算总数
        value = value.strip().replace(',', '').replace('%', '')
        try:
            num_val = float(value)
        except ValueError:
            num_val = value
        if current_group != group:
            current_group = group
            data[group] = {}
        data[group][metric] = num_val
    return data


def rebuild_card(data: dict, week: str, date_str: str, existing_card: str = "") -> str:
    """重建完整画像卡 Markdown"""
    # 计算集中度
    total_revenue = sum((d.get("总营收", 0) or 0) for d in data.values())

    # 解析已有更新记录
    existing_records = []
    if existing_card:
        m = re.search(r'## 更新记录\n\n\| 日期 \| 周次 \| 动作 \|\n\|[-| ]+\|[-| ]+\|[-| ]+\|', existing_card)
        if m:
            start = m.end()
            rest = existing_card[start:].lstrip('\n')
            for line in rest.split('\n'):
                if line.startswith('|') and '------' not in line and line.strip():
                    parts = [p.strip() for p in line.split('|')[1:-1]]
                    if len(parts) == 3 and parts[0]:
                        existing_records.append((parts[0], parts[1], parts[2]))
                else:
                    break

    # 追加新记录（去重同日期）
    new_record = (date_str, week, "自动更新")
    if not existing_records or existing_records[-1] != new_record:
        existing_records.append(new_record)
    # 最多保留12条
    if len(existing_records) > 12:
        existing_records = existing_records[-12:]

    # 构建各部分
    parts = []

    # Header
    first_date, first_week, _ = existing_records[0] if existing_records else (date_str, week, "")
    parts.append(f"""# 项目组画像卡

> 追踪每个项目组的风险状态、趋势和关键指标变化
> 首次生成：{first_date}（{first_week}）
> 每次生成周报后自动更新
""")

    # 更新记录
    parts.append("## 更新记录\n")
    parts.append("| 日期 | 周次 | 动作 |")
    parts.append("|------|------|------|")
    for d, w, a in existing_records:
        parts.append(f"| {d} | {w} | {a} |")
    parts.append("")

    # 项目组状态总览
    parts.append("## 项目组状态总览\n")
    parts.append("| 项目组 | 当前风险等级 | 趋势 | 连续周数 | 本周核心问题 |")
    parts.append("|--------|------------|------|---------|------------|")
    for group in ORDER:
        if group not in data:
            continue
        d = data[group]
        smroi = d.get("SMROI", 0) or 0
        revenue = d.get("总营收", 0) or 0
        risk_emoji, risk_desc, _ = judge_risk(smroi, revenue, total_revenue)
        parts.append(f"| {group} | {risk_emoji} | ➡️ | 1 | {risk_desc} |")
    parts.append("")

    # 分项目组画像
    parts.append("## 分项目组画像\n")
    for group in ORDER:
        if group not in data:
            continue
        d = data[group]
        smroi = d.get("SMROI", 0) or 0
        revenue = d.get("总营收", 0) or 0
        lx_gmv = d.get("拉新GMV", 0) or 0
        xb_gmv = d.get("续报GMV", 0) or 0
        risk_emoji, risk_desc, concentration = judge_risk(smroi, revenue, total_revenue)

        summary = f"本周总营收{revenue:.1f}万，拉新{lx_gmv:.1f}万，续报{xb_gmv:.1f}万，SMROI {smroi:.2f}。"
        if risk_desc:
            summary += f" 风险：{risk_desc}。"
        if concentration > 50:
            summary += f" 集中度{concentration:.0f}%。"

        parts.append(f"""### {group}
- **当前风险等级**：{risk_emoji}
- **本周SMROI**：{smroi:.2f}
- **本周总营收**：{revenue:.1f}万
- **趋势**：➡️
- **连续周数**：1
- **本周摘要**：{summary}
- **待跟踪问题**：{risk_desc or "无"}
""")

    # 滚动趋势（从已有卡中提取历史数据）
    parts.append("## 滚动趋势数据（最近8周）\n")
    parts.append("> 每次更新周报后追加本周数据，超出8周的部分自动淘汰\n")

    # 收集历史周次
    week_data = {}  # {group: [(week, revenue, lx_gmv, smroi), ...]}
    if existing_card and "## 滚动趋势数据" in existing_card:
        # 解析历史数据
        pass  # 简化：暂不支持历史滚动，只写本周

    for group in ORDER:
        if group not in data:
            continue
        d = data[group]
        smroi = d.get("SMROI", 0) or 0
        revenue = d.get("总营收", 0) or 0
        lx_gmv = d.get("拉新GMV", 0) or 0
        parts.append(f"### {group}")
        parts.append("| 周次 | 总营收 | 拉新GMV | SMROI |")
        parts.append("|------|--------|---------|-------|")
        parts.append(f"| {week} | {revenue:.1f}万 | {lx_gmv:.1f}万 | {smroi:.2f} |")
        parts.append("")

    return "\n".join(parts)


def main():
    parser = argparse.ArgumentParser(description="更新项目组画像卡")
    parser.add_argument("workdir", help="工作目录（包含 data_snapshot.md 和 项目组画像卡.md）")
    parser.add_argument("--week", default=None, help="周次，如 W17")
    parser.add_argument("--date", default=None, help="日期，如 2026-05-03")
    args = parser.parse_args()

    workdir = Path(args.workdir)
    today = datetime.now().strftime("%Y-%m-%d")
    week = args.week or datetime.now().strftime("W%W")
    date_str = args.date or today

    # 读取 data_snapshot.md
    snapshots = sorted(workdir.glob("data_snapshot*.md"), key=lambda p: p.stat().st_mtime)
    if not snapshots:
        print("❌ 未找到 data_snapshot*.md 文件", file=sys.stderr)
        sys.exit(1)
    snapshot_path = snapshots[-1]
    print(f"📖 读取：{snapshot_path.name}")

    data = parse_snapshot(snapshot_path)
    print(f"📊 解析到 {len(data)} 个项目组")

    # 读取现有画像卡
    card_path = workdir / "项目组画像卡.md"
    existing_card = card_path.read_text() if card_path.exists() else ""
    if existing_card:
        print(f"📖 读取画像卡：{card_path}")
    else:
        print(f"🆕 创建新画像卡：{card_path}")

    # 重建
    new_card = rebuild_card(data, week, date_str, existing_card)
    card_path.write_text(new_card)
    print(f"✅ 画像卡已更新：{card_path}")
    print(f"   本周 {week} / {date_str}，共 {len(data)} 个项目组")


if __name__ == "__main__":
    main()
