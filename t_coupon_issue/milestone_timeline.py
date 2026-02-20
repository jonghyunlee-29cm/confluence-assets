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
    'surface': '#fafafa',
    'text1': '#111827',
    'text2': '#6b7280',
    'text3': '#9ca3af',
    'border': '#e5e7eb',
    'divider': '#f3f4f6',
    'accent': '#3b82f6',
    'accent_light': '#eff6ff',
    'critical': '#ef4444',
    'critical_light': '#fef2f2',
}

PHASE_SEGS = [
    ('P0 설계확정',    1, 2,  '#3b82f6', 0.20),
    ('P1 개발',        2, 6,  '#1d4ed8', 0.15),
    ('P2 Shadow검증',  6, 8,  '#f59e0b', 0.20),
    ('P3 전환\xb7안정화', 8, 10, '#10b981', 0.20),
    ('후속',           10, 11, '#9ca3af', 0.15),
]

milestones = [
    {
        'id': 'M0', 'name': '설계확정', 'week': 1, 'date': '4/4',
        'is_gate': True, 'gate_label': 'GATE Go/No-Go',
        'exit': ['프로덕션 벤치마크 3.0x+ 달성', '설계 리뷰 완료'],
        'rollback': None,
    },
    {
        'id': 'M1', 'name': '개발완료', 'week': 5, 'date': '5/2',
        'is_gate': False, 'gate_label': None,
        'exit': ['단위 테스트 통과', 'Feature Flag 동작', 'Shadow Mode 배포 가능'],
        'rollback': 'FF OFF -> DB 즉시 전환 (<1분)',
    },
    {
        'id': 'M2', 'name': '검증완료', 'week': 7, 'date': '5/16',
        'is_gate': False, 'gate_label': None,
        'exit': ['Shadow Mode 1주+ 무장애', 'TPS 3.4x+ 달성', 'QA 전수 통과'],
        'rollback': 'Lua script 이전 버전 배포 (<5분)',
    },
    {
        'id': 'M3', 'name': 'MC 전환완료', 'week': 8, 'date': '5/23',
        'is_gate': False, 'gate_label': None,
        'exit': ['MC 100% + 48h 안정화', 'drift < 0.01%'],
        'rollback': 'Redis MC: FF -> DB 전환 (<1분)',
    },
    {
        'id': 'M4', 'name': '안정화완료', 'week': 9, 'date': '5/30',
        'is_gate': False, 'gate_label': None,
        'exit': ['7일간 Sev-0/Sev-1 0건', '변경 동결 기간 무사 통과'],
        'rollback': None,
    },
    {
        'id': 'M5', 'name': '인덱스삭제완료', 'week': 10, 'date': '6/6',
        'is_gate': False, 'gate_label': None,
        'exit': ['인덱스 6개 삭제 완료', 'INSERT TPS 3.4x+ 달성'],
        'rollback': '인덱스 재생성 (15~40분)',
    },
]

# ── Figure ──
fig, ax = plt.subplots(figsize=(24, 10))
fig.set_facecolor(C['bg'])
ax.set_facecolor(C['bg'])
ax.axis('off')

# Coordinate system
# x: week 1..10 mapped to 1..10
# y: timeline at y=5, cards above (y>5) and below (y<5)
TL_Y = 5.0  # timeline y
PHASE_Y = TL_Y + 0.55  # phase bar y

ax.set_xlim(-0.5, 12.5)
ax.set_ylim(0.0, 10.0)

def wx(week):
    return float(week)

# ── Title ──
ax.text(0.3, 9.5,
        't_coupon_issue INSERT 부하 개선',
        fontsize=22, fontweight='bold', color=C['text1'],
        va='bottom', ha='left')
ax.text(0.3, 9.15,
        'Milestone Timeline',
        fontsize=13, color=C['text2'], va='bottom', ha='left')

ax.text(11.7, 9.5,
        '6 Milestones  /  10 Weeks  /  1 GATE',
        fontsize=11, color=C['text2'], va='bottom', ha='right')

# ── Phase bar ──
bar_h = 0.14
for name, start, end, color, alpha in PHASE_SEGS:
    xs, xe = wx(start), wx(end)
    r = FancyBboxPatch(
        (xs, PHASE_Y - bar_h/2), xe - xs, bar_h,
        boxstyle="round,pad=0,rounding_size=0.04",
        facecolor=color, alpha=alpha, edgecolor='none', zorder=2
    )
    ax.add_patch(r)
    ax.text((xs + xe) / 2, PHASE_Y + 0.2, name,
            fontsize=7.5, color=C['text2'], ha='center', va='bottom',
            fontweight='medium')

# ── Timeline ──
ax.plot([wx(0.5), wx(11.0)], [TL_Y, TL_Y],
        color=C['border'], linewidth=2.5, zorder=1, solid_capstyle='round')

# Week tick marks & labels
for wk in range(1, 11):
    x = wx(wk)
    ax.plot([x, x], [TL_Y - 0.06, TL_Y + 0.06],
            color=C['border'], linewidth=1, zorder=2)
    ax.text(x, TL_Y - 0.22, f'W{wk}',
            fontsize=8, color=C['text3'], ha='center', va='top')

# ── Duration labels between milestones ──
for i in range(len(milestones) - 1):
    m1, m2 = milestones[i], milestones[i + 1]
    x1, x2 = wx(m1['week']), wx(m2['week'])
    dur = m2['week'] - m1['week']
    ax.text((x1 + x2) / 2, TL_Y + 0.22, f'{dur}w',
            fontsize=8, color=C['text3'], ha='center', va='bottom',
            fontweight='medium',
            bbox=dict(boxstyle='round,pad=0.12', facecolor='white',
                      edgecolor='none', alpha=0.9))

