import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import numpy as np

# ── Font & Global ──
plt.rcParams['font.family'] = 'Apple SD Gothic Neo'
plt.rcParams['svg.fonttype'] = 'none'
plt.rcParams['axes.unicode_minus'] = False

# ── Color System ──
C = {
    'bg': '#ffffff',
    'text1': '#111827',
    'text2': '#6b7280',
    'text3': '#9ca3af',
    'divider': '#e5e7eb',
    'divider_light': '#f3f4f6',
    'row_alt': '#f9fafb',
    'BE1': '#3b82f6',
    'BE2': '#1d4ed8',
    'DBA': '#f59e0b',
    'SRE': '#10b981',
    'QA': '#8b5cf6',
    'critical': '#ef4444',
    'accent': '#3b82f6',
}

ROLE_COLORS = {
    'BE-1': C['BE1'],
    'BE-2': C['BE2'],
    'DBA': C['DBA'],
    'SRE': C['SRE'],
    'QA': C['QA'],
}

# Phase background tints
PHASE_TINTS = {
    'P0 설계확정': '#eff6ff',     # blue-50
    'P1 개발': '#eef2ff',         # indigo-50
    'P2 Shadow검증': '#fffbeb',   # amber-50
    'P3 전환·안정화': '#ecfdf5',  # emerald-50
    '후속': '#f9fafb',            # gray-50
}

WEEK_LABELS = ['W1\n4/1', 'W2\n4/7', 'W3\n4/14', 'W4\n4/21', 'W5\n4/28',
               'W6\n5/5', 'W7\n5/12', 'W8\n5/19', 'W9\n5/26', 'W10\n6/2']

def w(n):
    """Convert week number to x position (W1=0)."""
    return n - 1

def text_width_est(text, fontsize=8.5):
    """CJK-aware text width estimation in data units."""
    total = 0
    for ch in text:
        if ord(ch) > 0x2E7F:
            total += 0.062
        else:
            total += 0.040
    return total * (fontsize / 8.5)

# ── Data ──
phases = [
    {
        'name': 'P0 설계확정',
        'weeks': 'W1',
        'md': 12,
        'tasks': [
            ('BE-1', '벤치마크·리뷰', 2, 1, 2, True),
            ('BE-2', '리뷰·구조확정', 2, 1, 2, False),
            ('DBA', '벤치마크·분석', 3, 1, 2, False),
            ('SRE', '정책·대시보드', 4, 1, 2, False),
            ('QA', '테스트계획', 1, 1, 1.5, False),
        ]
    },
    {
        'name': 'P1 개발',
        'weeks': 'W2-W5',
        'md': 55,
        'tasks': [
            ('BE-1', 'gate_keeper Lua', 5, 2, 4, True),
            ('BE-1', 'compensate·FF', 5, 4, 5.3, True),
            ('BE-1', 'Shadow준비', 4.5, 5.3, 6, False),
            ('BE-2', 'MC통합', 8, 2, 6, True),
            ('BE-2', '보상워커', 7, 2, 5, False),
            ('BE-2', 'Reconciliation', 6, 5, 6, False),
            ('BE-2', 'Shadow준비', 4.5, 5, 6, False),
            ('DBA', '인덱스사용처확인', 5, 2, 5, False),
            ('SRE', '대시보드구축', 6, 2, 5, False),
            ('QA', '케이스작성', 4, 4, 6, False),
        ]
    },
    {
        'name': 'P2 Shadow검증',
        'weeks': 'W6-W7',
        'md': 31,
        'tasks': [
            ('BE-1', 'Shadow운영', 4, 6, 8, True),
            ('BE-1', '부하테스트', 2, 7.5, 8, False),
            ('BE-2', 'Recon diff검증', 4, 6, 8, False),
            ('BE-2', '부하테스트', 2, 7.5, 8, False),
            ('DBA', '삭제/복구리허설', 4, 6, 8, False),
            ('SRE', '모니터링강화', 5, 6, 8, False),
            ('QA', '전수QA', 10, 6, 8, False),
        ]
    },
    {
        'name': 'P3 전환·안정화',
        'weeks': 'W8-W9',
        'md': 20,
        'tasks': [
            ('BE-1', 'MC 100%전환', 3, 8, 9, True),
            ('BE-2', '인덱스삭제지원', 3, 8, 9, False),
            ('DBA', '삭제·모니터링', 5, 8, 10, False),
            ('SRE', '7일안정화', 5, 8, 10, False),
            ('QA', '회귀테스트', 4, 8, 9, False),
        ]
    },
    {
        'name': '후속',
        'weeks': 'W10',
        'md': 0,
        'tasks': [
            ('DBA', '인덱스6개삭제', 0, 10, 11, True),
        ]
    },
]

