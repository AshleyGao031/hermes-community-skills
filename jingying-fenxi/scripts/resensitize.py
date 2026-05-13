#!/usr/bin/env python3
"""
解敏脚本：读取脱敏报告.md (+ xlsx) + mapping.json，输出真实报告.md (+ xlsx)

用法：
    # 解敏md报告
    python scripts/resensitize.py <脱敏报告.md> <mapping.json>

    # 解敏md报告并指定xlsx文件
    python scripts/resensitize.py <脱敏报告.md> <mapping.json> --xlsx <模块6.xlsx>

    # 自动扫描同目录xlsx并解敏
    python scripts/resensitize.py <脱敏报告.md> <mapping.json> --auto-xlsx

功能：
    - 项目组名还原（项目组A→全国大班）
    - 业务线名还原（业务线A→升学）
    - 金额无需还原（脱敏不改数字）
    - 格式保持不变
    - Bug 2 Fix: 同时解敏xlsx文件中的脱敏代号
"""

import argparse
import json
import os
import sys
import glob


def resensitize_report(report_path, mapping_path, output_path=None, xlsx_path=None, auto_xlsx=True):
    """
    解敏报告文件（仅还原名称）
    """
    if not os.path.exists(report_path):
        print(f"❌ 报告文件不存在: {report_path}", file=sys.stderr)
        sys.exit(1)

    if not os.path.exists(mapping_path):
        print(f"❌ mapping.json 不存在: {mapping_path}", file=sys.stderr)
        sys.exit(1)

    with open(mapping_path, "r", encoding="utf-8") as f:
        mapping_data = json.load(f)

    name_mapping = mapping_data.get("name_mapping", {})

    # Build reverse mapping: desensitized_name -> original_name
    reverse_mapping = {v: k for k, v in name_mapping.items()}

    # ========== 解敏 .md 文件（跳过 .xlsx 文件） ==========
    if report_path.lower().endswith('.xlsx') or report_path.lower().endswith('.xls'):
        print(f"  ℹ️ 第一个参数是xlsx，跳过md解敏（用 --xlsx 参数指定xlsx文件）", file=sys.stderr)
        names_restored = 0
        output_path = output_path  # keep user-specified if given
    else:
        with open(report_path, "r", encoding="utf-8") as f:
            content = f.read()

        result = content
        names_restored = 0

        # 按长度降序排列，避免部分匹配（如"项目组A"不应先匹配到"项目组"）
        sorted_items = sorted(reverse_mapping.items(), key=lambda x: -len(x[0]))
        for desensitized_name, original_name in sorted_items:
            count = result.count(desensitized_name)
            if count > 0:
                result = result.replace(desensitized_name, original_name)
                names_restored += count

        if output_path is None:
            base, ext = os.path.splitext(report_path)
            output_path = f"{base}_真实{ext}"

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(result)

    print(f"✅ 解敏完成")
    print(f"  📄 输出: {output_path}")
    print(f"  🏷️  md名称还原: {names_restored} 处")
    print(f"  💰 金额: 无需还原（脱敏未改数字）")

    # ========== 解敏 .xlsx 文件 (Bug 2 Fix) ==========
    xlsx_files = []
    if xlsx_path:
        xlsx_files = [xlsx_path]
    elif auto_xlsx:
        # 自动扫描同目录下的xlsx文件（排除原始Excel数据文件）
        report_dir = os.path.dirname(os.path.abspath(report_path))
        all_xlsx = glob.glob(os.path.join(report_dir, "*.xlsx"))
        for xf in all_xlsx:
            basename = os.path.basename(xf)
            # 跳过原始GMV数据文件，只处理模块6等分析结果xlsx
            if "模块6" in basename or "模块六" in basename or "抽检清单" in basename:
                xlsx_files.append(xf)
            elif not basename.startswith("GMV全量数据"):
                xlsx_files.append(xf)

    for xlsx_file in xlsx_files:
        resensitize_xlsx(xlsx_file, reverse_mapping)

    return output_path


def resensitize_xlsx(xlsx_path, reverse_mapping):
    """
    Bug 2 Fix: 解敏xlsx文件中的脱敏代号
    用mapping.json的reverse mapping替换所有字符串单元格中的脱敏代号
    """
    import openpyxl

    if not os.path.exists(xlsx_path):
        print(f"  ⚠️ xlsx文件不存在，跳过: {xlsx_path}", file=sys.stderr)
        return

    try:
        wb = openpyxl.load_workbook(xlsx_path)
    except Exception as e:
        print(f"  ⚠️ 无法打开xlsx文件，跳过: {xlsx_path} ({e})", file=sys.stderr)
        return

    total_replaced = 0
    # 按长度降序排列，避免部分匹配
    sorted_items = sorted(reverse_mapping.items(), key=lambda x: -len(x[0]))

    for ws in wb.worksheets:
        for row in ws.iter_rows():
            for cell in row:
                if cell.data_type == 's' and cell.value is not None:
                    original = str(cell.value)
                    modified = original
                    for desensitized_name, original_name in sorted_items:
                        if desensitized_name in modified:
                            modified = modified.replace(desensitized_name, original_name)
                    if modified != original:
                        cell.value = modified
                        total_replaced += 1

    # 保存到原文件（覆盖）
    wb.save(xlsx_path)
    wb.close()

    print(f"  ✅ xlsx解敏完成: {os.path.basename(xlsx_path)}")
    print(f"     单元格还原: {total_replaced} 处")


def main():
    parser = argparse.ArgumentParser(description="解敏经营周报报告（支持.md和.xlsx）")
    parser.add_argument("report", help="脱敏报告.md 文件路径")
    parser.add_argument("mapping", help="mapping.json 文件路径")
    parser.add_argument("--output", default=None, help="输出.md路径 (默认: 原名_真实.md)")
    parser.add_argument("--xlsx", default=None, help="指定要解敏的xlsx文件路径")
    parser.add_argument("--auto-xlsx", action="store_true",
                        help="自动扫描同目录下的xlsx文件一并解敏（默认: 否）")
    args = parser.parse_args()

    resensitize_report(
        args.report,
        args.mapping,
        output_path=args.output,
        xlsx_path=args.xlsx,
        auto_xlsx=args.auto_xlsx
    )


if __name__ == "__main__":
    main()
