#!/usr/bin/env python3
"""
Final Synthesized Gantt Chart - t_coupon_issue INSERT 부하 개선
==============================================================
Base: Dense (best data) + Executive styling elements + Cross-validation fixes

Cross-validation decisions:
1. Dense's BE-1/BE-2 split retained (most accurate role mapping)
2. Dense's MD counts on bars retained (self-documenting, no appendix lookup)
3. Dense's Critical Path border + arrow chain retained (strongest CP visualization)
4. Dense's phase label boxes on left retained (clearest phase grouping)
5. Title fixed: "t_coupon_issue INSERT 부하 개선 — 메인 타임라인 (4~5월)"
6. Total MD corrected to match document (118MD + buffer 20MD = 138MD)
7. Phase backgrounds improved for clearer distinction
8. Role badge positioning fixed to avoid clipping
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from matplotlib.lines import Line2D
import numpy as np
from collections import OrderedDict

# ── Font & Global Config ──
plt.rcParams['font.family'] = 'Apple SD Gothic Neo'
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['svg.fonttype'] = 'none'

# ── Color Palette ──
COLORS = {
    'BE-1': '#42A5F5',   # Blue 400
    'BE-2': '#1565C0',   # Blue 800
    'DBA':  '#FF9800',   # Orange 500
    'SRE':  '#66BB6A',   # Green 400
    'QA':   '#AB47BC',   # Purple 400
}

PHASE_BG = {
    0: '#EBF5FB',       # Light blue
    1: '#FEF9E7',       # Light yellow
    2: '#FDEBD0',       # Light orange
    3: '#E8F8F5',       # Light teal
    'post': '#F5EEF8',  # Light purple
}

PHASE_ACCENT = {
    0: '#2980B9',
    1: '#F39C12',
    2: '#E74C3C',
    3: '#27AE60',
    'post': '#8E44AD',
}

# ── Task Data ──
PHASES = OrderedDict()

PHASES[0] = {
    'label': 'P0: 설계 확정',
    'weeks': (1, 1),
    'total_md': 12,
    'tasks': [
        ('BE-1', '벤치마크', 1, 1, 1, True),
        ('BE-1', 'Lua 설계 리뷰', 1, 1, 1, False),
        ('BE-2', 'Lua 설계 리뷰', 1, 1, 1, False),
        ('BE-2', 'Key 구조 확정', 1, 1, 1, False),
        ('DBA',  '벤치마크 지원', 2, 1, 1, True),
        ('DBA',  'idx 분석', 1, 1, 1, False),
        ('SRE',  'Key 정책 확정', 1, 1, 1, False),
        ('SRE',  '대시보드 설계', 3, 1, 1, False),
        ('QA',   '테스트 계획', 1, 1, 1, False),
    ]
}

PHASES[1] = {
    'label': 'P1: 개발',
    'weeks': (2, 5),
    'total_md': 55,
    'tasks': [
        ('BE-1', 'gate_keeper Lua', 5, 2, 3, True),
        ('BE-1', 'compensate Lua', 3, 3, 3.5, True),
        ('BE-1', 'FF 설정', 2, 3.5, 4, False),
        ('BE-1', 'Shadow 준비', 4.5, 4, 5, False),
        ('BE-2', 'MC 통합', 8, 2, 5, True),
        ('BE-2', '보상 워커', 7, 2, 4, False),
        ('BE-2', 'Reconciliation', 6, 4, 5, False),
        ('BE-2', 'Shadow 준비', 4.5, 4, 5, False),
        ('DBA',  '인덱스 사용처 확인', 5, 2, 4, False),
        ('SRE',  '대시보드 구축', 6, 2, 4, False),
        ('QA',   '케이스 작성', 4, 3, 5, False),
    ]
}

PHASES[2] = {
    'label': 'P2: Shadow 검증',
    'weeks': (6, 7),
    'total_md': 31,
    'tasks': [
        ('BE-1', 'Shadow 운영', 4, 6, 7, True),
        ('BE-1', '부하 테스트', 2, 7, 7, False),
        ('BE-2', 'Recon diff 검증', 4, 6, 7, False),
        ('BE-2', '부하 테스트', 2, 7, 7, False),
        ('DBA',  '삭제/복구 리허설', 4, 6, 7, False),
        ('SRE',  '모니터링 강화', 5, 6, 7, False),
        ('QA',   '전수 QA', 10, 6, 7, False),
    ]
}

PHASES[3] = {
    'label': 'P3: 전환·안정화',
    'weeks': (8, 9),
    'total_md': 20,
    'tasks': [
        ('BE-1', 'MC 100% 전환', 3, 8, 8, True),
        ('BE-2', '인덱스 삭제 지원', 3, 8, 8, False),
        ('DBA',  '무중단 삭제', 3, 8, 8, False),
        ('DBA',  '24h 모니터링', 2, 8, 9, False),
        ('SRE',  '7일 안정화', 5, 8, 9, False),
        ('QA',   '회귀 테스트', 4, 8, 8, False),
    ]
}

PHASES['post'] = {
    'label': '후속',
    'weeks': (10, 10),
    'total_md': None,
    'tasks': [
        ('DBA', '인덱스 6개 삭제', None, 10, 10, True),
    ]
}

MILESTONES = [
    (1, 'M0', 'Go/No-Go', '4/4', True),
    (5, 'M1', '개발완료', '5/2', False),
    (7, 'M2', '검증완료', '5/16', False),
    (8, 'M3', '전환완료', '5/23', False),
    (9, 'M4', '안정화완료', '5/30', False),
    (10, 'M5', '삭제완료', '6/6', False),
]

ROLE_ORDER = ['BE-1', 'BE-2', 'DBA', 'SRE', 'QA']

def build_rows():
    rows = []
    y = 0
    phase_y_ranges = {}
    phase_gap = 1.2

    for phase_key, phase_data in PHASES.items():
        phase_start_y = y
        prev_role = None
        for role in ROLE_ORDER:
            role_tasks = [t for t in phase_data['tasks'] if t[0] == role]
            if not role_tasks:
                continue
            if prev_role is not None:
                y += 0.2
            for task in role_tasks:
                rows.append({
                    'y': y,
                    'role': task[0],
                    'name': task[1],
                    'md': task[2],
                    'start': task[3],
                    'end': task[4],
                    'critical': task[5],
                    'phase': phase_key,
                })
                y += 1
            prev_role = role
        phase_y_ranges[phase_key] = (phase_start_y, y - 1)
        y += phase_gap

    return rows, phase_y_ranges

rows, phase_y_ranges = build_rows()

# ── Figure Setup ──
fig, ax = plt.subplots(figsize=(24, 18))
fig.set_facecolor('#FAFBFC')
ax.set_facecolor('#FAFBFC')

BAR_HEIGHT = 0.72
WEEK_WIDTH = 1.0

WEEK_LABELS = {
    1: '4/1', 2: '4/7', 3: '4/14', 4: '4/21', 5: '4/28',
    6: '5/5', 7: '5/12', 8: '5/19', 9: '5/26', 10: '6/2',
}

# ── Phase backgrounds with accent border ──
for phase_key, (py_start, py_end) in phase_y_ranges.items():
    phase_data = PHASES[phase_key]
    bg_color = PHASE_BG.get(phase_key, '#F5F5F5')
    accent = PHASE_ACCENT.get(phase_key, '#999')

    # Full-width background
    rect = FancyBboxPatch(
        (0.6, py_start - BAR_HEIGHT / 2 - 0.2),
        10.8,
        (py_end - py_start) + BAR_HEIGHT + 0.4,
        boxstyle="round,pad=0.12",
        facecolor=bg_color,
        edgecolor=accent,
        linewidth=1.2,
        alpha=0.45,
        zorder=0,
    )
    ax.add_patch(rect)

    # Phase label box in left margin
    mid_y = (py_start + py_end) / 2
    md_text = f"  [ {phase_data['total_md']} MD ]" if phase_data['total_md'] else ""
    label_text = f"{phase_data['label']}{md_text}"
    ax.text(0.2, mid_y, label_text,
            ha='center', va='center', fontsize=11, fontweight='bold',
            color='white', zorder=5,
            bbox=dict(boxstyle='round,pad=0.4', facecolor=accent,
                      edgecolor=accent, alpha=0.92, linewidth=0))

# ── Week grid ──
for w in range(1, 12):
    ax.axvline(x=w, color='#E0E0E0', linewidth=0.5, linestyle='-', zorder=1)

# ── Task bars ──
for row in rows:
    x_start = row['start']
    x_width = row['end'] - row['start'] + WEEK_WIDTH
    y = row['y']
    color = COLORS[row['role']]

    edgecolor = '#C62828' if row['critical'] else color
    linewidth = 3.0 if row['critical'] else 0.8

    bar = FancyBboxPatch(
        (x_start, y - BAR_HEIGHT / 2),
        x_width,
        BAR_HEIGHT,
        boxstyle="round,pad=0.07",
        facecolor=color,
        edgecolor=edgecolor,
        linewidth=linewidth,
        alpha=0.88,
        zorder=3,
    )
    ax.add_patch(bar)

    # Label: "TaskName (NMD)"
    md_str = f"  ({row['md']}MD)" if row['md'] else ""
    label = f"{row['name']}{md_str}"
    text_x = x_start + x_width / 2

    if x_width >= 1.8:
        fontsize = 10 if x_width >= 3.0 else 9
        ax.text(text_x, y, label,
                ha='center', va='center', fontsize=fontsize, fontweight='bold',
                color='white', zorder=4)
    else:
        ax.text(x_start + x_width + 0.08, y, label,
                ha='left', va='center', fontsize=9, fontweight='bold',
                color=color, zorder=4)

    # Role badge
    ax.text(x_start - 0.12, y, row['role'],
            ha='right', va='center', fontsize=8.5, fontweight='bold',
            color=color, zorder=4,
            bbox=dict(boxstyle='round,pad=0.18', facecolor='white',
                      edgecolor=color, alpha=0.93, linewidth=1.0))

# ── Week header ──
max_y_val = max(r['y'] for r in rows)
header_y = -2.5
for w, date_str in WEEK_LABELS.items():
    ax.text(w + 0.5, header_y, f'W{w}\n{date_str}',
            ha='center', va='center', fontsize=11, fontweight='bold',
            color='#37474F')

# ── Milestones ──
for m_week, m_id, m_label, m_date, is_gate in MILESTONES:
    x = m_week + WEEK_WIDTH
    color = '#C62828' if is_gate else '#E65100'
    linestyle = '-' if is_gate else '--'
    lw = 2.0 if is_gate else 1.0

    y_min_val = min(r['y'] for r in rows) - 0.5
    ax.vlines(x=x, ymin=y_min_val, ymax=max_y_val + 0.5,
              color=color, linewidth=lw, linestyle=linestyle, alpha=0.4, zorder=2)

    ax.plot(x, header_y - 1.5, marker='D', markersize=16, color=color,
            markeredgecolor='white', markeredgewidth=2.5, zorder=6)

    gate_text = ' (GATE)' if is_gate else ''
    ax.text(x, header_y - 2.8, f'{m_id}: {m_label}{gate_text}\n{m_date}',
            ha='center', va='center', fontsize=10, fontweight='bold',
            color=color, zorder=6,
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                      edgecolor=color, alpha=0.95, linewidth=1.5))

# ── Critical Path arrows ──
critical_tasks = [r for r in rows if r['critical']]
for i in range(len(critical_tasks) - 1):
    curr = critical_tasks[i]
    nxt = critical_tasks[i + 1]

    x_from = curr['end'] + WEEK_WIDTH - 0.05
    y_from = curr['y']
    x_to = nxt['start'] + 0.05
    y_to = nxt['y']

    dy = abs(y_to - y_from)
    rad = 0.0 if dy < 0.5 else (0.15 if dy < 5 else 0.25)

    arrow = FancyArrowPatch(
        (x_from, y_from), (x_to, y_to),
        arrowstyle='->,head_length=10,head_width=6',
        color='#C62828',
        linewidth=1.8,
        connectionstyle=f'arc3,rad={rad}',
        zorder=5,
        alpha=0.6,
    )
    ax.add_patch(arrow)

# ── Legend ──
legend_elements = []
for role, color in COLORS.items():
    legend_elements.append(mpatches.Patch(facecolor=color, edgecolor='#424242',
                                           linewidth=0.8, label=role, alpha=0.88))
legend_elements.append(mpatches.Patch(facecolor='#BDBDBD', edgecolor='#C62828',
                                       linewidth=3.0, label='Critical Path'))
legend_elements.append(Line2D([0], [0], marker='D', color='w', markerfacecolor='#C62828',
                               markersize=12, label='GATE'))
legend_elements.append(Line2D([0], [0], marker='D', color='w', markerfacecolor='#E65100',
                               markersize=12, label='Milestone'))

ax.legend(handles=legend_elements, loc='upper right', fontsize=11,
          framealpha=0.95, edgecolor='#90A4AE', ncol=4,
          bbox_to_anchor=(0.99, 1.02), fancybox=True)

# ── Title ──
ax.set_title('t_coupon_issue INSERT 부하 개선 — 메인 타임라인 (4~5월)',
             fontsize=20, fontweight='bold', pad=90, color='#212121', loc='left')

# ── Summary bar ──
summary = 'Total: 118 MD + Buffer 20 MD = 138 MD   |   P0: 12   P1: 55   P2: 31   P3: 20   Buffer: 20'
ax.text(0.5, 1.04, summary,
        transform=ax.transAxes, ha='center', va='bottom',
        fontsize=12, fontweight='bold', color='#37474F',
        bbox=dict(boxstyle='round,pad=0.4', facecolor='#E8EAF6',
                  edgecolor='#7986CB', alpha=0.9))

# ── Critical Path annotation ──
cp_text = ('Critical Path: 인덱스 사용 통계 수집(3월) → 벤치마크(W1) → Lua 개발(W2~W3) → '
           'MC 통합(W4~W5) → Shadow(W6~W7) → MC 100%(W8) → 48h 안정화 → 인덱스 삭제(W10)')
ax.text(0.5, -0.025, cp_text,
        transform=ax.transAxes, ha='center', va='top',
        fontsize=11.5, fontweight='bold', color='#C62828',
        bbox=dict(boxstyle='round,pad=0.4', facecolor='#FFEBEE',
                  edgecolor='#C62828', alpha=0.9))

# ── Axes ──
ax.set_xlim(-0.5, 11.8)
ax.set_ylim(max_y_val + 2.5, header_y - 4.5)
ax.set_yticks([])
ax.set_xticks([])
for spine in ax.spines.values():
    spine.set_visible(False)

plt.tight_layout(pad=3.0)
plt.savefig('/tmp/final_gantt.svg', format='svg', bbox_inches='tight', dpi=150)
plt.close()
print("OK: /tmp/final_gantt.svg")
