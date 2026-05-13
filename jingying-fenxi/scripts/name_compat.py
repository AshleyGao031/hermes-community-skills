#!/usr/bin/env python3
"""
名称兼容层：让 generate_report.py 同时支持真实名称和脱敏名称的数据输入。

设计：
    - 真实名称工作流完全不受影响（detect 到非脱敏数据时，r() 原样返回）
    - 脱敏模式下，硬编码的真实名自动转为脱敏名
    - 通过检测 snapshot JSON 中的项目组名称自动判断
"""

import json
import os

# ========== 映射表（与 desensitize.py 保持同步） ==========

PROJECT_MAPPING = {
    "全国大班": "项目组A",
    "云领学": "项目组B",
    "小图灵": "项目组C",
    "KP": "项目组D",
    "研习所": "项目组E",
    "纵横工作室": "项目组F",
    "线下店": "项目组G",
    "Deepthink": "项目组H",
    "博闻": "项目组I",
    "思维": "项目组J",
    "新世界": "项目组K",
    "强基业务": "项目组L",
}

BIZLINE_MAPPING = {
    "升学": "业务线A",
    "素养": "业务线B",
}

# 合并映射
NAME_MAPPING = {}
NAME_MAPPING.update(PROJECT_MAPPING)
NAME_MAPPING.update(BIZLINE_MAPPING)

ALL_DESENSITIZED = set(NAME_MAPPING.values())
ALL_REAL = set(NAME_MAPPING.keys())


class NameResolver:
    """名称解析器，自动处理真实/脱敏名称转换"""

    def __init__(self):
        self.is_desensitized = False
        self._real_to_desensitized = dict(NAME_MAPPING)
        self._desensitized_to_real = {v: k for k, v in NAME_MAPPING.items()}

    def detect_from_workbook(self, wb):
        """从 openpyxl workbook 自动检测是否使用脱敏名称"""
        desensitized_count = 0
        real_count = 0

        sheets_to_check = []
        for name in ['周营收-财务口径', '周营收-团队口径', 'Q1季度-B标']:
            if name in wb.sheetnames:
                sheets_to_check.append(name)

        for sheet_name in sheets_to_check:
            ws = wb[sheet_name]
            for r in range(1, min(ws.max_row + 1, 30)):
                for c in range(1, min(ws.max_column + 1, 3)):
                    val = ws.cell(r, c).value
                    if val is None:
                        continue
                    val_str = str(val).strip()
                    if val_str in ALL_DESENSITIZED:
                        desensitized_count += 1
                    if val_str in ALL_REAL:
                        real_count += 1

        self.is_desensitized = desensitized_count > 0 and real_count == 0
        return self.is_desensitized

    def detect_from_snapshot_data(self, data):
        """从 snapshot JSON 数据自动检测是否使用脱敏名称"""
        desensitized_count = 0
        real_count = 0

        for sheet_name in ['周营收-财务口径', '周营收-团队口径']:
            sheet = data.get('data', {}).get(sheet_name, {})
            for row in sheet.get('rows', []):
                name = str(row.get('项目组', '')).strip()
                if name in ALL_DESENSITIZED:
                    desensitized_count += 1
                if name in ALL_REAL:
                    real_count += 1

        self.is_desensitized = desensitized_count > 0 and real_count == 0
        return self.is_desensitized

    def r(self, name):
        """解析名称：脱敏模式下真实名→脱敏名；否则原样返回"""
        if not self.is_desensitized:
            return name
        return self._real_to_desensitized.get(name, name)

    def r_list(self, name_list):
        """解析名称列表（保持顺序）"""
        return [self.r(n) for n in name_list]

    def r_set(self, name_set):
        """解析名称集合"""
        return {self.r(n) for n in name_set}

    def is_name(self, actual_name, canonical_name):
        """检查 actual_name 是否匹配 canonical_name（真实名或脱敏版本）"""
        if actual_name == canonical_name:
            return True
        if self.is_desensitized:
            return actual_name == self._real_to_desensitized.get(canonical_name, canonical_name)
        return False

    def real_name(self, desensitized_name):
        """反向解析：脱敏名 → 真实名"""
        if not self.is_desensitized:
            return desensitized_name
        return self._desensitized_to_real.get(desensitized_name, desensitized_name)

    def load_mapping_json(self, mapping_path):
        """从 mapping.json 加载映射表（可选覆盖内置映射）"""
        if not os.path.exists(mapping_path):
            return False
        try:
            with open(mapping_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            nm = data.get('name_mapping', {})
            if nm:
                self._real_to_desensitized = nm
                self._desensitized_to_real = {v: k for k, v in nm.items()}
                return True
        except Exception:
            pass
        return False
