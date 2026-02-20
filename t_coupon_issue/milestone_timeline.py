#!/usr/bin/env python3
"""
Final Synthesized Milestone Timeline - t_coupon_issue INSERT 부하 개선
=====================================================================
Base: Dense (best features) + Executive card styling + Cross-validation fixes

Cross-validation decisions:
1. Dense's duration arrows retained (unique, high operational value)
2. Dense's rollback annotations retained (operational context in chart)
3. Dense's phase ribbon retained (proportional width, color-coded)
4. Executive's card styling adapted (colored top stripe approach)
5. Title fixed: "t_coupon_issue INSERT 부하 개선 — 마일스톤 & Exit Criteria"
6. GATE marker enlarged and made more prominent
7. Card font size increased for readability
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
from matplotlib.lines import Line2D
import numpy as np

# ── Font & Global Config ──
plt.rcParams['font.family'] = 'Apple SD Gothic Neo'
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['svg.fonttype'] = 'none'

# ── Colors ──
MS_COLORS = {
    'M0': '#E74C3C',   # Red (GATE)
    'M1': '#3498DB',   # Blue
    'M2': '#2ECC71',   # Green
    'M3': '#E67E22',   # Orange
    'M4': '#9B59B6',   # Purple
    'M5': '#1ABC9C',   # Teal
}

PHASE_COLORS = {
    'P0': '#E74C3C',
    'P1': '#3498DB',
    'P2': '#2ECC71',
    'P3': '#E67E22',
    'post': '#9B59B6',
}

BG_COLOR = '#FAFBFC'
TEXT_COLOR = '#2C3E50'
SUBTEXT_COLOR = '#7F8C8D'

# ── Milestones ──
milestones = [
    {
        'id': 'M0', 'week': 1, 'date': '4/4 (W1)', 'title': '설계 확정',
        'phase': 'P0', 'type': 'GATE',
        'exit': ['프로덕션 벤치마크 3.0x+ 달성', '설계 리뷰 완료'],
        'rollback': None,
    },
    {
        'id': 'M1', 'week': 5, 'date': '5/2 (W5)', 'title': '개발 완료',
        'phase': 'P1', 'type': 'PASS',
        'exit': ['단위 테스트 통과', 'Feature Flag 동작', 'Shadow Mode 배포 가능'],
        'rollback': 'FF OFF → DB 즉시 전환 (<1분)',
    },
    {
        'id': 'M2', 'week': 7, 'date': '5/16 (W7)', 'title': '검증 완료',
        'phase': 'P2', 'type': 'PASS',
        'exit': ['Shadow Mode 1주+ 무장애', 'TPS 3.4x+ 달성', 'QA 전수 통과'],
        'rollback': 'Lua script: 이전 버전 배포 (<5분)',
    },
    {
        'id': 'M3', 'week': 8, 'date': '5/23 (W8)', 'title': 'MC 전환 완료',
        'phase': 'P3', 'type': 'PASS',
        'exit': ['MC 100% + 48h 안정화', 'drift < 0.01%'],
        'rollback': 'Redis MC: FF → DB 전환 (<1분)',
    },
    {
        'id': 'M4', 'week': 9, 'date': '5/30 (W9)', 'title': '안정화 완료',
        'phase': 'P3', 'type': 'PASS',
        'exit': ['7일간 Sev-0/Sev-1 0건', '변경 동결 기간 무사 통과'],
        'rollback': None,
    },
    {
        'id': 'M5', 'week': 10, 'date': '6/6 (W10)', 'title': '인덱스 삭제 완료',
        'phase': 'post', 'type': 'PASS',
        'exit': ['인덱스 6개 삭제 완료', 'INSERT TPS 3.4x+ 달성'],
        'rollback': '인덱스 재생성 (15~40분)',
    },
]

phase_segments = [
    ('P0: 설계 확정', 0.5, 1.5, 'P0'),
    ('P1: 개발', 1.5, 5.5, 'P1'),
    ('P2: Shadow 검증', 5.5, 7.5, 'P2'),
    ('P3: 전환/안정화', 7.5, 9.5, 'P3'),
    ('후속', 9.5, 10.5, 'post'),
]

# ── Build Chart ──
fig, ax = plt.subplots(figsize=(24, 11))
fig.set_facecolor(BG_COLOR)
ax.set_facecolor(BG_COLOR)

TIMELINE_Y = 0.48
ax.set_xlim(0.0, 11.5)
ax.set_ylim(-0.08, 1.08)

# ── Phase ribbon at top ──
ribbon_y = 0.95
ribbon_h = 0.06
for label, x_start, x_end, phase_id in phase_segments:
    color = PHASE_COLORS[phase_id]
    rect = FancyBboxPatch(
        (x_start, ribbon_y - ribbon_h / 2),
        x_end - x_start,
        ribbon_h,
        boxstyle="round,pad=0.04",
        facecolor=color, edgecolor='white', linewidth=2.5, alpha=0.88, zorder=3,
    )
    ax.add_patch(rect)
    mid_x = (x_start + x_end) / 2
    ax.text(mid_x, ribbon_y, label,
            ha='center', va='center', fontsize=11, fontweight='bold',
            color='white', zorder=4)

# ── Main timeline line ──
ax.plot([0.3, 11.2], [TIMELINE_Y, TIMELINE_Y],
        color='#BDC3C7', linewidth=5, solid_capstyle='round', zorder=1)

# ── Week tick marks ──
for w in range(1, 11):
    x = w + 0.5
    ax.plot([x, x], [TIMELINE_Y - 0.018, TIMELINE_Y + 0.018],
            color='#95A5A6', linewidth=1.5, zorder=2)
    ax.text(x, TIMELINE_Y - 0.032, f'W{w}',
            ha='center', va='top', fontsize=9.5, color=SUBTEXT_COLOR, zorder=3)

# ── Draw milestones ──
for i, ms in enumerate(milestones):
    x = ms['week'] + 0.5
    is_gate = ms['type'] == 'GATE'
    ms_color = MS_COLORS[ms['id']]

    # Diamond marker
    marker_size = 550 if is_gate else 400
    ax.scatter(x, TIMELINE_Y, marker='D', s=marker_size,
               color=ms_color, zorder=6,
               edgecolors='white', linewidth=3)

    # Milestone ID inside diamond
    ax.text(x, TIMELINE_Y, ms['id'],
            ha='center', va='center', fontsize=9, fontweight='bold',
            color='white', zorder=7)

    # Date label
    date_y = TIMELINE_Y - 0.055
    ax.text(x, date_y, ms['date'],
            ha='center', va='top', fontsize=10.5, fontweight='bold',
            color=ms_color, zorder=5)

    # Card positioning: alternate above/below
    if i % 2 == 0:
        card_y = 0.72
        va_align = 'bottom'
        line_y_start = TIMELINE_Y + 0.04
        line_y_end = card_y - 0.01
    else:
        card_y = 0.24
        va_align = 'top'
        line_y_start = TIMELINE_Y - 0.04
        line_y_end = card_y + 0.01

    # Connector line
    ax.plot([x, x], [line_y_start, line_y_end],
            color=ms_color, linewidth=2, linestyle='-', alpha=0.5, zorder=2)

    # Build card content
    gate_badge = '  [GATE Go/No-Go]' if is_gate else ''
    title_line = f'{ms["title"]}{gate_badge}'
    separator = '\u2500' * 24
    exit_items = '\n'.join([f'  \u2022 {c}' for c in ms['exit']])
    card_text = f'{title_line}\n{separator}\n{exit_items}'

    card_border_width = 2.5 if is_gate else 1.5

    ax.text(x, card_y, card_text,
            ha='center', va=va_align,
            fontsize=10, color=TEXT_COLOR,
            linespacing=1.6, zorder=5,
            bbox=dict(boxstyle='round,pad=0.55', facecolor='white',
                      edgecolor=ms_color, linewidth=card_border_width, alpha=0.97))

    # Rollback annotation
    if ms['rollback']:
        rb_y = TIMELINE_Y + 0.065 if i % 2 != 0 else TIMELINE_Y - 0.075
        rb_va = 'bottom' if i % 2 != 0 else 'top'
        ax.text(x, rb_y, f'Rollback: {ms["rollback"]}',
                ha='center', va=rb_va,
                fontsize=8, color='#C0392B', fontstyle='italic', zorder=5,
                bbox=dict(boxstyle='round,pad=0.25', facecolor='#FDEDEC',
                          edgecolor='#E74C3C', linewidth=0.8, alpha=0.92))

# ── Duration arrows between milestones ──
for i in range(len(milestones) - 1):
    x1 = milestones[i]['week'] + 0.5
    x2 = milestones[i + 1]['week'] + 0.5
    weeks_between = milestones[i + 1]['week'] - milestones[i]['week']
    mid_x = (x1 + x2) / 2
    arrow_y = TIMELINE_Y + 0.028
    ax.annotate('', xy=(x2 - 0.2, arrow_y),
                xytext=(x1 + 0.2, arrow_y),
                arrowprops=dict(arrowstyle='<->', color='#7F8C8D', lw=1.0), zorder=2)
    ax.text(mid_x, arrow_y + 0.012, f'{weeks_between}w',
            ha='center', va='bottom', fontsize=8.5, fontweight='bold',
            color='#7F8C8D', zorder=3)

# ── Title ──
ax.set_title('t_coupon_issue INSERT 부하 개선 — 마일스톤 & Exit Criteria',
             fontsize=20, fontweight='bold', pad=30, color=TEXT_COLOR, loc='left')

# ── Summary bar ──
ax.text(0.5, 1.01, '10 Weeks (4/1 ~ 6/6)   |   6 Milestones   |   1 GATE Decision   |   성공 기준: INSERT TPS 3.4x+',
        transform=ax.transAxes, ha='center', va='top',
        fontsize=12, fontweight='bold', color='#2C3E50',
        bbox=dict(boxstyle='round,pad=0.35', facecolor='#EBF5FB',
                  edgecolor='#3498DB', alpha=0.9))

# ── Legend ──
legend_elements = [
    Line2D([0], [0], marker='D', color='w', markerfacecolor='#E74C3C',
           markersize=14, markeredgecolor='white', markeredgewidth=1.5, label='GATE (Go/No-Go)'),
    Line2D([0], [0], marker='D', color='w', markerfacecolor='#E67E22',
           markersize=14, markeredgecolor='white', markeredgewidth=1.5, label='Milestone'),
    mpatches.Patch(facecolor='#FDEDEC', edgecolor='#E74C3C',
                   linewidth=0.8, label='Rollback Strategy'),
]
ax.legend(handles=legend_elements, loc='lower right', fontsize=11,
          framealpha=0.95, edgecolor='#BDC3C7', fancybox=True,
          bbox_to_anchor=(0.99, 0.01))

# ── Axes ──
for spine in ax.spines.values():
    spine.set_visible(False)
ax.set_xticks([])
ax.set_yticks([])

plt.tight_layout(pad=2.5)
plt.savefig('/tmp/final_milestone.svg', format='svg', bbox_inches='tight', dpi=150)
plt.close()
print("OK: /tmp/final_milestone.svg")
