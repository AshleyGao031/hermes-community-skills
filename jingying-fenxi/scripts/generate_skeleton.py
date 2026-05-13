#!/usr/bin/env python3
"""
经营分析骨架生成器
读取Excel，算完所有数字，按原报告7模块格式输出骨架
分析部分用[待分析]占位，等我填入
"""
import sys, os, json, openpyxl, re
from datetime import datetime

WORK_DIR = '/Users/gaojiayu/clawd/projects/经营分析/课程业务'
DATA_FILE = 'GMV全量数据_2026Q2_2026-04-05.xlsx'
LAST_FILE = 'GMV全量数据_2026Q1_2026-03-31.xlsx'

def sf(v):
    try:
        return float(v) if v not in (None, '', '-', 'None', 'nan') else 0.0
    except: return 0.0

def em(v):
    try:
        return '🟢' if float(v) > 0 else '🔴' if float(v) < 0 else '⚪'
    except: return '⚪'

def pct(v):
    try:
        return f"{float(v)*100:.1f}%"
    except: return str(v)

# ===== 读取Excel =====
wb = openpyxl.load_workbook(os.path.join(WORK_DIR, DATA_FILE), data_only=True)

# 判断季度
fname = DATA_FILE.lower()
quarter = 2 if 'q2' in fname else 1

# 读取周营收财务口径
ws_fin = wb['周营收-财务口径']
fin_rows = []
fin_total = None
for row in ws_fin.iter_rows(min_row=2, values_only=True):
    if not row[0]: continue
    if row[0] == '合计':
        fin_total = {'总营收':sf(row[2]),'拉新GMV':sf(row[5]),'续报GMV':sf(row[7]),'SMROI':sf(row[9]),'SMROI_环比':row[10]}
        continue
    if row[0] in ('','合计'): continue
    fin_rows.append({'项目组':row[0],'类别':row[1],'总营收':sf(row[2]),'占比':row[3],'环比':row[4],
                    '拉新GMV':sf(row[5]),'拉新GMV_环比':row[6],'续报GMV':sf(row[7]),'续报GMV_环比':row[8],
                    'SMROI':sf(row[9]),'SMROI_环比':row[10]})

# 读取周营收团队口径
ws_team = wb['周营收-团队口径']
team_rows = []
team_total = None
for row in ws_team.iter_rows(min_row=2, values_only=True):
    if not row[0]: continue
    if row[0] == '合计':
        team_total = {'总营收':sf(row[2]),'市场GMV':sf(row[5]),'辅导GMV':sf(row[7]),'SMROI':sf(row[9])}
        continue
    if row[0] in ('','合计'): continue
    team_rows.append({'项目组':row[0],'类别':row[1],'总营收':sf(row[2]),'占比':row[3],'环比':row[4],
                      '市场GMV':sf(row[5]),'市场GMV_环比':row[6],'辅导GMV':sf(row[7]),'辅导GMV_环比':row[8],
                      'SMROI':sf(row[9]),'SMROI_环比':row[10]})

# 读取Q2季度B标
ws_qb = wb['Q2季度-B标']
qb_rows = []
for row in ws_qb.iter_rows(min_row=2, values_only=True):
    if not row[0] or row[0] in ('','总计'): continue
    qb_rows.append({'项目组':str(row[0]).strip(),'总GMV':sf(row[9]),'目标':sf(row[10]),
                    '进度':row[11],'续报进度':row[6],'拉新SMROI':row[7],'拉新进度':row[3]})

# 读取Q2季度A标
ws_qa = wb['Q2季度-A标']
qa_rows = []
for row in ws_qa.iter_rows(min_row=2, values_only=True):
    if not row[0] or row[0] in ('','总计'): continue
    qa_rows.append({'项目组':str(row[0]).strip(),'总GMV':sf(row[9]),'目标':sf(row[10]),'进度':row[11]})

# 读取Q2累计同比
ws_yoy = wb['Q2累计同比']
yoy_rows = []
for row in ws_yoy.iter_rows(min_row=2, values_only=True):
    if not row[0] or not row[3]: continue
    yoy_rows.append({'_col_0':row[0],'_col_3':row[3],'_col_4':row[4],'_col_5':row[5],
                     '_col_6':row[6],'_col_7':row[7],'_col_8':row[8],'_col_9':row[9],
                     '_col_10':row[10],'_col_11':row[11]})