milestones = [
    ('M0', 'Go/No-Go', 1, True),
    ('M1', '개발완료', 5, False),
    ('M2', '검증완료', 7, False),
    ('M3', '전환완료', 8, False),
    ('M4', '안정화완료', 9, False),
    ('M5', '삭제완료', 10, False),
]

critical_tasks = {'벤치마크·리뷰', 'gate_keeper Lua', 'compensate·FF', 'MC통합',
                  'Shadow운영', 'MC 100%전환', '인덱스6개삭제'}

# ── Build row layout ──
def build_rows(phases):
    rows = []
    role_order = ['BE-1', 'BE-2', 'DBA', 'SRE', 'QA']
    for phase in phases:
        role_tasks = {}
        for t in phase['tasks']:
            role_tasks.setdefault(t[0], []).append(t)

        phase_row_start = len(rows)
        for role in role_order:
            if role not in role_tasks:
                continue
            tasks = role_tasks[role]
            sub_rows = []
            for t in sorted(tasks, key=lambda x: x[3]):
                placed = False
                for sr in sub_rows:
                    if all(t[3] >= existing[4] or t[4] <= existing[3] for existing in sr):
                        sr.append(t)
                        placed = True
                        break
                if not placed:
                    sub_rows.append([t])

            for i, sr in enumerate(sub_rows):
                rows.append({
                    'role': role,
                    'role_label': role if i == 0 else '',
                    'tasks': sr,
                    'phase_name': phase['name'],
                })

        if len(rows) > phase_row_start:
            rows[phase_row_start]['phase_start'] = True
            rows[phase_row_start]['phase_data'] = phase

    return rows

all_rows = build_rows(phases)
n_rows = len(all_rows)

# ── Figure ──
fig, ax = plt.subplots(figsize=(24, 16))
fig.set_facecolor(C['bg'])
ax.set_facecolor(C['bg'])

# Layout
HEADER_Y = 2.0          # y of header baseline
ROW_H = 0.68
BAR_H = 0.48
LEFT_COL_W = 1.6        # width for role labels
CHART_LEFT = 0          # x=0 is W1 start
CHART_RIGHT = 10.0      # x=10 is W10 end

ax.set_xlim(-LEFT_COL_W - 0.5, CHART_RIGHT + 2.0)
bottom_y = HEADER_Y - 0.8 - n_rows * ROW_H - 0.8
ax.set_ylim(bottom_y, HEADER_Y + 1.8)
ax.axis('off')

# ── Title ──
ax.text(-LEFT_COL_W, HEADER_Y + 1.4,
        't_coupon_issue INSERT 부하 개선',
        fontsize=22, fontweight='bold', color=C['text1'],
        va='bottom', ha='left')
ax.text(-LEFT_COL_W, HEADER_Y + 1.05,
        'Implementation Gantt Chart',
        fontsize=13, color=C['text2'], va='bottom', ha='left')

total_md = sum(p['md'] for p in phases)
ax.text(CHART_RIGHT + 1.3, HEADER_Y + 1.4,
        f'Total {total_md} MD',
        fontsize=14, fontweight='bold', color=C['text1'],
        va='bottom', ha='right')
ax.text(CHART_RIGHT + 1.3, HEADER_Y + 1.05,
        '10 Weeks  /  5 Roles',
        fontsize=11, color=C['text2'], va='bottom', ha='right')

