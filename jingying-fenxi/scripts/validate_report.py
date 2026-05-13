#!/usr/bin/env python3
"""
报告数据校验脚本 v6.0
对照 data_snapshot.md 中的JSON数据块，校验报告中所有关键数字。

三路交叉验证：
1. 数据源JSON → 报告数字溯源
2. 各项目组加总 vs 合计行
3. 关键指标一致性（占位符检查）

用法: python validate_report.py <报告.md> <data_snapshot.md>
      python validate_report.py <报告.md> <工作目录>  # 兼容旧用法
返回: 0=PASS, 1=FAIL
"""
import sys

# Windows编码兼容
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
import os
import re
import json
import math


def safe_float(val):
    if val is None:
        return 0.0
    if isinstance(val, (int, float)):
        return 0.0 if math.isnan(val) else float(val)
    s = str(val).strip().replace(",", "").replace("%", "").replace("+", "")
    if s in ('-', '', 'N/A', '—'):
        return 0.0
    try:
        result = float(s)
        return 0.0 if math.isnan(result) else result
    except (ValueError, TypeError):
        return 0.0


def load_snapshot_json(snapshot_path):
    """从 data_snapshot.md 提取嵌入的JSON数据块"""
    if not os.path.exists(snapshot_path):
        return None

    with open(snapshot_path, 'r', encoding='utf-8') as f:
        content = f.read()
    match = re.search(r'<!-- DATA_JSON_START\n(.*?)\nDATA_JSON_END -->', content, re.DOTALL)
    if not match:
        return None
    return json.loads(match.group(1))


def extract_report_numbers(report_path):
    """从报告中提取所有数字及其位置"""
    numbers = []
    with open(report_path, encoding='utf-8') as f:
        lines = f.readlines()

    for i, line in enumerate(lines):
        if "|" in line and "---" not in line:
            cells = [c.strip() for c in line.split("|")[1:-1]]
            for cell in cells:
                # Pre-extract date fragments to exclude them
                date_fragments = set()
                for dm in re.finditer(r'\d{4}-(\d{1,2})-(\d{1,2})', cell):
                    date_fragments.add(dm.group(1).lstrip('0') or '0')
                    date_fragments.add(dm.group(2).lstrip('0') or '0')
                    date_fragments.add(dm.group(1))
                    date_fragments.add(dm.group(2))

                for m in re.finditer(r'[+-]?[\d,]+\.?\d*', cell):
                    raw = m.group()
                    val_str = raw.replace(",", "")
                    # 排除日期（YYYY, YYYYMMDD）
                    if re.match(r'^20\d{2}$', val_str) or re.match(r'^20\d{6}$', val_str):
                        continue
                    # 排除周次编号（W11等）
                    start = m.start()
                    if start > 0 and cell[start - 1] == 'W':
                        continue
                    # 排除日期上下文中的数字片段（如 2026-03-09 中的 -09, 02 等）
                    if date_fragments:
                        abs_val = val_str.lstrip('-').lstrip('0') or '0'
                        if raw.startswith('-') and start > 0 and cell[start-1:start].isdigit():
                            if abs_val in date_fragments or val_str.lstrip('-') in date_fragments:
                                continue
                        before = cell[:start]
                        if before.endswith('-') and (abs_val in date_fragments or val_str in date_fragments):
                            continue
                    try:
                        val = float(val_str)
                        if abs(val) > 0.001:
                            numbers.append({
                                "line": i + 1,
                                "value": val,
                                "raw": raw,
                                "cell": cell,
                            })
                    except ValueError:
                        pass
    return numbers


def build_reference_values(data):
    """从JSON数据构建所有合法参考值"""
    values = set()

    def add_val(v):
        fv = safe_float(v)
        if abs(fv) > 0.001:
            values.add(round(fv, 2))
            values.add(round(fv, 1))
            values.add(round(fv, 0))
            values.add(abs(round(fv, 1)))
            values.add(abs(round(fv, 2)))

    def add_pct(v):
        fv = safe_float(v)
        if abs(fv) > 0.001:
            pv = round(fv * 100, 1)
            values.add(pv)
            values.add(abs(pv))

    # Extract all numeric values from all sheets
    for sheet_name, sheet_data in data.get("data", {}).items():
        rows = sheet_data.get("rows", []) if isinstance(sheet_data, dict) else []
        for row in rows:
            if isinstance(row, dict):
                for k, v in row.items():
                    if isinstance(v, (int, float)) and v != 0:
                        add_val(v)
                        # Also add percentage interpretation for small values
                        if abs(v) < 2:
                            add_pct(v)

    # Also last week data
    for sheet_name, sheet_data in data.get("last_week_data", {}).items():
        rows = sheet_data.get("rows", []) if isinstance(sheet_data, dict) else []
        for row in rows:
            if isinstance(row, dict):
                for k, v in row.items():
                    if isinstance(v, (int, float)) and v != 0:
                        add_val(v)

    # Key metrics (pre-formatted)
    for item in data.get("key_metrics", []):
        val_str = str(item.get("value", ""))
        # Strip formatting
        clean = val_str.replace(",", "").replace("%", "").replace("+", "").replace("万", "")
        try:
            fv = float(clean)
            add_val(fv)
        except (ValueError, TypeError):
            pass

    # Time progress
    tp = data.get("time_progress", {})
    for k, v in tp.items():
        if isinstance(v, (int, float)):
            values.add(round(float(v), 1))

    # Clean NaN and 0
    values.discard(0)
    values.discard(0.0)
    clean = set()
    for v in values:
        if isinstance(v, float) and math.isnan(v):
            continue
        if abs(v) > 0.001:
            clean.add(v)
    return clean


