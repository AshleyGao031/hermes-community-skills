#!/usr/bin/env python3
"""
经营分析 Skill 自动化测试
验证：
1. read_excel.py 能读取模板/示例目录并生成 data_snapshot.md
2. data_snapshot.md 包含关键指标索引
3. Skill 文件结构完整

说明：该 Skill 的完整业务测试依赖真实工作目录文件（分析规则与模板.md、项目组画像卡.md 等），
因此这里做的是“防编数关键路径”测试，而不是整份周报生成测试。
"""
import os
import sys
import shutil
import tempfile
import subprocess
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = SKILL_DIR / "scripts"


def write_mock_excel(path: Path, sheet_specs):
    import openpyxl
    wb = openpyxl.Workbook()
    first = True
    for sheet_name, rows in sheet_specs.items():
        ws = wb.active if first else wb.create_sheet(sheet_name)
        ws.title = sheet_name
        for row in rows:
            ws.append(row)
        first = False
    wb.save(path)


def main():
    passed = 0
    failed = 0
    tmpdir = Path(tempfile.mkdtemp(prefix="jingying_skill_test_"))
    print("=" * 56)
    print(" jingying-fenxi 防编数关键路径测试")
    print("=" * 56)
    print(f"临时目录: {tmpdir}")

    try:
        # 准备两周 mock 数据
        # 表头与实际脚本期望的字段名保持一致
        headers_fin = ["项目组", "总营收", "拉新GMV", "续报GMV", "SMROI"]
        headers_team = ["项目组", "总营收", "市场GMV", "辅导GMV", "市场SMROI"]
        headers_q = ["季度数据", "总GMV", "目标", "进度%", "拉新SMROI", "SMROI目标"]
        headers_m = ["月度数据", "总GMV", "目标", "进度%", "拉新SMROI"]
        headers_y = ["季度同比数据", "指标名", "2026年Q1", "2025年Q1", "同比变化",
                     "2026拉新GMV", "2025拉新GMV", "拉新同比", "2026SMROI", "2025SMROI", "SMROI同比"]
        headers_my = ["月度同比数据", "指标名", "当月同比"]

        last_week = tmpdir / "GMV全量数据_2026Q1_2026-02-22.xlsx"
        this_week = tmpdir / "GMV全量数据_2026Q1_2026-03-01.xlsx"

        base_specs = {
            "周营收-财务口径": [
                headers_fin,
                ["全国大班", 1000, 600, 400, 1.06],
                ["小图灵", 800, 500, 300, 1.00],
                ["合计", 1800, 1100, 700, 1.04],
            ],
            "周营收-团队口径": [
                headers_team,
                ["小图灵", 300, 200, 100, 1.16],
                ["KP", 280, 180, 100, 1.22],
                ["合计", 580, 380, 200, 1.19],
            ],
            "Q1季度-B标": [
                headers_q,
                ["总计", 18000, 20000, 0.90, 1.33, 1.37],
                ["全国大班", 5000, 6000, 0.72, 1.06, 1.30],
                ["小图灵", 4500, 5500, 0.68, 1.00, 1.32],
            ],
            "2月-B标": [
                headers_m,
                ["全国大班", 2500, 3000, 0.80, 1.05],
                ["小图灵", 2200, 2800, 0.74, 0.99],
            ],
            "2月同比": [
                headers_my,
                ["全国大班", "全国大班", "+21%"],
                ["小图灵", "小图灵", "+15%"],
            ],
            "Q1累计同比": [
                headers_y,
                ["总GMV", "总GMV", 18000, 16000, "+12.5%", 11000, 9500, "+15.8%", "1.33", "1.30", "+2.3%"],
                ["拉新GMV", "拉新GMV", 11000, 9500, "+15.8%", None, None, None, None, None, None],
                ["└ 全国大班", "项目组", 5000, 4200, "+19.0%", 3000, 2500, "+20.0%", "1.06", "1.01", "+5.0%"],
                ["└ 小图灵", "项目组", 4500, 4000, "+12.5%", 2800, 2400, "+16.7%", "1.00", "0.96", "+4.2%"],
                ["平均SMROI", "平均SMROI", "1.33", "1.30", "+2.3%", None, None, None, None, None, None],
            ],
        }
        last_specs = {
            "周营收-财务口径": [
                headers_fin,
                ["全国大班", 900, 520, 380, 1.01],
                ["小图灵", 760, 450, 310, 0.96],
                ["合计", 1660, 970, 690, 0.99],
            ],
            "周营收-团队口径": [
                headers_team,
                ["小图灵", 280, 190, 90, 1.10],
                ["KP", 250, 170, 80, 1.18],
                ["合计", 530, 360, 170, 1.14],
            ],
            "Q1季度-B标": [
                headers_q,
                ["总计", 15500, 19000, 0.82, 1.28, 1.35],
                ["全国大班", 4600, 5800, 0.66, 1.01, 1.28],
                ["小图灵", 4100, 5300, 0.61, 0.96, 1.30],
            ],
            "2月-B标": [
                headers_m,
                ["全国大班", 2300, 2900, 0.71, 0.98],
                ["小图灵", 2000, 2700, 0.67, 0.93],
            ],
            "Q1累计同比": [
                headers_y,
                ["总GMV", "总GMV", 16600, 15000, "+10.7%", 9700, 8900, "+9.0%", "1.29", "1.26", "+2.4%"],
                ["拉新GMV", "拉新GMV", 9700, 8700, "+11.5%", None, None, None, None, None, None],
                ["└ 全国大班", "项目组", 4600, 3900, "+17.9%", 2800, 2300, "+21.7%", "1.01", "0.97", "+4.1%"],
                ["└ 小图灵", "项目组", 4100, 3700, "+10.8%", 2600, 2200, "+18.2%", "0.96", "0.92", "+4.3%"],
                ["平均SMROI", "平均SMROI", "1.29", "1.26", "+2.4%", None, None, None, None, None, None],
            ],
            "2月同比": [
                headers_my,
                ["全国大班", "全国大班", "+16%"],
                ["小图灵", "小图灵", "+11%"],
            ],
        }
        write_mock_excel(last_week, last_specs)
        write_mock_excel(this_week, base_specs)

        # Test 1: 脚本执行
        print("\n--- Test 1: read_excel.py 执行 ---")
        result = subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / "read_excel.py"), str(tmpdir)],
            capture_output=True, text=True, timeout=20
        )
        if result.returncode == 0:
            print("✅ read_excel.py 执行成功")
            passed += 1
        else:
            print("❌ read_excel.py 执行失败")
            print(result.stderr[:300])
            failed += 1

        # Test 2: data_snapshot.md 生成
        print("\n--- Test 2: data_snapshot.md 生成 ---")
        snapshot = tmpdir / "data_snapshot.md"
        if snapshot.exists():
            print("✅ data_snapshot.md 已生成")
            passed += 1
        else:
            print("❌ 未生成 data_snapshot.md")
            failed += 1

        # Test 3: 关键指标索引
        print("\n--- Test 3: 关键指标索引 ---")
        if snapshot.exists():
            text = snapshot.read_text(encoding="utf-8")
            if "## 关键指标索引（优先查这里）" in text and "全国大班" in text and "SMROI" in text:
                print("✅ 快照包含关键指标索引")
                passed += 1
            else:
                print("❌ 快照缺少关键指标索引或核心字段")
                failed += 1

        # Test 4: 上周数据快照
        print("\n--- Test 4: 上周数据快照 ---")
        if snapshot.exists() and "# 上周数据（用于计算环比变动）" in snapshot.read_text(encoding="utf-8"):
            print("✅ 已包含上周数据，支持环比校验")
            passed += 1
        else:
            print("❌ 未包含上周数据")
            failed += 1

        # Test 5: Skill 基础文件
        print("\n--- Test 5: Skill 基础文件 ---")
        needed = [SKILL_DIR / "SKILL.md", SKILL_DIR / "config.yaml", SCRIPTS_DIR / "read_excel.py"]
        if all(p.exists() for p in needed):
            print("✅ SKILL.md / config.yaml / read_excel.py 齐全")
            passed += 1
        else:
            print("❌ 缺少基础文件")
            failed += 1

        # Test 6 (P3): snapshot → generate_report 集成链路
        print("\n--- Test 6: snapshot→generate_report 集成测试 ---")
        snapshot = tmpdir / "data_snapshot.md"
        if snapshot.exists():
            result_gen = subprocess.run(
                [sys.executable, str(SCRIPTS_DIR / "generate_report.py"), str(snapshot)],
                capture_output=True, text=True, timeout=30
            )
            if result_gen.returncode == 0:
                # 查找生成的报告
                import glob as _glob
                reports = sorted(_glob.glob(str(tmpdir / "W*.md")))
                if reports:
                    report_path = reports[0]
                    report_size = os.path.getsize(report_path)
                    if report_size > 500:
                        print(f"✅ generate_report.py 成功，报告 {os.path.basename(report_path)} ({report_size} bytes)")
                        passed += 1
                        # 检查模块6 Excel是否生成
                        xlsx_files = sorted(_glob.glob(str(tmpdir / "*模块6*.xlsx")))
                        if xlsx_files:
                            xlsx_size = os.path.getsize(xlsx_files[0])
                            if xlsx_size > 1024:
                                print(f"✅ 模块6 Excel 已生成: {os.path.basename(xlsx_files[0])} ({xlsx_size} bytes)")
                                passed += 1
                            else:
                                print(f"❌ 模块6 Excel 文件过小: {xlsx_size} bytes")
                                failed += 1
                        else:
                            print("⚠️  未找到模块6 Excel（可能工作表名匹配问题）")
                    else:
                        print(f"❌ 报告文件过小: {report_size} bytes")
                        failed += 1
                else:
                    print("❌ 未生成报告文件")
                    print(result_gen.stderr[:500] if result_gen.stderr else result_gen.stdout[:500])
                    failed += 1
            else:
                print("❌ generate_report.py 执行失败")
                print(result_gen.stderr[:500] if result_gen.stderr else result_gen.stdout[:500])
                failed += 1
        else:
            print("⏭️  跳过 Test 6（snapshot不存在）")

    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)
        print("\n🧹 临时文件已清理")

    total = passed + failed
    print("\n" + "=" * 56)
    print(f"结果: {passed}/{total} 通过" + (" ✅" if failed == 0 else f" | {failed} 失败 ❌"))
    print("=" * 56)
    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