# ── Cards: define positions carefully to avoid overlap ──
# Card layout: specify (card_center_x, is_above) for each milestone
# We manually tune x offsets to prevent overlap
card_specs = [
    # M0: above, at week 1
    {'cx': 1.0, 'above': True},
    # M1: below, at week 5
    {'cx': 5.0, 'above': False},
    # M2: above, at week 7
    {'cx': 6.5, 'above': True},
    # M3: below, at week 8
    {'cx': 8.5, 'above': False},
    # M4: above, at week 9
    {'cx': 9.5, 'above': True},
    # M5: below, at week 10.5
    {'cx': 10.8, 'above': False},
]

CARD_W = 2.2

for i, m in enumerate(milestones):
    spec = card_specs[i]
    node_x = wx(m['week'])
    is_gate = m['is_gate']
    is_above = spec['above']
    card_cx = spec['cx']

    # ── Node on timeline ──
    node_size = 18 if is_gate else 15
    node_color = C['critical'] if is_gate else C['accent']
    ax.plot(node_x, TL_Y, 'o', markersize=node_size,
            color=node_color, markeredgecolor='white',
            markeredgewidth=2.5, zorder=5)
    ax.text(node_x, TL_Y, m['id'],
            fontsize=7.5 if is_gate else 7, color='white',
            ha='center', va='center', fontweight='bold', zorder=6)

    # Date below node
    ax.text(node_x, TL_Y - 0.42, m['date'],
            fontsize=9, color=node_color, ha='center', va='top',
            fontweight='bold')

    # ── Card dimensions ──
    n_exit = len(m['exit'])
    has_rb = m['rollback'] is not None
    has_gate = m['gate_label'] is not None
    line_h = 0.21
    card_h = 0.25 + (1 if has_gate else 0) * 0.20 + 0.22 + n_exit * line_h + (0.25 if has_rb else 0) + 0.12

    card_left = card_cx - CARD_W / 2
    # Clamp to visible area
    if card_left < 0.0:
        card_left = 0.0
    if card_left + CARD_W > 12.3:
        card_left = 12.3 - CARD_W

    if is_above:
        card_bottom = TL_Y + 0.75
        card_top = card_bottom + card_h
    else:
        card_top = TL_Y - 0.75
        card_bottom = card_top - card_h

    # ── Connector line ──
    conn_top = TL_Y + 0.25 if is_above else TL_Y - 0.25
    conn_bot = card_bottom if is_above else card_top
    # Angled connector from node to card center
    ax.plot([node_x, card_cx], [conn_top, conn_bot],
            color=C['border'], linewidth=1, zorder=1)

    # ── Card background ──
    border_c = C['critical'] if is_gate else C['border']
    bg_c = C['critical_light'] if is_gate else C['surface']

    card_y_min = min(card_bottom, card_top)
    card_rect = FancyBboxPatch(
        (card_left, card_y_min), CARD_W, card_h,
        boxstyle="round,pad=0.02,rounding_size=0.06",
        facecolor=bg_c, edgecolor=border_c,
        linewidth=1.2 if is_gate else 0.8,
        zorder=3
    )
    ax.add_patch(card_rect)

    # ── Card content ──
    tx = card_left + 0.12
    if is_above:
        ty = card_top - 0.18
    else:
        ty = card_top - 0.18

    # Title
    title_c = C['critical'] if is_gate else C['text1']
    ax.text(tx, ty, f"{m['id']}: {m['name']}",
            fontsize=9.5, fontweight='bold', color=title_c,
            va='top', ha='left', zorder=4)
    ty -= 0.22

    # Gate sub-label
    if has_gate:
        ax.text(tx, ty, m['gate_label'],
                fontsize=7.5, color=C['critical'], fontweight='medium',
                va='top', ha='left', zorder=4, fontstyle='italic')
        ty -= 0.22

    # Exit criteria header
    ax.text(tx, ty, 'Exit Criteria:',
            fontsize=7, color=C['text3'], va='top', ha='left',
            fontweight='bold', zorder=4)
    ty -= 0.2

    # Exit items
    for item in m['exit']:
        disp = item if len(item) <= 26 else item[:24] + '...'
        ax.text(tx + 0.08, ty, f'\u2022  {disp}',
                fontsize=7.5, color=C['text2'], va='top', ha='left',
                zorder=4)
        ty -= line_h

    # Rollback
    if has_rb:
        ty -= 0.06
        rb = m['rollback']
        if len(rb) > 30:
            rb = rb[:28] + '...'
        ax.text(tx, ty, f'Rollback: {rb}',
                fontsize=7, color=C['critical'], va='top', ha='left',
                fontstyle='italic', zorder=4)

# ── Legend ──
leg_y = 0.45
ax.plot(1.0, leg_y, 'o', markersize=10, color=C['critical'],
        markeredgecolor='white', markeredgewidth=2)
ax.text(1.3, leg_y, 'GATE Milestone', fontsize=9, color=C['text1'],
        va='center')

ax.plot(3.2, leg_y, 'o', markersize=10, color=C['accent'],
        markeredgecolor='white', markeredgewidth=2)
ax.text(3.5, leg_y, 'Milestone', fontsize=9, color=C['text1'],
        va='center')

ax.text(5.0, leg_y, 'Rollback:',
        fontsize=8, color=C['critical'], va='center', fontstyle='italic')
ax.text(5.65, leg_y, 'Rollback plan available',
        fontsize=9, color=C['text1'], va='center')

plt.savefig('/tmp/agent_c_milestone.svg', format='svg', bbox_inches='tight',
            facecolor=C['bg'], edgecolor='none', dpi=150)
plt.close()
print("OK: /tmp/agent_c_milestone.svg")