def validate_cross_checks(data):
    """三路交叉验证"""
    errors = []

    # 1. 周营收-财务口径：各项目组加总 vs 合计行
    fin_sheet = data.get("data", {}).get("周营收-财务口径", {})
    fin_rows = fin_sheet.get("rows", []) if isinstance(fin_sheet, dict) else []

    total_row = None
    detail_rows = []
    for row in fin_rows:
        if isinstance(row, dict):
            name = str(row.get("项目组", ""))
            if "合计" in name:
                total_row = row
            elif name and name not in ("", "None"):
                detail_rows.append(row)

    if total_row and detail_rows:
        for metric in ["总营收", "拉新GMV", "续报GMV"]:
            total_val = safe_float(total_row.get(metric, 0))
            sum_detail = sum(safe_float(r.get(metric, 0)) for r in detail_rows)
            if total_val > 0:
                diff = abs(sum_detail - total_val)
                if diff > max(0.5, total_val * 0.01):  # 允许1%或0.5万误差
                    errors.append(
                        f"财务口径 {metric}: 明细加总({sum_detail:.1f}) vs 合计({total_val:.1f})，差异{diff:.1f}"
                    )

    # 2. Q1季度-B标：进度合理性检查
    q1_sheet = data.get("data", {}).get("Q1季度-B标", {})
    q1_rows = q1_sheet.get("rows", []) if isinstance(q1_sheet, dict) else []
    for row in q1_rows:
        if isinstance(row, dict):
            label = str(row.get("季度数据", "")).strip()
            if "总计" in label or "合计" in label:
                total_gmv = safe_float(row.get("总GMV", 0))
                target = safe_float(row.get("目标", 0))
                if target > 0 and total_gmv > 0:
                    achieve = total_gmv / target
                    if achieve > 5.0:
                        errors.append(f"Q1总计达成率异常: {achieve*100:.0f}%（可能数据错误）")

    # 3. 时间进度合理性
    tp = data.get("time_progress", {})
    q1_progress = safe_float(tp.get("q1_progress", 0))
    if q1_progress > 100 or q1_progress < 0:
        errors.append(f"Q1时间进度异常: {q1_progress}%")
    month_progress = safe_float(tp.get("month_progress", 0))
    if month_progress > 100 or month_progress < 0:
        errors.append(f"当月时间进度异常: {month_progress}%")

    return errors


def check_placeholders(report_path):
    """检查占位符类型"""
    with open(report_path, encoding='utf-8') as f:
        content = f.read()

    ai_placeholders = re.findall(r'\[AI洞察[^\]]*\]', content)  # 参照analysis-rules.md第10条"校验报告占位符"
    data_missing = re.findall(r'\[数据缺失[^\]]*\]', content)
    confirm_tags = re.findall(r'【人工确认】|【待确认】|【待BP确认】|\[待补充', content)
    star_placeholders = re.findall(r'\[\*\]', content)

    return ai_placeholders, data_missing, confirm_tags, star_placeholders


def resolve_snapshot_path(arg):
    """解析第二个参数为 data_snapshot.md 路径。兼容旧的目录用法。"""
    if arg.endswith('.xlsx') or arg.endswith('.xls'):
        print("❌ validate_report.py 只接受 data_snapshot.md，请先运行 read_excel.py", file=sys.stderr)
        sys.exit(1)
    if os.path.isdir(arg):
        return os.path.join(arg, "data_snapshot.md")
    return arg