# ── Week column headers ──
for i, label in enumerate(WEEK_LABELS):
    x = i
    # Alternating column shading (very subtle, full height)
    if i % 2 == 0:
        ax.fill_between([x, x + 1],
                        HEADER_Y + 0.6, bottom_y + 0.5,
                        color=C['divider_light'], alpha=0.5, zorder=0)
    ax.text(x + 0.5, HEADER_Y + 0.25, label,
            fontsize=9, color=C['text2'], ha='center', va='center',
            fontweight='medium', linespacing=1.3)

# Header bottom border
ax.plot([-0.05, 10.05], [HEADER_Y - 0.05, HEADER_Y - 0.05],
        color=C['divider'], linewidth=1.2, zorder=2)

# ── Milestone diamonds at header ──
for m_name, m_label, m_week, is_gate in milestones:
    x = w(m_week) + 0.5
    color = C['critical'] if is_gate else C['accent']
    diamond_y = HEADER_Y + 0.7
    ax.plot(x, diamond_y, marker='D', markersize=7, color=color,
            markeredgecolor='white', markeredgewidth=1.5, zorder=5)
    ax.text(x, diamond_y + 0.22, m_name,
            fontsize=7.5, color=color, ha='center', va='bottom',
            fontweight='bold')
    # Subtle vertical line through entire chart
    ax.plot([x, x], [HEADER_Y - 0.05, bottom_y + 0.5],
            color=color, alpha=0.10, linestyle='--', linewidth=0.8, zorder=0)

# ── Draw rows ──
for idx, row in enumerate(all_rows):
    y_center = HEADER_Y - 0.5 - idx * ROW_H
    y_top = y_center + ROW_H / 2
    y_bottom = y_center - ROW_H / 2

    # Phase separator
    if row.get('phase_start'):
        pd = row['phase_data']
        sep_y = y_top + 0.15
        # Phase separator line
        ax.plot([-LEFT_COL_W - 0.1, CHART_RIGHT + 1.3], [sep_y, sep_y],
                color=C['divider'], linewidth=0.7, zorder=1)
        # Phase name
        ax.text(-LEFT_COL_W, sep_y + 0.04,
                pd['name'],
                fontsize=10.5, fontweight='bold', color=C['text1'],
                va='bottom', ha='left')
        # MD badge
        if pd['md'] > 0:
            md_x = -LEFT_COL_W + sum(0.11 if ord(c) > 0x2E7F else 0.07 for c in pd['name']) + 0.65
            ax.text(md_x, sep_y + 0.04,
                    f"{pd['md']} MD",
                    fontsize=8.5, color=C['text3'],
                    va='bottom', ha='left')

    # Alternating row bg
    if idx % 2 == 1:
        ax.fill_between([-0.05, 10.05], y_top - 0.02, y_bottom + 0.02,
                        color=C['row_alt'], alpha=0.4, zorder=0)

    # Role label
    if row['role_label']:
        role = row['role']
        ax.text(-0.15, y_center,
                row['role_label'],
                fontsize=9.5, fontweight='bold',
                color=ROLE_COLORS.get(role, C['text2']),
                va='center', ha='right')

    # Task bars - sorted for collision detection
    sorted_tasks = sorted(row['tasks'], key=lambda t: t[3])
    for ti, task in enumerate(sorted_tasks):
        role, name, md, start, end, _ = task
        x_bar = w(start)
        bar_width = end - start
        color = ROLE_COLORS.get(role, C['accent'])
        is_crit = name in critical_tasks

        # Rounded bar
        fancy = FancyBboxPatch(
            (x_bar, y_center - BAR_H / 2),
            bar_width, BAR_H,
            boxstyle="round,pad=0,rounding_size=0.07",
            facecolor=color, edgecolor='none', alpha=0.85, zorder=3
        )
        ax.add_patch(fancy)

        # Build label
        md_str = ''
        if md > 0:
            md_val = int(md) if md == int(md) else md
            md_str = f' ({md_val})'

        full_label = name + md_str
        text_est = text_width_est(full_label, 8.5)

        if bar_width >= text_est + 0.15:
            # ── Text INSIDE bar ──
            tx = x_bar + bar_width / 2
            if is_crit:
                dot_offset = text_est / 2 + 0.12
                ax.text(tx - dot_offset, y_center, '\u25CF',
                        fontsize=5, color=C['critical'],
                        va='center', ha='center', zorder=4)
            ax.text(tx, y_center, full_label,
                    fontsize=8.5, color='white', va='center', ha='center',
                    fontweight='medium', zorder=4)
        else:
            # ── Text OUTSIDE bar (right) with collision detection ──
            tx = x_bar + bar_width + 0.08
            crit_offset = 0.12 if is_crit else 0

            # Available space before next bar
            if ti + 1 < len(sorted_tasks):
                next_start = w(sorted_tasks[ti + 1][3])
                avail = next_start - tx - crit_offset - 0.08
            else:
                avail = CHART_RIGHT + 1.5 - tx - crit_offset

            display_label = full_label
            label_w = text_width_est(full_label, 8)
            if label_w > avail > 0.25:
                for cut in range(len(full_label), 0, -1):
                    candidate = full_label[:cut] + '..'
                    if text_width_est(candidate, 8) <= avail:
                        display_label = candidate
                        break
            elif avail <= 0.25:
                display_label = ''

            if display_label:
                if is_crit:
                    ax.text(tx, y_center, '\u25CF',
                            fontsize=5, color=C['critical'],
                            va='center', ha='left', zorder=4)
                    tx += crit_offset
                ax.text(tx, y_center, display_label,
                        fontsize=8, color=C['text1'], va='center', ha='left',
                        zorder=4,
                        bbox=dict(boxstyle='round,pad=0.04', facecolor='white',
                                  edgecolor='none', alpha=0.85))