# 读取4月B标
ws_mb = wb['4月-B标']
mb_rows = []
for row in ws_mb.iter_rows(min_row=2, values_only=True):
    if not row[0] or row[0] in ('','总计'): continue
    mb_rows.append({'项目组':str(row[0]).strip(),'总GMV':sf(row[9]),'目标':sf(row[10]),
                    '进度':row[11],'续报进度':row[6],'拉新SMROI':row[7],'拉新进度':row[3]})

# 读取4月A标
ws_ma = wb['4月-A标']
ma_rows = []
for row in ws_ma.iter_rows(min_row=2, values_only=True):
    if not row[0] or row[0] in ('','总计'): continue
    ma_rows.append({'项目组':str(row[0]).strip(),'总GMV':sf(row[9]),'目标':sf(row[10]),'进度':row[11]})

# 读取上周财务口径
wb_lw = openpyxl.load_workbook(os.path.join(WORK_DIR, LAST_FILE), data_only=True)
ws_lw = wb_lw['周营收-财务口径']
lw_fin = []
lw_total = None
for row in ws_lw.iter_rows(min_row=2, values_only=True):
    if not row[0]: continue
    if row[0] == '合计':
        lw_total = {'总营收':sf(row[2]),'拉新GMV':sf(row[5]),'续报GMV':sf(row[7]),'SMROI':sf(row[9])}
        continue
    if row[0] in ('','合计'): continue
    lw_fin.append({'项目组':row[0],'类别':row[1],'总营收':sf(row[2]),'拉新GMV':sf(row[5]),'续报GMV':sf(row[7]),'SMROI':sf(row[9])})

# ===== 计算 =====
tw = fin_total
lw = lw_total

# 环比
chg_rev = (tw['总营收']-lw['总营收'])/abs(lw['总营收']) if lw['总营收'] else 0
chg_lx = (tw['拉新GMV']-lw['拉新GMV'])/abs(lw['拉新GMV']) if lw['拉新GMV'] else 0
chg_xb = (tw['续报GMV']-lw['续报GMV'])/abs(lw['续报GMV']) if lw['续报GMV'] else 0
abs_rev = tw['总营收']-lw['总营收']
abs_lx = tw['拉新GMV']-lw['拉新GMV']
abs_xb = tw['续报GMV']-lw['续报GMV']

# 升降判断
def trend_label(gmv_val, smroi_val):
    if gmv_val>0 and smroi_val>0: return "量增效增"
    elif gmv_val>0 and smroi_val<0: return "量增效降"
    elif gmv_val<0 and smroi_val>0: return "量跌效升"
    else: return "量跌效降"

trend = trend_label(chg_rev, chg_xb)

# 业务线
sx_names = ['全国大班','云领学','强基业务','研习所','新世界']
sy_names = ['Deepthink','KP','博闻','小图灵','思维','纵横工作室','线下店']

sx = [r for r in fin_rows if r['项目组'] in sx_names]
sy_fin = [r for r in fin_rows if r['项目组'] in sy_names]
sy_team = [r for r in team_rows if r['项目组'] in sy_names]
sx_total = sum(r['总营收'] for r in sx)
sy_total = sum(r['总营收'] for r in sy_fin)
sx_lx_total = sum(r['拉新GMV'] for r in sx)
sy_lx_total = sum(r['拉新GMV'] for r in sy_fin)
sx_share = sx_total/tw['总营收']*100 if tw['总营收'] else 0
sy_share = sy_total/tw['总营收']*100 if tw['总营收'] else 0

# 全国大班单独
dqb = next((r for r in fin_rows if r['项目组']=='全国大班'), None)
dqb_share = dqb['总营收']/tw['总营收']*100 if dqb and tw['总营收'] else 0

# Q1尾款
q1_tail = lw['续报GMV'] if lw else 0
natural_lx = tw['拉新GMV']

# 拉新Top3
top3_lx = sorted(sx, key=lambda x: x['拉新GMV']-next((r['拉新GMV'] for r in lw_fin if r['项目组']==x['项目组']), 0), reverse=True)[:3]
top3_xb = sorted(sx, key=lambda x: x['续报GMV']-next((r['续报GMV'] for r in lw_fin if r['项目组']==x['项目组']), 0), reverse=True)[:3]