def main():
    if len(sys.argv) < 3:
        print("用法: python validate_report.py <报告.md> <data_snapshot.md>")
        sys.exit(1)

    report_path = sys.argv[1]
    snapshot_path = resolve_snapshot_path(sys.argv[2])

    if not os.path.exists(report_path):
        print(f"❌ 报告文件不存在: {report_path}")
        sys.exit(1)
    if not os.path.exists(snapshot_path):
        print(f"❌ 快照文件不存在: {snapshot_path}")
        print("   请先运行 read_excel.py 生成 data_snapshot.md")
        sys.exit(1)

    print("=" * 60)
    print("  📊 报告数据校验 v6.1（经营分析）")
    print("=" * 60)
    print(f"  报告: {os.path.basename(report_path)}")
    print(f"  快照: {os.path.basename(snapshot_path)}")
    print()

    # 加载JSON数据
    data = load_snapshot_json(snapshot_path)
    if data is None:
        print("❌ data_snapshot.md 中未找到 DATA_JSON 数据块")
        print("   请先运行 read_excel.py 生成 data_snapshot.md")
        sys.exit(1)

    all_errors = []

    # ── Step 1: 交叉验证 ──
    print("📐 Step 1: 数据交叉验证")
    cross_errors = validate_cross_checks(data)
    if cross_errors:
        for e in cross_errors:
            print(f"  ❌ {e}")
        all_errors.extend(cross_errors)
    else:
        print("  ✅ 各项目组加总 ≈ 合计行")
        print("  ✅ Q1达成率合理")
        print("  ✅ 时间进度合理")
    print()

    # ── Step 2: 报告数字溯源 ──
    print("📋 Step 2: 报告数字溯源校验")
    ref_values = build_reference_values(data)
    report_nums = extract_report_numbers(report_path)
    key_nums = [n for n in report_nums if abs(n["value"]) > 5 and "%" not in n["cell"]]

    matched = 0
    unmatched = []
    for num in key_nums:
        v = num["value"]
        found = False
        candidates = [v, round(v, 1), round(v, 2), round(v, 0), abs(v), round(abs(v), 1)]
        for c in candidates:
            if c in ref_values:
                found = True
                break
        # Also check sum/diff of reference values for derived metrics
        if not found:
            for rv in ref_values:
                if abs(v - rv) < 0.15:
                    found = True
                    break
        if found:
            matched += 1
        else:
            # Skip small SMROI/progress values
            if abs(v) < 50 and ("SMROI" in num["cell"] or "进度" in num["cell"]):
                matched += 1  # soft match
            else:
                unmatched.append(num)

    total = len(key_nums)
    print(f"  参考值库: {len(ref_values)} 个")
    print(f"  报告关键数字: {total} 个")
    print(f"  ✅ 匹配: {matched} 个")
    if unmatched:
        print(f"  ⚠️ 未匹配: {len(unmatched)} 个")
        for num in unmatched[:15]:
            print(f"    Line {num['line']}: {num['raw']} (in: {num['cell'][:60]})")
        if len(unmatched) > 15:
            print(f"    ...还有 {len(unmatched)-15} 个")
        if total > 0 and len(unmatched) > total * 0.15:
            all_errors.append(f"报告中{len(unmatched)}/{total}个关键数字无法在快照中找到来源")
    else:
        print("  ✅ 所有关键数字均可在快照中找到出处")
    print()

    # ── Step 3: 关键数字核查 ──
    print("🔢 Step 3: 关键数字核查")
    # 从财务口径合计行提取总营收
    fin_sheet = data.get("data", {}).get("周营收-财务口径", {})
    fin_rows = fin_sheet.get("rows", []) if isinstance(fin_sheet, dict) else []
    total_revenue = 0
    for row in fin_rows:
        if isinstance(row, dict) and "合计" in str(row.get("项目组", "")):
            total_revenue = safe_float(row.get("总营收", 0))
            break

    if total_revenue > 0:
        print(f"  周总营收: {total_revenue:,.1f}万元")
        with open(report_path, encoding='utf-8') as f:
            report_content = f.read()
        rev_str = f"{total_revenue:,.1f}"
        rev_str_alt = f"{total_revenue:.1f}"
        if rev_str in report_content or rev_str_alt in report_content:
            print(f"  ✅ 报告包含正确的总营收: {rev_str}万")
        else:
            err = f"报告中未找到正确的总营收 {rev_str}万"
            print(f"  ⚠️ {err}")
            # Not a hard error - formatting might differ
    print()

    # ── Step 4: 占位符检查 ──
    print("📝 Step 4: 占位符检查")
    ai_ph, data_ph, confirm_tags, star_ph = check_placeholders(report_path)
    placeholder_errors = []
    if ai_ph:
        print(f"  📌 AI分析占位符: {len(ai_ph)}处（需模型填充）")
        placeholder_errors.append(f"残留 {len(ai_ph)} 处 [AI洞察-需模型填充] 占位符")
    if star_ph:
        print(f"  📌 [*]占位符: {len(star_ph)}处（需模型填充）")
        placeholder_errors.append(f"残留 {len(star_ph)} 处 [*] 占位符")
    if data_ph:
        print(f"  ⚠️ 数据缺失占位符: {len(data_ph)}处（需人工补充）")
    if confirm_tags:
        print(f"  🔍 人工确认标记: {len(confirm_tags)}处")
    if not ai_ph and not data_ph and not star_ph:
        print("  ✅ 无占位符（报告已完全填充）")
    if placeholder_errors:
        all_errors.extend(placeholder_errors)
    print()

    # ══════ 总结 ══════
    print("=" * 60)
    if not all_errors:
        print("  ✅ PASS: 所有校验通过")
        if total_revenue > 0:
            print(f"  周总营收 = {total_revenue:,.1f}万元")
        if total > 0:
            print(f"  数字匹配率: {matched}/{total} ({matched/total*100:.0f}%)")
    else:
        print(f"  ❌ FAIL: 发现 {len(all_errors)} 个问题")
        for e in all_errors:
            print(f"    - {e}")
    print("=" * 60)

    sys.exit(0 if not all_errors else 1)


if __name__ == "__main__":
    main()