# ── Legend bar ──
leg_y = bottom_y + 0.15
leg_x = -LEFT_COL_W

# Thin separator
ax.plot([-LEFT_COL_W - 0.1, CHART_RIGHT + 1.3], [leg_y + 0.35, leg_y + 0.35],
        color=C['divider'], linewidth=0.7, zorder=1)

spacing = 1.5
for i, (role, color) in enumerate(ROLE_COLORS.items()):
    x_pos = leg_x + i * spacing
    # Small rounded rect
    r = FancyBboxPatch((x_pos, leg_y - 0.06), 0.28, 0.16,
                       boxstyle="round,pad=0,rounding_size=0.04",
                       facecolor=color, edgecolor='none', alpha=0.85, zorder=3)
    ax.add_patch(r)
    ax.text(x_pos + 0.36, leg_y + 0.02, role,
            fontsize=9, color=C['text1'], va='center')

# Critical path
cp_x = leg_x + 5 * spacing + 0.3
ax.text(cp_x, leg_y + 0.02, '\u25CF', fontsize=6, color=C['critical'],
        va='center', ha='left')
ax.text(cp_x + 0.14, leg_y + 0.02, 'Critical Path',
        fontsize=9, color=C['text1'], va='center')

# Milestone
ml_x = cp_x + 1.6
ax.plot(ml_x + 0.06, leg_y + 0.02, 'D', markersize=6,
        color=C['accent'], markeredgecolor='white', markeredgewidth=1)
ax.text(ml_x + 0.22, leg_y + 0.02, 'Milestone',
        fontsize=9, color=C['text1'], va='center')

# Gate
gl_x = ml_x + 1.4
ax.plot(gl_x + 0.06, leg_y + 0.02, 'D', markersize=6,
        color=C['critical'], markeredgecolor='white', markeredgewidth=1)
ax.text(gl_x + 0.22, leg_y + 0.02, 'GATE',
        fontsize=9, color=C['text1'], va='center')

plt.savefig('/tmp/agent_c_gantt.svg', format='svg', bbox_inches='tight',
            facecolor=C['bg'], edgecolor='none', dpi=150)
plt.close()
print("OK: /tmp/agent_c_gantt.svg")