# 素养汇总
sy_mkt = sum(r['市场GMV'] for r in sy_team)
sy_ment = sum(r['辅导GMV'] for r in sy_team)
lw_sy_mkt = sum(r['市场GMV'] for r in team_rows if r['项目组'] in sy_names)
lw_sy_ment = sum(r['辅导GMV'] for r in team_rows if r['项目组'] in sy_names)
sy_mkt_chg = (sy_mkt-lw_sy_mkt)/abs(lw_sy_mkt) if lw_sy_mkt else 0
sy_ment_chg = (sy_ment-lw_sy_ment)/abs(lw_sy_ment) if lw_sy_ment else 0
sy_rev_chg = (sy_total-sum(r['总营收'] for r in sy_fin if r['总营收']>0)/abs(sum(r['总营收'] for r in sy_fin if r['总营收']>0)) if sum(r['总营收'] for r in sy_fin if r['总营收']>0) else 0

# 素养各项目SMROI排名
sy_smroi_ranked = sorted([(r['项目组'], r['SMROI']) for r in sy_team], key=lambda x: x[1], reverse=True)
best_sy_name, best_sy_smroi = sy_smroi_ranked[0] if sy_smroi_ranked else ('暂无', 0)
pos_smroi = [(n,v) for n,v in sy_smroi_ranked if v>0]
worst_sy_name, worst_sy_smroi = pos_smroi[-1] if pos_smroi else ('暂无', 0)

# 风险扫描
risk = []
for r in fin_rows:
    n = r['项目组']
    if n in ('', '合计'): continue
    rev = r['总营收']; smr = r['SMROI']
    if rev < 0:
        risk.append(('GMV为负', n, rev))
    elif smr < 1:
        risk.append(('SMROI亏损', n, smr))
risk.sort(key=lambda x: abs(x[2]), reverse=True)
top_risk = risk[0] if risk else None

# Q2进度状态判断
def progress_status(prog, time_prog=5.5, threshold=5):
    diff = prog - time_prog
    if diff > threshold: return '✅超前', f'+{diff:.1f}pp'
    elif diff < -threshold: return '🔴落后', f'{diff:.1f}pp'
    else: return '⚠️边缘', f'{diff:+.1f}pp'

# 同比数据
yoy_dict = {}
for row in yoy_rows:
    v = str(row.get('_col_0',''))
    if v and '20' in v:
        yoy_dict[v] = row

# ===== 输出骨架报告 =====
lines = []
lines.append(f"# W14 经营分析报告（3月30日-4月5日）")
lines.append(f"> 数据截止：2026-04-05 | 分析日期：{datetime.now().strftime('%Y-%m-%d')} | 骨架生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}")
lines.append("")
lines.append("---")
lines.append("")
lines.append("## 时间进度基准")
lines.append(f"- **Q2时间进度**：{5.5}%（5/91天）")
lines.append(f"- **4月时间进度**：{16.7}%（5/30天）")
lines.append("")
lines.append("---")
lines.append("")
lines.append("## 模块1：单周营收趋势（财务口径）")
lines.append("**W14（3月30日-4月5日）数据：**")
lines.append("")
lines.append("| 指标 | 本周 | 环比 | 绝对变动 |")
lines.append("| --------- | --------- | -------- | -------- |")
lines.append(f"| 总营收 | {tw['总营收']:.1f}万 | {em(chg_rev)}{'+'if chg_rev>0 else ''}{chg_rev*100:.1f}% | {'+'if abs_rev>0 else ''}{abs_rev:.1f}万 |")
lines.append(f"| 拉新GMV | {tw['拉新GMV']:.1f}万 | {em(chg_lx)}{'+'if chg_lx>0 else ''}{chg_lx*100:.1f}% | {'+'if abs_lx>0 else ''}{abs_lx:.1f}万 |")
lines.append(f"| 续报GMV | {tw['续报GMV']:.1f}万 | {em(chg_xb)}{'+'if chg_xb>0 else ''}{chg_xb*100:.1f}% | {'+'if abs_xb>0 else ''}{abs_xb:.1f}万 |")
lines.append(f"| 拉新SMROI | {tw['SMROI']:.2f} | 🔴{tw['SMROI_环比']} | - |")
lines.append("")
lines.append(f"**整体趋势：[待分析——由模型根据数据判断趋势类型并说明原因]**")
lines.append(f"- 总营收{chg_rev*100:+.1f}%至{em(chg_rev)}{tw['总营收']:.1f}万")
lines.append(f"- 拉新GMV {tw['拉新GMV']:.1f}万（{em(chg_lx)}{chg_lx*100:+.1f}%），SMROI {tw['SMROI']:.2f}")
lines.append(f"- 续报GMV {tw['续报GMV']:.1f}万（{em(chg_xb)}{chg_xb*100:+.1f}%）")
lines.append(f"- Q1尾款：{q1_tail:.1f}万 | Q2自然增量：{natural_lx:.1f}万")
lines.append("")
lines.append("### 拉新GMV Top3 及 SMROI 趋势")
lines.append("按拉新GMV绝对变动额排序（本周 - 上周）：")
lines.append("")
lines.append("| 排名 | 项目组 | 拉新GMV变动 | 本周SMROI | 说明 |")
lines.append("| ---- | -------- | ----------- | --------- | ---- |")
for i, r in enumerate(top3_lx, 1):
    lw_r = next((x for x in lw_fin if x['项目组']==r['项目组']), None)
    lw_smroi = lw_r['SMROI'] if lw_r else 0
    abs_chg_lx = r['拉新GMV'] - (lw_r['拉新GMV'] if lw_r else 0)
    chg_dir = '🟢+' if abs_chg_lx > 0 else '🔴'
    # SMROI变化
    if lw_smroi and lw_smroi != 0:
        smroi_chg_pct = (r['SMROI']-lw_smroi)/abs(lw_smroi)*100
        if smroi_chg_pct > 10: note = "效率提升"
        elif smroi_chg_pct < -10: note = "效率下滑"
        else: note = "效率稳定"
    else:
        note = "数据暂无环比"
    lines.append(f"| {i} | {r['项目组']} | {chg_dir}{abs(abs_chg_lx):.1f}万 | {r['SMROI']:.2f} | {note} |")
lines.append("")
lines.append("**续报变动Top3：**")
lines.append("")
lines.append("| 排名 | 项目组 | 续报GMV变动 |")
lines.append("| ---- | -------- | ----------- |")
for i, r in enumerate(top3_xb, 1):
    lw_r = next((x for x in lw_fin if x['项目组']==r['项目组']), None)
    abs_chg_xb = r['续报GMV'] - (lw_r['续报GMV'] if lw_r else 0)
    chg_dir = '🟢+' if abs_chg_xb > 0 else '🔴'
    lines.append(f"| {i} | {r['项目组']} | {chg_dir}{abs(abs_chg_xb):.1f}万 |")
lines.append("")
lines.append("---")
lines.append("")
lines.append("## 模块2：素养项目组周营收（团队口径）")
lines.append("**素养整体汇总：**")
lines.append("")
lines.append(f"| 指标 | 本周 | 环比 |")
lines.append("| ------- | ------- | --------- |")
lines.append(f"| 总营收 | {sy_total:.1f}万 | 🔴待计算 |")
lines.append(f"| 市场GMV | {sy_mkt:.1f}万 | 🔴待计算 |")
lines.append(f"| 辅导GMV | {sy_ment:.1f}万 | 🔴待计算 |")
lines.append("")
lines.append("**各素养项目组详情：**")
lines.append("")
lines.append(f"| 项目组 | 总营收 | 市场GMV | 辅导GMV | SMROI | 环比趋势 |")
lines.append("| ---------- | ------- | ------- | ------- | ----- | --------- |")
for r in sy_team:
    rev_chg = '待计算'
    lines.append(f"| {r['项目组']} | {r['总营收']:.1f}万 | {r['市场GMV']:.1f}万 | {r['辅导GMV']:.1f}万 | {r['SMROI']:.2f} | {rev_chg} |")
lines.append("")
lines.append("**素养整体动因总结：[待分析——由模型判断原因并给出定性描述]**")
lines.append(f"- 素养总营收 {sy_total:.1f}万（环比🔴待计算）")
lines.append(f"- 市场GMV {sy_mkt:.1f}万（环比🔴待计算）")
lines.append(f"- 辅导GMV {sy_ment:.1f}万（环比🔴待计算）")
lines.append(f"- SMROI最优：{best_sy_name} {best_sy_smroi:.2f} | 最差：{worst_sy_name} {worst_sy_smroi:.2f}")
lines.append("")
lines.append("---")
lines.append("")
lines.append("## 模块3：各项目组GMV进度及SMROI达标")
lines.append("### Q2季度进度分析（vs 5.5%时间进度）")
lines.append("")
lines.append(f"| 项目组 | Q2进度(B标) | 状态 | B标总达成率 | A标总达成率 | B标拉新进度 | B标续报进度 |")
lines.append("| ---------- | ------- | -------- | ------ | ------ | ------ | ------ |")
# 按进度排序
def get_qb(name):
    for r in qb_rows:
        if name in r['项目组']: return r
    return None
def get_qa(name):
    for r in qa_rows:
        if name in r['项目组']: return r
    return None

all_proj = sx_names + sy_names
for pname in all_proj:
    qbr = get_qb(pname)
    qar = get_qa(pname)
    if not qbr: continue
    prog_str = qbr['进度'] if qbr['进度'] else '-'
    try: prog_val = float(str(prog_str).replace('%',''))
    except: prog_val = 0
    status, diff_str = progress_status(prog_val)
    qbr_rate = qbr['进度'] if qbr['进度'] else '-'
    qar_rate = qar['进度'] if qar and qar['进度'] else '-'
    lx_prog = qbr['拉新进度'] if qbr['拉新进度'] else '-'
    xb_prog = qbr['续报进度'] if qbr['续报进度'] else '-'
    lines.append(f"| {pname} | {prog_str} | {status} | {qbr_rate} | {qar_rate} | {lx_prog} | {xb_prog} |")
lines.append("")
lines.append("### 4月进度分析（vs 16.7%时间进度）")
lines.append("")
lines.append(f"| 项目组 | 4月进度(B标) | 状态 | B标总达成率 | A标总达成率 | B标拉新进度 | B标续报进度 |")
lines.append("| ---------- | ------- | -------- | ------ | ------ | ------ | ------ |")
def get_mb(name):
    for r in mb_rows:
        if name in r['项目组']: return r
    return None
def get_ma(name):
    for r in ma_rows:
        if name in r['项目组']: return r
    return None

for pname in all_proj:
    mbr = get_mb(pname)
    mar = get_ma(pname)
    if not mbr: continue
    prog_str = mbr['进度'] if mbr['进度'] else '-'
    try: prog_val = float(str(prog_str).replace('%',''))
    except: prog_val = 0
    status, diff_str = progress_status(prog_val, time_prog=16.7, threshold=5)
    mbr_rate = mbr['进度'] if mbr['进度'] else '-'
    mar_rate = mar['进度'] if mar and mar['进度'] else '-'
    lx_prog = mbr['拉新进度'] if mbr['拉新进度'] else '-'
    xb_prog = mbr['续报进度'] if mbr['续报进度'] else '-'
    lines.append(f"| {pname} | {prog_str} | {status} | {mbr_rate} | {mar_rate} | {lx_prog} | {xb_prog} |")
lines.append("")
lines.append("---")
lines.append("")
lines.append("## 模块4：与上周对比（复利跟踪）")
lines.append("### 风险等级变化追踪")
lines.append("> ⚠️ [待分析——由模型对比画像卡数据，判断各项目组风险变化]")
lines.append("")
lines.append("[待补充-画像卡数据]")
lines.append("")
lines.append("---")
lines.append("")
lines.append("## 模块5：Q2累计同比分析")
lines.append("### 整体同比表现")
lines.append("")
# 从yoy_rows找总计
def get_yoy(key):
    for r in yoy_rows:
        if key in str(r.get('_col_0','')): return r
    return None

yoy_total = get_yoy('总GMV')
yoy_lx = get_yoy('拉新GMV')
yoy_xb = get_yoy('续报GMV')
yoy_smroi = get_yoy('平均SMROI')

lines.append("| 指标 | 2026年Q2 | 2025年Q2 | 同比变化 |")
lines.append("| --------- | -------- | -------- | -------- |")
if yoy_total:
    v26=sf(yoy_total.get('_col_1')); v25=sf(yoy_total.get('_col_2'))
    chg=(v26-v25)/abs(v25)*100 if v25 else 0
    lines.append(f"| 总GMV | {v26:.1f}万 | {v25:.1f}万 | {em(chg)}{chg:+.1f}% |")
if yoy_lx:
    v26=sf(yoy_lx.get('_col_1')); v25=sf(yoy_lx.get('_col_2'))
    chg=(v26-v25)/abs(v25)*100 if v25 else 0
    lines.append(f"| 拉新GMV | {v26:.1f}万 | {v25:.1f}万 | {em(chg)}{chg:+.1f}% |")
if yoy_xb:
    v26=sf(yoy_xb.get('_col_1')); v25=sf(yoy_xb.get('_col_2'))
    chg=(v26-v25)/abs(v25)*100 if v25 else 0
    lines.append(f"| 续报GMV | {v26:.1f}万 | {v25:.1f}万 | {em(chg)}{chg:+.1f}% |")
if yoy_smroi:
    v26=sf(yoy_smroi.get('_col_1')); v25=sf(yoy_smroi.get('_col_2'))
    chg=v26-v25
    lines.append(f"| 平均SMROI | {v26:.2f} | {v25:.2f} | {em(chg)}{chg:+.2f} |")
lines.append("")
lines.append("### 业务线同比分析")
lines.append(f"**升学业务线（5个项目组）：[待分析]**")
lines.append(f"**素养业务线（7个项目组）：[待分析]**")
lines.append("")
lines.append("### 重点项目组同比亮点")
lines.append("")
lines.append("| 项目组 | 2026 GMV | 2025 GMV | 同比增长 | 关键表现 |")
lines.append("| -------- | -------- | -------- | --------- | ---------------------- |")
for r in yoy_rows:
    name = str(r.get('_col_0',''))
    if not name or '└' not in name: continue
    if any(n in name for n in sy_names):
        v26=sf(r.get('_col_3')); v25=sf(r.get('_col_4'))
        chg_str = r.get('_col_5','-')
        try: chg_v = float(str(chg_str).replace('%','').replace('+',''))
        except: chg_v = 0
        clean = name.lstrip('├└─│┬┴ ')
        note = "[待分析——模型判断]"
        lines.append(f"| {clean} | {v26:.1f}万 | {v25:.1f}万 | {em(chg_v)}{chg_str} | {note} |")
lines.append("")
lines.append("### 同比挑战项目组")
lines.append("")
lines.append("| 项目组 | 2026 GMV | 2025 GMV | 同比下降 | 主要挑战 |")
lines.append("| ---------- | -------- | -------- | -------- | -------------------------- |")
lines.append("[待分析——模型判断]")

# ===== 模块6：LCT分析 =====
lines.append("")
lines.append("---")
lines.append("")
lines.append("## 模块6：课程业务（LCT）分析")
lines.append(f"**更新人：___ 更新日期：{datetime.now().strftime('%Y-%m-%d')}**")
lines.append("")
lines.append("### 1. 本周速览")
lines.append("")
lines.append(f"| **指标** | **本周实际** | **上周实际** | **环比** | **Q2累计** | **Q2预算** | **达成率** |")
lines.append(f"| :------------- | :----------------- | :----------------- | :------------- | :--------------- | :--------------- | :--------------- |")

# 汇总数据
lw_rev = lw['总营收'] if lw else 0
lw_lx = lw['拉新GMV'] if lw else 0
lw_xb = lw['续报GMV'] if lw else 0
lw_smroi = lw['SMROI'] if lw else 0

yoy_total_row = get_yoy('总GMV')
q2_budget_total = sf(yoy_total_row.get('_col_1')) if yoy_total_row else 0
q2_target_total = sf(yoy_total_row.get('_col_2')) if yoy_total_row else 0
q2_rate = q2_budget_total/q2_target_total*100 if q2_target_total else 0

lines.append(f"| GMV（万） | {tw['总营收']:.1f} | {lw_rev:.1f} | {em(chg_rev)}{chg_rev*100:+.1f}% | {q2_budget_total:.1f} | {q2_target_total:.1f} | {q2_rate:.1f}% |")
lines.append(f"| 其中：拉新 | {tw['拉新GMV']:.1f} | {lw_lx:.1f} | {em(chg_lx)}{chg_lx*100:+.1f}% | 待填 | 待填 | 待填 |")
lines.append(f"| 其中：续报 | {tw['续报GMV']:.1f} | {lw_xb:.1f} | {em(chg_xb)}{chg_xb*100:+.1f}% | 待填 | 待填 | 待填 |")
lines.append(f"| 市场SMROI | 待填 | 待填 | 待填 | 待填 | 待填 | 待填 |")
lines.append(f"| 项目SMROI | {tw['SMROI']:.2f} | {lw_smroi:.2f} | {em(chg_rev)}{tw['SMROI_环比']} | 待填 | 待填 | 待填 |")
lines.append("")
lines.append(f"**一句话总结：[待分析——模型根据数据判断本周整体情况]**")
lines.append(f"- Q2首周整体量增效增（总营收 {tw['总营收']:.1f}万，环比{em(chg_rev)}{chg_rev*100:+.1f}%），拉新SMROI {tw['SMROI']:.2f}")
lines.append(f"- 本周续报冲量主要来自Q1结算尾款约{q1_tail:.1f}万，Q2自然增量约{natural_lx:.1f}万")
lines.append(f"- 全国大班占比{dqb_share:.0f}%为最大单一引擎，升学线SMROI同比[待分析]")
lines.append("")
lines.append("### 2. 分产品线")
lines.append("")
lines.append(f"| **产品线** | **本周GMV（万）** | **周环比** | **Q2累计（万）** | **Q2预算达成率** | **上年同期（万）** | **季度同比** | **备注** |")
lines.append(f"| :--------------- | :---------------------- | :---------------- | :--------------------- | :--------------------- | :------------------ | :------------- | :------------------------------- |")

# 升学线
sx_yoy = get_yoy('升学')
sx_yoy_26 = sf(sx_yoy.get('_col_3')) if sx_yoy else 0
sx_yoy_25 = sf(sx_yoy.get('_col_4')) if sx_yoy else 0
sx_yoy_chg = (sx_yoy_26-sx_yoy_25)/abs(sx_yoy_25)*100 if sx_yoy_25 else 0
lines.append(f"| **升学** | **{sx_total:.1f}** | **{em(chg_rev)}{chg_rev*100:+.1f}%** | **{sx_total:.1f}** | **{sx_total/sx_yoy_25*100:.1f}%** | **{sx_yoy_25:.1f}** | **{em(sx_yoy_chg)}{sx_yoy_chg:+.1f}%** | - |")
for r in sx:
    lw_r = next((x for x in lw_fin if x['项目组']==r['项目组']), None)
    lx_chg_r = (r['拉新GMV']-(lw_r['拉新GMV'] if lw_r else 0))/abs(lw_r['拉新GMV'] if lw_r and lw_r['拉新GMV'] else 1)
    qbr = get_qb(r['项目组'])
    prog = qbr['进度'] if qbr and qbr['进度'] else '-'
    yoy_r = get_yoy(r['项目组'])
    yoy_25 = sf(yoy_r.get('_col_4')) if yoy_r else 0
    yoy_chg_r = (sf(yoy_r.get('_col_3'))-yoy_25)/abs(yoy_25)*100 if yoy_r and yoy_25 else 0
    rev = r['总营收']
    lw_rev_r = lw_r['总营收'] if lw_r else 0
    rev_chg = (rev-lw_rev_r)/abs(lw_rev_r) if lw_rev_r else 0
    lines.append(f"| └ {r['项目组']} | {r['总营收']:.1f} | {em(rev_chg)}{rev_chg*100:+.1f}% | {r['总营收']:.1f} | {prog} | {yoy_25:.1f} | {em(yoy_chg_r)}{yoy_chg_r:+.1f}% | - |")

# 素养线
sy_yoy = get_yoy('素养')
sy_yoy_26 = sf(sy_yoy.get('_col_3')) if sy_yoy else 0
sy_yoy_25 = sf(sy_yoy.get('_col_4')) if sy_yoy else 0
sy_yoy_chg = (sy_yoy_26-sy_yoy_25)/abs(sy_yoy_25)*100 if sy_yoy_25 else 0
lines.append(f"| **素养** | **{sy_total:.1f}** | **🔴待计算** | **{sy_total:.1f}** | **Q2落后** | **{sy_yoy_25:.1f}** | **🔴{sy_yoy_chg:+.1f}%** | **Q2落后** |")
for r in sy_fin:
    lw_r = next((x for x in lw_fin if x['项目组']==r['项目组']), None)
    lw_rev_r = lw_r['总营收'] if lw_r else 0
    rev_chg = (r['总营收']-lw_rev_r)/abs(lw_rev_r) if lw_rev_r else 0
    yoy_r = get_yoy(r['项目组'])
    yoy_25 = sf(yoy_r.get('_col_4')) if yoy_r else 0
    yoy_chg_r = (sf(yoy_r.get('_col_3'))-yoy_25)/abs(yoy_25)*100 if yoy_r and yoy_25 else 0
    lines.append(f"| └ {r['项目组']} | {r['总营收']:.1f} | {em(rev_chg)}{rev_chg*100:+.1f}% | {r['总营收']:.1f} | - | {yoy_25:.1f} | {em(yoy_chg_r)}{yoy_chg_r:+.1f}% | - |")

lines.append("")
lines.append("### 3. 关键洞察")
lines.append("")
lines.append("**🟢 积极信号：[待分析——模型判断本周最值得关注的正面变化，2-3个要点]**")
lines.append(f"- 升学线占比{sx_share:.0f}%为核心引擎；全国大班单独占比{dqb_share:.0f}%")
lines.append(f"- [模型填入：具体积极信号]")
lines.append("")
lines.append("**🔴 风险关注：[待分析——模型判断本周最需要关注的风险点，2-3个要点]**")
lines.append(f"- 全国大班集中度高（占比{dqb_share:.0f}%），一旦下滑将拖累整体。素养占比仅{sy_share:.0f}%严重收缩")
lines.append(f"- [模型填入：具体风险项目]")

# ===== 模块7：Wording =====
lines.append("")
lines.append("---")
lines.append("")
lines.append("## 模块7：周报模板（自动填充）")
lines.append("")
lines.append("### 整体 Wording 模板")
lines.append("")
lines.append("```")
lines.append(f"最近一周（W14: 3月30日-4月5日）总营收 {tw['总营收']:.1f}万（环比{em(chg_rev)}{chg_rev*100:+.1f}%），拉新GMV {tw['拉新GMV']:.1f}万（环比{em(chg_lx)}{chg_lx*100:+.1f}%），续报GMV {tw['续报GMV']:.1f}万（环比{em(chg_xb)}{chg_xb*100:+.1f}%），拉新SMROI {tw['SMROI']:.2f}（环比{em(chg_rev)}{tw['SMROI_环比']}）。[待分析——模型补充本周增长驱动分析]")
lines.append("")
lines.append("其中拉新：[待模型填充]")
lines.append("续报：[待模型填充]")
lines.append("```")
lines.append("")
lines.append("### 素养 Wording 模板")
lines.append("")
lines.append("```")
lines.append(f"素养本周整体总营收{sy_total:.1f}万（环比🔴待计算），市场GMV {sy_mkt:.1f}万（环比🔴待计算），辅导GMV {sy_ment:.1f}万（环比🔴待计算）。[待分析——模型给出定性]")
lines.append(f"* [待模型填充：各项目组市场GMV明细]")
lines.append("```")

# ===== 核心洞察与建议 =====
lines.append("")
lines.append("---")
lines.append("")
lines.append("## 核心洞察与建议")
lines.append("")
lines.append("**Q2首周核心判断：[待分析——模型根据数据判断，重点说明Q1尾款和Q2自然增量]**")
lines.append(f"- 本周{tw['总营收']:.1f}万中约{q1_tail:.1f}万来自Q1续报结算尾款，Q2自然增量约{natural_lx:.1f}万")
lines.append(f"- [模型填入：升学SMROI同比、Q2自然增量质量判断]")
lines.append("")
lines.append("**优先级排序：**")
if top_risk:
    if top_risk[0] == 'GMV为负':
        lines.append(f"🔴 **高优先级：** {top_risk[1]}GMV{top_risk[2]:.1f}万为负，需排查原因")
    else:
        lines.append(f"🔴 **高优先级：** {top_risk[1]}SMROI {top_risk[2]:.2f}<1，投放效率亏损，需确认投放策略")
lines.append(f"🟡 **中优先级：** 全国大班占比{dqb_share:.0f}%的集中度风险，建议与业务沟通云领学等高效项目的扩张可能性")
lines.append("🟡 **中优先级：** [待模型分析：确认素养类同比变化的原因]")
lines.append(f"🟢 **持续关注：** {best_sy_name}（SMROI {best_sy_smroi:.2f}）[模型判断：是否值得关注]")
lines.append(f"**下周重点观察：[待分析——模型基于数据给出1-2个下周重点]**")
lines.append("")
lines.append("---")
lines.append("")
lines.append(f"**骨架生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}**")
lines.append(f"**数据来源：{DATA_FILE}**")
lines.append(f"**⚠️ 标注[待分析]的部分需要模型填入分析判断**")

out = os.path.join(WORK_DIR, 'W14_skeleton_2026-04-09.md')
with open(out, 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))
print(f"✅ 骨架已生成: {out}")
