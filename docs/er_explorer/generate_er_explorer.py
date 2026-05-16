from __future__ import annotations

import html
import json
import math
import re
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "docs" / "db_er_diagram.mmd"
OUT_DIR = ROOT / "docs" / "er_explorer"
APP_DIR = OUT_DIR / "apps"
NEIGHBORHOOD_DIR = OUT_DIR / "neighborhoods"


FIELD_FONT = 12
TITLE_FONT = 15
HEADER_H = 34
ROW_H = 18
CARD_PAD_X = 14
CARD_PAD_Y = 12
MIN_CARD_W = 260
MAX_FULL_FIELDS = 80
MAX_COMPACT_FIELDS = 8


PALETTE = [
    ("#2563eb", "#eff6ff", "#dbeafe"),
    ("#059669", "#ecfdf5", "#d1fae5"),
    ("#d97706", "#fffbeb", "#fef3c7"),
    ("#dc2626", "#fef2f2", "#fee2e2"),
    ("#7c3aed", "#f5f3ff", "#ede9fe"),
    ("#0891b2", "#ecfeff", "#cffafe"),
    ("#4f46e5", "#eef2ff", "#e0e7ff"),
    ("#0f766e", "#f0fdfa", "#ccfbf1"),
    ("#be123c", "#fff1f2", "#ffe4e6"),
    ("#475569", "#f8fafc", "#e2e8f0"),
]


def stable_index(value: str, modulo: int) -> int:
    total = 0
    for index, char in enumerate(value):
        total += (index + 1) * ord(char)
    return total % modulo


def slug(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", value)


def parse_mermaid(source: str) -> tuple[dict[str, dict], list[dict]]:
    lines = source.splitlines()
    tables: dict[str, dict] = {}
    entity_re = re.compile(r"^\s*([A-Za-z_][\w]*)\s*\{\s*$")
    relation_re = re.compile(
        r"^\s*([A-Za-z_][\w]*)\s+([|o{}]+)--([|o{}]+)\s+([A-Za-z_][\w]*)\s*:\s*(.+?)\s*$"
    )

    index = 0
    while index < len(lines):
        match = entity_re.match(lines[index])
        if not match:
            index += 1
            continue

        table_name = match.group(1)
        fields = []
        index += 1
        while index < len(lines) and lines[index].strip() != "}":
            raw = lines[index].strip()
            if raw:
                pieces = raw.split()
                field_type = pieces[0] if pieces else ""
                field_name = pieces[1] if len(pieces) > 1 else raw
                rest = " ".join(pieces[2:])
                tags = [tag for tag in ("PK", "FK", "UK") if re.search(rf"\b{tag}\b", rest)]
                notes = re.findall(r'"([^"]+)"', rest)
                fields.append(
                    {
                        "name": field_name,
                        "type": field_type,
                        "tags": tags,
                        "notes": notes,
                    }
                )
            index += 1

        tables[table_name] = {"name": table_name, "fields": fields}
        index += 1

    relationships = []
    for line in lines:
        match = relation_re.match(line)
        if not match:
            continue

        src, left_cardinality, right_cardinality, dst, label = match.groups()
        label = label.strip()
        if label.startswith('"') and label.endswith('"'):
            label = label[1:-1]
        relationships.append(
            {
                "src": src,
                "dst": dst,
                "left": left_cardinality,
                "right": right_cardinality,
                "label": label,
            }
        )
        tables.setdefault(src, {"name": src, "fields": []})
        tables.setdefault(dst, {"name": dst, "fields": []})

    return tables, relationships


def discover_apps(tables: dict[str, dict]) -> list[str]:
    repo_apps = {
        child.name
        for child in ROOT.iterdir()
        if child.is_dir()
        and not child.name.startswith(".")
        and child.name
        not in {
            "__pycache__",
            "docs",
            "media",
        }
    }
    repo_apps.update(
        {
            "auth",
            "database_connections",
            "django",
            "django_apscheduler",
            "token_blacklist",
            "inventory",
            "production_planning",
        }
    )
    table_prefixes = {table.split("_", 1)[0] for table in tables}
    repo_apps.update(table_prefixes)
    return sorted(repo_apps, key=len, reverse=True)


def app_for(table: str, apps: list[str]) -> str:
    for app in apps:
        if table == app or table.startswith(f"{app}_"):
            return app
    return table.split("_", 1)[0]


def color_for(app: str) -> tuple[str, str, str]:
    return PALETTE[stable_index(app, len(PALETTE))]


def escape(value: object) -> str:
    return html.escape(str(value), quote=True)


def field_line(field: dict) -> str:
    tag = "/".join(field["tags"]) if field["tags"] else ""
    notes = f" ({', '.join(field['notes'])})" if field["notes"] else ""
    return f"{tag:<5} {field['name']} : {field['type']}{notes}".rstrip()


def display_fields(table: dict, compact: bool) -> list[str]:
    fields = table["fields"]
    if not fields:
        return ["(no fields listed)"]
    limit = MAX_COMPACT_FIELDS if compact else MAX_FULL_FIELDS
    rows = [field_line(field) for field in fields[:limit]]
    if len(fields) > limit:
        rows.append(f"... {len(fields) - limit} more fields")
    return rows


def card_size(table: dict, compact: bool) -> tuple[int, int]:
    rows = display_fields(table, compact)
    longest = max([len(table["name"])] + [len(row) for row in rows])
    width = max(MIN_CARD_W if compact else 320, int(longest * 7.0 + CARD_PAD_X * 2))
    height = HEADER_H + CARD_PAD_Y * 2 + ROW_H * len(rows)
    return width, height


def total_stack_height(names: list[str], sizes: dict[str, tuple[int, int]], gap: int) -> int:
    return sum(sizes[name][1] for name in names) + gap * max(0, len(names) - 1)


def stack_columns(
    names: list[str],
    sizes: dict[str, tuple[int, int]],
    start_x: int,
    start_y: int,
    target_height: int,
    gap_x: int = 54,
    gap_y: int = 34,
) -> tuple[dict[str, tuple[int, int]], int, int]:
    positions: dict[str, tuple[int, int]] = {}
    x = start_x
    y = start_y
    column_width = 0
    max_bottom = start_y
    used_width = 0

    for name in names:
        width, height = sizes[name]
        if y > start_y and y + height - start_y > target_height:
            x += column_width + gap_x
            used_width += column_width + gap_x
            y = start_y
            column_width = 0
        positions[name] = (x, y)
        y += height + gap_y
        column_width = max(column_width, width)
        max_bottom = max(max_bottom, y - gap_y)

    used_width += column_width
    return positions, used_width, max_bottom - start_y


def boundary_point(a: tuple[int, int, int, int], b: tuple[int, int, int, int]) -> tuple[float, float]:
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    acx = ax + aw / 2
    acy = ay + ah / 2
    bcx = bx + bw / 2
    bcy = by + bh / 2
    dx = bcx - acx
    dy = bcy - acy
    if dx == 0 and dy == 0:
        return acx, acy
    scale_x = (aw / 2) / abs(dx) if dx else float("inf")
    scale_y = (ah / 2) / abs(dy) if dy else float("inf")
    scale = min(scale_x, scale_y)
    return acx + dx * scale, acy + dy * scale


def center(rect: tuple[int, int, int, int]) -> tuple[float, float]:
    x, y, width, height = rect
    return x + width / 2, y + height / 2


def choose_sides(
    src_rect: tuple[int, int, int, int],
    dst_rect: tuple[int, int, int, int],
) -> tuple[str, str]:
    src_x, src_y = center(src_rect)
    dst_x, dst_y = center(dst_rect)
    dx = dst_x - src_x
    dy = dst_y - src_y
    if abs(dx) > max(80, abs(dy) * 0.45):
        return ("right", "left") if dx >= 0 else ("left", "right")
    return ("bottom", "top") if dy >= 0 else ("top", "bottom")


def port_point(
    rect: tuple[int, int, int, int],
    side: str,
    slot: int,
    total: int,
    margin: int = 18,
    lane_step: int = 6,
) -> tuple[tuple[int, int], tuple[int, int]]:
    x, y, width, height = rect
    ratio = (slot + 1) / (total + 1)
    if side == "right":
        py = round(y + height * ratio)
        return (x + width, py), (x + width + margin + slot * lane_step, py)
    if side == "left":
        py = round(y + height * ratio)
        return (x, py), (x - margin - slot * lane_step, py)
    if side == "bottom":
        px = round(x + width * ratio)
        return (px, y + height), (px, y + height + margin)
    px = round(x + width * ratio)
    return (px, y), (px, y - margin)


def segment_hits_rect(
    point_a: tuple[int, int],
    point_b: tuple[int, int],
    rect: tuple[int, int, int, int],
) -> bool:
    ax, ay = point_a
    bx, by = point_b
    left, top, right, bottom = rect
    if ax == bx:
        y1, y2 = sorted((ay, by))
        return left < ax < right and max(y1, top) < min(y2, bottom)
    if ay == by:
        x1, x2 = sorted((ax, bx))
        return top < ay < bottom and max(x1, left) < min(x2, right)
    return False


def simplify_points(points: list[tuple[int, int]]) -> list[tuple[int, int]]:
    compact = []
    for point in points:
        if not compact or compact[-1] != point:
            compact.append(point)
    if len(compact) <= 2:
        return compact
    simplified = [compact[0]]
    for index in range(1, len(compact) - 1):
        prev_x, prev_y = simplified[-1]
        cur_x, cur_y = compact[index]
        next_x, next_y = compact[index + 1]
        if (prev_x == cur_x == next_x) or (prev_y == cur_y == next_y):
            continue
        simplified.append(compact[index])
    simplified.append(compact[-1])
    return simplified


def fallback_route(
    visual_start: tuple[int, int],
    outer_start: tuple[int, int],
    outer_end: tuple[int, int],
    visual_end: tuple[int, int],
) -> list[tuple[int, int]]:
    sx, sy = outer_start
    ex, ey = outer_end
    if abs(ex - sx) >= abs(ey - sy):
        mid = round((sx + ex) / 2)
        points = [visual_start, outer_start, (mid, sy), (mid, ey), outer_end, visual_end]
    else:
        mid = round((sy + ey) / 2)
        points = [visual_start, outer_start, (sx, mid), (ex, mid), outer_end, visual_end]
    return simplify_points(points)


def segment_key(point_a: tuple[int, int], point_b: tuple[int, int]) -> tuple[tuple[int, int], tuple[int, int]]:
    return (point_a, point_b) if point_a <= point_b else (point_b, point_a)


def overlap_length(start_a: int, end_a: int, start_b: int, end_b: int) -> int:
    a1, a2 = sorted((start_a, end_a))
    b1, b2 = sorted((start_b, end_b))
    return max(0, min(a2, b2) - max(a1, b1))


def occupied_segment_penalty(
    point_a: tuple[int, int],
    point_b: tuple[int, int],
    horizontal_spans: dict[int, list[tuple[int, int]]],
    vertical_spans: dict[int, list[tuple[int, int]]],
    lane_counts: Counter[tuple[str, int]],
) -> int:
    ax, ay = point_a
    bx, by = point_b
    if ax == bx:
        overlap = sum(overlap_length(ay, by, start, end) for start, end in vertical_spans.get(ax, []))
        return (6000 if overlap else 0) + overlap * 120 + lane_counts[("v", ax)] * 220
    if ay == by:
        overlap = sum(overlap_length(ax, bx, start, end) for start, end in horizontal_spans.get(ay, []))
        return (6000 if overlap else 0) + overlap * 120 + lane_counts[("h", ay)] * 220
    return 0


def segment_overlaps_occupied(
    point_a: tuple[int, int],
    point_b: tuple[int, int],
    horizontal_spans: dict[int, list[tuple[int, int]]],
    vertical_spans: dict[int, list[tuple[int, int]]],
) -> bool:
    ax, ay = point_a
    bx, by = point_b
    if ax == bx:
        return any(overlap_length(ay, by, start, end) > 0 for start, end in vertical_spans.get(ax, []))
    if ay == by:
        return any(overlap_length(ax, bx, start, end) > 0 for start, end in horizontal_spans.get(ay, []))
    return False


def record_route_usage(
    points: list[tuple[int, int]],
    horizontal_spans: dict[int, list[tuple[int, int]]],
    vertical_spans: dict[int, list[tuple[int, int]]],
    lane_counts: Counter[tuple[str, int]],
) -> None:
    used_lanes: set[tuple[str, int]] = set()
    seen_segments: set[tuple[tuple[int, int], tuple[int, int]]] = set()
    for point_a, point_b in zip(points, points[1:]):
        if point_a == point_b:
            continue
        key = segment_key(point_a, point_b)
        if key in seen_segments:
            continue
        seen_segments.add(key)
        ax, ay = point_a
        bx, by = point_b
        if ax == bx:
            vertical_spans[ax].append(tuple(sorted((ay, by))))
            used_lanes.add(("v", ax))
        elif ay == by:
            horizontal_spans[ay].append(tuple(sorted((ax, bx))))
            used_lanes.add(("h", ay))
    for lane in used_lanes:
        lane_counts[lane] += 1


def find_orthogonal_route(
    visual_start: tuple[int, int],
    outer_start: tuple[int, int],
    outer_end: tuple[int, int],
    visual_end: tuple[int, int],
    obstacles: list[tuple[int, int, int, int]],
    canvas_width: int,
    canvas_height: int,
    horizontal_spans: dict[int, list[tuple[int, int]]],
    vertical_spans: dict[int, list[tuple[int, int]]],
    lane_counts: Counter[tuple[str, int]],
    block_occupied: bool = True,
) -> list[tuple[int, int]]:
    import heapq

    xs = {max(10, min(canvas_width - 10, outer_start[0])), max(10, min(canvas_width - 10, outer_end[0])), 24, canvas_width - 24}
    ys = {max(10, min(canvas_height - 10, outer_start[1])), max(10, min(canvas_height - 10, outer_end[1])), 24, canvas_height - 24}
    xs.update(range(24, max(25, canvas_width - 23), 46))
    ys.update(range(24, max(25, canvas_height - 23), 36))
    for left, top, right, bottom in obstacles:
        xs.update((max(10, left), min(canvas_width - 10, right)))
        ys.update((max(10, top), min(canvas_height - 10, bottom)))

    xs = sorted(int(x) for x in xs)
    ys = sorted(int(y) for y in ys)
    start = (xs.index(int(outer_start[0])), ys.index(int(outer_start[1])))
    goal = (xs.index(int(outer_end[0])), ys.index(int(outer_end[1])))

    def clear(point_a: tuple[int, int], point_b: tuple[int, int]) -> bool:
        if any(segment_hits_rect(point_a, point_b, rect) for rect in obstacles):
            return False
        if block_occupied and segment_overlaps_occupied(point_a, point_b, horizontal_spans, vertical_spans):
            return False
        return True

    def heuristic(node: tuple[int, int]) -> int:
        return abs(xs[node[0]] - xs[goal[0]]) + abs(ys[node[1]] - ys[goal[1]])

    start_state = (start[0], start[1], "")
    heap = [(heuristic(start), 0, start_state)]
    distances = {start_state: 0}
    previous: dict[tuple[int, int, str], tuple[int, int, str]] = {}
    best_goal: tuple[int, int, str] | None = None

    while heap:
        _, cost, state = heapq.heappop(heap)
        if cost != distances[state]:
            continue
        ix, iy, direction = state
        if (ix, iy) == goal:
            best_goal = state
            break

        candidates = []
        if ix > 0:
            candidates.append((ix - 1, iy, "h"))
        if ix < len(xs) - 1:
            candidates.append((ix + 1, iy, "h"))
        if iy > 0:
            candidates.append((ix, iy - 1, "v"))
        if iy < len(ys) - 1:
            candidates.append((ix, iy + 1, "v"))

        current_point = (xs[ix], ys[iy])
        for next_ix, next_iy, next_direction in candidates:
            next_point = (xs[next_ix], ys[next_iy])
            if not clear(current_point, next_point):
                continue
            step = abs(next_point[0] - current_point[0]) + abs(next_point[1] - current_point[1])
            turn_penalty = 36 if direction and direction != next_direction else 0
            reuse_penalty = occupied_segment_penalty(
                current_point,
                next_point,
                horizontal_spans,
                vertical_spans,
                lane_counts,
            )
            next_state = (next_ix, next_iy, next_direction)
            next_cost = cost + step + turn_penalty + reuse_penalty
            if next_cost < distances.get(next_state, 10**12):
                distances[next_state] = next_cost
                previous[next_state] = state
                heapq.heappush(heap, (next_cost + heuristic((next_ix, next_iy)), next_cost, next_state))

    if best_goal is None:
        if block_occupied:
            return find_orthogonal_route(
                visual_start,
                outer_start,
                outer_end,
                visual_end,
                obstacles,
                canvas_width,
                canvas_height,
                horizontal_spans,
                vertical_spans,
                lane_counts,
                block_occupied=False,
            )
        fallback = fallback_route(visual_start, outer_start, outer_end, visual_end)
        record_route_usage(fallback, horizontal_spans, vertical_spans, lane_counts)
        return fallback

    grid_points = []
    state = best_goal
    while True:
        grid_points.append((xs[state[0]], ys[state[1]]))
        if state == start_state:
            break
        state = previous[state]
    grid_points.reverse()
    route = [visual_start, *grid_points, visual_end]
    record_route_usage(route, horizontal_spans, vertical_spans, lane_counts)
    return simplify_points(route)


def path_data(points: list[tuple[int, int]]) -> str:
    if not points:
        return ""
    commands = [f"M {points[0][0]} {points[0][1]}"]
    commands.extend(f"L {x} {y}" for x, y in points[1:])
    return " ".join(commands)


def point_at_path_midpoint(points: list[tuple[int, int]]) -> tuple[float, float]:
    if not points:
        return 0, 0
    lengths = []
    total = 0.0
    for first, second in zip(points, points[1:]):
        segment = abs(second[0] - first[0]) + abs(second[1] - first[1])
        lengths.append(segment)
        total += segment
    if total == 0:
        return points[0]
    target = total / 2
    walked = 0.0
    for index, segment in enumerate(lengths):
        if walked + segment >= target:
            start = points[index]
            end = points[index + 1]
            ratio = (target - walked) / segment if segment else 0
            return start[0] + (end[0] - start[0]) * ratio, start[1] + (end[1] - start[1]) * ratio
        walked += segment
    return points[-1]


def svg_interactivity_script() -> str:
    return """
  <script><![CDATA[
    (function () {
      const svg = document.currentScript.ownerSVGElement;
      if (!svg || svg.dataset.erInteractive === "1") return;
      svg.dataset.erInteractive = "1";
      const relations = Array.from(svg.querySelectorAll(".relation"));
      const cards = Array.from(svg.querySelectorAll(".card"));

      function clear() {
        relations.forEach((relation) => relation.classList.remove("active"));
        cards.forEach((card) => card.classList.remove("active-card"));
      }

      function highlight(relation) {
        const src = relation.dataset.src;
        const dst = relation.dataset.dst;
        relations.forEach((item) => {
          item.classList.toggle("active", item === relation);
        });
        cards.forEach((card) => {
          const connected = card.dataset.table === src || card.dataset.table === dst;
          card.classList.toggle("active-card", connected);
        });
      }

      relations.forEach((relation) => {
        relation.addEventListener("click", (event) => {
          event.stopPropagation();
          highlight(relation);
        });
      });
      svg.addEventListener("click", clear);
    })();
  ]]></script>
"""


def marker_defs() -> str:
    return """
  <defs>
    <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="#64748b"/>
    </marker>
    <marker id="arrow-active" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="#ef4444"/>
    </marker>
  </defs>
"""


def svg_shell(width: int, height: int, content: str) -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
{marker_defs()}
  <style>
    .page-title {{ font: 700 28px "Segoe UI", Arial, sans-serif; fill: #0f172a; }}
    .subtitle {{ font: 400 13px "Segoe UI", Arial, sans-serif; fill: #475569; }}
    .card-title {{ font: 700 {TITLE_FONT}px "Segoe UI", Arial, sans-serif; }}
    .field {{ font: {FIELD_FONT}px Consolas, "Liberation Mono", monospace; fill: #1f2937; }}
    .meta {{ font: 12px "Segoe UI", Arial, sans-serif; fill: #64748b; }}
    .section {{ font: 700 14px "Segoe UI", Arial, sans-serif; fill: #334155; }}
    .card {{ transition: opacity .12s ease; }}
    .card-outline {{ transition: stroke .12s ease, stroke-width .12s ease; }}
    .card.active-card .card-outline {{ stroke: #ef4444; stroke-width: 4; }}
    .relation {{ cursor: pointer; }}
    .overview-app {{ cursor: pointer; }}
    .overview-app:hover .overview-outline {{ stroke-width: 4; }}
    .edge-hit {{ stroke: transparent; stroke-width: 18; fill: none; pointer-events: stroke; }}
    .edge {{ stroke: #64748b; stroke-width: 1.8; fill: none; marker-end: url(#arrow); opacity: .62; }}
    .external-edge {{ stroke: #475569; opacity: .58; }}
    .relation.active .edge {{ stroke: #ef4444; stroke-width: 4; marker-end: url(#arrow-active); opacity: 1; }}
    .relation.active .edge-label-bg {{ stroke: #ef4444; stroke-width: 1.5; opacity: 1; }}
    .relation.active .edge-label {{ fill: #b91c1c; font-weight: 700; }}
    .edge-label-bg {{ fill: #ffffff; stroke: #e2e8f0; stroke-width: 1; opacity: .9; }}
    .edge-label {{ font: 10px "Segoe UI", Arial, sans-serif; fill: #475569; }}
  </style>
  <rect width="100%" height="100%" fill="#f8fafc"/>
{content}
{svg_interactivity_script()}
</svg>
"""


def render_card(
    table: dict,
    app: str,
    x: int,
    y: int,
    compact: bool,
    highlight: bool = False,
    external: bool = False,
) -> str:
    stroke, fill, header = color_for(app)
    if external:
        stroke, fill, header = "#94a3b8", "#f8fafc", "#e2e8f0"
    if highlight:
        stroke, header = "#0f172a", "#bfdbfe"

    width, height = card_size(table, compact)
    rows = display_fields(table, compact)
    parts = [
        f'  <g id="{escape(slug(table["name"]))}" class="card" data-table="{escape(table["name"])}">',
        f'    <title>{escape(table["name"])}</title>',
        f'    <rect class="card-outline" x="{x}" y="{y}" width="{width}" height="{height}" rx="8" fill="#ffffff" stroke="{stroke}" stroke-width="{3 if highlight else 1.5}"/>',
        f'    <rect x="{x}" y="{y}" width="{width}" height="{HEADER_H}" rx="8" fill="{header}" stroke="{stroke}" stroke-width="1"/>',
        f'    <rect x="{x}" y="{y + HEADER_H - 8}" width="{width}" height="8" fill="{header}"/>',
        f'    <text x="{x + CARD_PAD_X}" y="{y + 22}" class="card-title" fill="{stroke}">{escape(table["name"])}</text>',
    ]
    if external:
        parts.append(
            f'    <text x="{x + width - CARD_PAD_X}" y="{y + 22}" class="meta" text-anchor="end">{escape(app)}</text>'
        )
    row_y = y + HEADER_H + CARD_PAD_Y + 12
    for row in rows:
        parts.append(f'    <text x="{x + CARD_PAD_X}" y="{row_y}" class="field">{escape(row)}</text>')
        row_y += ROW_H
    parts.append("  </g>")
    return "\n".join(parts)


def render_edges(
    relationships: list[dict],
    rects: dict[str, tuple[int, int, int, int]],
    canvas_width: int,
    canvas_height: int,
    show_labels: bool = True,
) -> str:
    chunks = []
    horizontal_spans: defaultdict[int, list[tuple[int, int]]] = defaultdict(list)
    vertical_spans: defaultdict[int, list[tuple[int, int]]] = defaultdict(list)
    lane_counts: Counter[tuple[str, int]] = Counter()
    endpoint_sides: dict[int, tuple[str, str]] = {}
    endpoint_entries: defaultdict[tuple[str, str], list[tuple[int, float, str]]] = defaultdict(list)

    for index, relation in enumerate(relationships):
        if relation["src"] not in rects or relation["dst"] not in rects:
            continue
        src_side, dst_side = choose_sides(rects[relation["src"]], rects[relation["dst"]])
        endpoint_sides[index] = (src_side, dst_side)
        dst_center = center(rects[relation["dst"]])
        src_center = center(rects[relation["src"]])
        src_sort = dst_center[1] if src_side in {"left", "right"} else dst_center[0]
        dst_sort = src_center[1] if dst_side in {"left", "right"} else src_center[0]
        endpoint_entries[(relation["src"], src_side)].append((index, src_sort, "src"))
        endpoint_entries[(relation["dst"], dst_side)].append((index, dst_sort, "dst"))

    endpoint_slots: dict[tuple[int, str], tuple[int, int]] = {}
    for entries in endpoint_entries.values():
        entries.sort(key=lambda item: (item[1], item[0]))
        total = len(entries)
        for slot, (index, _, endpoint) in enumerate(entries):
            endpoint_slots[(index, endpoint)] = (slot, total)

    for index, relation in enumerate(relationships):
        if relation["src"] not in rects or relation["dst"] not in rects:
            continue
        src_side, dst_side = endpoint_sides[index]
        src_slot, src_total = endpoint_slots[(index, "src")]
        dst_slot, dst_total = endpoint_slots[(index, "dst")]
        obstacles = []
        for table_name, (x, y, width, height) in rects.items():
            if table_name in {relation["src"], relation["dst"]}:
                continue
            obstacles.append((x - 14, y - 14, x + width + 14, y + height + 14))
        visual_start, outer_start = port_point(rects[relation["src"]], src_side, src_slot, src_total)
        visual_end, outer_end = port_point(rects[relation["dst"]], dst_side, dst_slot, dst_total)
        if any(segment_hits_rect(visual_start, outer_start, rect) for rect in obstacles):
            visual_start, outer_start = port_point(rects[relation["src"]], src_side, src_slot, src_total, lane_step=0)
        if any(segment_hits_rect(visual_end, outer_end, rect) for rect in obstacles):
            visual_end, outer_end = port_point(rects[relation["dst"]], dst_side, dst_slot, dst_total, lane_step=0)
        points = find_orthogonal_route(
            visual_start,
            outer_start,
            outer_end,
            visual_end,
            obstacles,
            canvas_width,
            canvas_height,
            horizontal_spans,
            vertical_spans,
            lane_counts,
        )
        d = path_data(points)
        chunks.append(
            f'  <g class="relation" data-src="{escape(relation["src"])}" data-dst="{escape(relation["dst"])}" data-label="{escape(relation["label"])}">'
        )
        chunks.append(f'    <title>{escape(relation["src"])} to {escape(relation["dst"])} via {escape(relation["label"])}</title>')
        chunks.append(f'    <path class="edge-hit" d="{d}"/>')
        chunks.append(f'    <path class="edge" d="{d}"/>')
        if show_labels:
            label = relation["label"]
            label_w = max(34, len(label) * 6 + 12)
            lx, ly = point_at_path_midpoint(points)
            chunks.append(
                f'    <rect class="edge-label-bg" x="{lx - label_w / 2:.1f}" y="{ly - 8:.1f}" width="{label_w}" height="16" rx="4"/>'
            )
            chunks.append(
                f'    <text class="edge-label" x="{lx:.1f}" y="{ly + 4:.1f}" text-anchor="middle">{escape(label)}</text>'
            )
        chunks.append("  </g>")
    return "\n".join(chunks)


def render_external_edges(
    relationships: list[dict],
    internal_names: set[str],
    rects: dict[str, tuple[int, int, int, int]],
    central_left: int,
    central_right: int,
    show_labels: bool = True,
) -> str:
    external_relationships = [
        relation
        for relation in relationships
        if (relation["src"] in internal_names) != (relation["dst"] in internal_names)
        and relation["src"] in rects
        and relation["dst"] in rects
    ]
    if not external_relationships:
        return ""

    endpoint_entries: defaultdict[tuple[str, str], list[tuple[int, float, str]]] = defaultdict(list)
    for index, relation in enumerate(external_relationships):
        src_side = "right" if relation["src"] in internal_names else "left"
        dst_side = "right" if relation["dst"] in internal_names else "left"
        src_sort = center(rects[relation["dst"]])[1]
        dst_sort = center(rects[relation["src"]])[1]
        endpoint_entries[(relation["src"], src_side)].append((index, src_sort, "src"))
        endpoint_entries[(relation["dst"], dst_side)].append((index, dst_sort, "dst"))

    endpoint_slots: dict[tuple[int, str], tuple[int, int]] = {}
    for entries in endpoint_entries.values():
        entries.sort(key=lambda item: (item[1], item[0]))
        total = len(entries)
        for slot, (index, _, endpoint) in enumerate(entries):
            endpoint_slots[(index, endpoint)] = (slot, total)

    sorted_indexes = sorted(
        range(len(external_relationships)),
        key=lambda index: (
            center(rects[external_relationships[index]["src"]])[1]
            + center(rects[external_relationships[index]["dst"]])[1],
            external_relationships[index]["label"],
        ),
    )
    spacing = max(10, (central_right - central_left - 80) / max(1, len(external_relationships) - 1))
    track_x_by_index = {
        relation_index: round(central_left + 40 + order * spacing)
        for order, relation_index in enumerate(sorted_indexes)
    }

    chunks = []
    for index, relation in enumerate(external_relationships):
        src_side = "right" if relation["src"] in internal_names else "left"
        dst_side = "right" if relation["dst"] in internal_names else "left"
        src_slot, src_total = endpoint_slots[(index, "src")]
        dst_slot, dst_total = endpoint_slots[(index, "dst")]
        visual_start, outer_start = port_point(
            rects[relation["src"]],
            src_side,
            src_slot,
            src_total,
            margin=20,
            lane_step=6,
        )
        visual_end, outer_end = port_point(
            rects[relation["dst"]],
            dst_side,
            dst_slot,
            dst_total,
            margin=20,
            lane_step=6,
        )
        track_x = track_x_by_index[index]
        lane_offset = round((index - (len(external_relationships) - 1) / 2) * 4)
        start_lane_y = outer_start[1] + lane_offset
        end_lane_y = outer_end[1] + lane_offset
        points = simplify_points(
            [
                visual_start,
                outer_start,
                (outer_start[0], start_lane_y),
                (track_x, start_lane_y),
                (track_x, end_lane_y),
                (outer_end[0], end_lane_y),
                outer_end,
                visual_end,
            ]
        )
        d = path_data(points)
        chunks.append(
            f'  <g class="relation" data-src="{escape(relation["src"])}" data-dst="{escape(relation["dst"])}" data-label="{escape(relation["label"])}">'
        )
        chunks.append(f'    <title>{escape(relation["src"])} to {escape(relation["dst"])} via {escape(relation["label"])}</title>')
        chunks.append(f'    <path class="edge-hit" d="{d}"/>')
        chunks.append(f'    <path class="edge external-edge" d="{d}"/>')
        if show_labels:
            label = relation["label"]
            label_w = max(34, len(label) * 6 + 12)
            lx, ly = point_at_path_midpoint(points)
            chunks.append(
                f'    <rect class="edge-label-bg" x="{lx - label_w / 2:.1f}" y="{ly - 8:.1f}" width="{label_w}" height="16" rx="4"/>'
            )
            chunks.append(
                f'    <text class="edge-label" x="{lx:.1f}" y="{ly + 4:.1f}" text-anchor="middle">{escape(label)}</text>'
            )
        chunks.append("  </g>")
    return "\n".join(chunks)


def render_column_edges(
    relationships: list[dict],
    rects: dict[str, tuple[int, int, int, int]],
    lane_left: int,
    lane_right: int,
    show_labels: bool = True,
) -> str:
    relationships = [
        relation
        for relation in relationships
        if relation["src"] in rects and relation["dst"] in rects
    ]
    if not relationships:
        return ""

    endpoint_entries: defaultdict[tuple[str, str], list[tuple[int, float, str]]] = defaultdict(list)
    for index, relation in enumerate(relationships):
        endpoint_entries[(relation["src"], "left")].append((index, center(rects[relation["dst"]])[1], "src"))
        endpoint_entries[(relation["dst"], "left")].append((index, center(rects[relation["src"]])[1], "dst"))

    endpoint_slots: dict[tuple[int, str], tuple[int, int]] = {}
    for entries in endpoint_entries.values():
        entries.sort(key=lambda item: (item[1], item[0]))
        total = len(entries)
        for slot, (index, _, endpoint) in enumerate(entries):
            endpoint_slots[(index, endpoint)] = (slot, total)

    sorted_indexes = sorted(
        range(len(relationships)),
        key=lambda index: (
            center(rects[relationships[index]["src"]])[1]
            + center(rects[relationships[index]["dst"]])[1],
            relationships[index]["label"],
        ),
    )
    spacing = max(10, (lane_right - lane_left - 80) / max(1, len(relationships) - 1))
    track_x_by_index = {
        relation_index: round(lane_right - 40 - order * spacing)
        for order, relation_index in enumerate(sorted_indexes)
    }

    chunks = []
    for index, relation in enumerate(relationships):
        src_slot, src_total = endpoint_slots[(index, "src")]
        dst_slot, dst_total = endpoint_slots[(index, "dst")]
        visual_start, outer_start = port_point(
            rects[relation["src"]],
            "left",
            src_slot,
            src_total,
            margin=20,
            lane_step=6,
        )
        visual_end, outer_end = port_point(
            rects[relation["dst"]],
            "left",
            dst_slot,
            dst_total,
            margin=20,
            lane_step=6,
        )
        track_x = track_x_by_index[index]
        lane_offset = round((index - (len(relationships) - 1) / 2) * 4)
        start_lane_y = outer_start[1] + lane_offset
        end_lane_y = outer_end[1] + lane_offset
        points = simplify_points(
            [
                visual_start,
                outer_start,
                (outer_start[0], start_lane_y),
                (track_x, start_lane_y),
                (track_x, end_lane_y),
                (outer_end[0], end_lane_y),
                outer_end,
                visual_end,
            ]
        )
        d = path_data(points)
        chunks.append(
            f'  <g class="relation" data-src="{escape(relation["src"])}" data-dst="{escape(relation["dst"])}" data-label="{escape(relation["label"])}">'
        )
        chunks.append(f'    <title>{escape(relation["src"])} to {escape(relation["dst"])} via {escape(relation["label"])}</title>')
        chunks.append(f'    <path class="edge-hit" d="{d}"/>')
        chunks.append(f'    <path class="edge" d="{d}"/>')
        if show_labels:
            label = relation["label"]
            label_w = max(34, len(label) * 6 + 12)
            lx, ly = point_at_path_midpoint(points)
            chunks.append(
                f'    <rect class="edge-label-bg" x="{lx - label_w / 2:.1f}" y="{ly - 8:.1f}" width="{label_w}" height="16" rx="4"/>'
            )
            chunks.append(
                f'    <text class="edge-label" x="{lx:.1f}" y="{ly + 4:.1f}" text-anchor="middle">{escape(label)}</text>'
            )
        chunks.append("  </g>")
    return "\n".join(chunks)


def app_diagram(
    app: str,
    tables: dict[str, dict],
    apps_by_table: dict[str, str],
    relationships: list[dict],
    tables_by_app: dict[str, list[str]],
    degree: Counter[str],
) -> tuple[str, int, int]:
    internal = sorted(tables_by_app[app], key=lambda name: (-degree[name], name))
    related = [
        relation
        for relation in relationships
        if relation["src"] in internal or relation["dst"] in internal
    ]
    internal_set = set(internal)
    local_edges = [
        relation
        for relation in related
        if relation["src"] in internal_set and relation["dst"] in internal_set
    ]
    external_edges = [
        relation
        for relation in related
        if (relation["src"] in internal_set) != (relation["dst"] in internal_set)
    ]
    external = sorted(
        {
            endpoint
            for relation in related
            for endpoint in (relation["src"], relation["dst"])
            if endpoint not in internal
        },
        key=lambda name: (apps_by_table[name], name),
    )

    sizes = {}
    for name in internal:
        sizes[name] = card_size(tables[name], compact=False)
    for name in external:
        sizes[name] = card_size(tables[name], compact=True)

    local_lane_width = max(170, len(local_edges) * 14 + 90)
    start_x = 60 + local_lane_width
    start_y = 132
    internal_pos, internal_w, internal_h = stack_columns(internal, sizes, start_x, start_y, 100_000, gap_y=44)
    central_gap = max(440, len(external_edges) * 13 + 100)
    external_start = start_x + internal_w + central_gap
    external_pos, external_w, external_h = stack_columns(external, sizes, external_start, start_y, 100_000, gap_y=44)
    positions = {**internal_pos, **external_pos}
    rects = {
        name: (x, y, sizes[name][0], sizes[name][1])
        for name, (x, y) in positions.items()
    }
    width = max(1100, start_x + internal_w + (central_gap if external else 0) + external_w + 60)
    height = max(720, start_y + max(internal_h, external_h) + 80)

    title = f"{app.replace('_', ' ').title()} ER Slice"
    subtitle = (
        f"{len(internal)} local tables, {len(external)} linked external tables, "
        f"{len(local_edges)} local relationships, {len(external_edges)} external relationships"
    )
    content = [
        f'  <text x="60" y="54" class="page-title">{escape(title)}</text>',
        f'  <text x="60" y="80" class="subtitle">{escape(subtitle)}</text>',
    ]
    if external:
        content.append(f'  <text x="{external_start}" y="112" class="section">Linked external tables</text>')
    content.append(render_column_edges(local_edges, rects, 60, start_x, show_labels=True))
    content.append(
        render_external_edges(
            external_edges,
            internal_set,
            rects,
            start_x + internal_w,
            external_start,
            show_labels=True,
        )
    )
    for name in internal:
        x, y = positions[name]
        content.append(render_card(tables[name], app, x, y, compact=False))
    for name in external:
        x, y = positions[name]
        content.append(render_card(tables[name], apps_by_table[name], x, y, compact=True, external=True))
    return svg_shell(width, height, "\n".join(content)), width, height


def neighborhood_diagram(
    focus: str,
    tables: dict[str, dict],
    apps_by_table: dict[str, str],
    relationships: list[dict],
    degree: Counter[str],
) -> tuple[str, int, int]:
    direct = [relation for relation in relationships if relation["src"] == focus or relation["dst"] == focus]
    parents = sorted({relation["src"] for relation in direct if relation["dst"] == focus}, key=lambda name: (-degree[name], name))
    children = sorted({relation["dst"] for relation in direct if relation["src"] == focus}, key=lambda name: (-degree[name], name))
    both = set(parents).intersection(children)
    parents = [name for name in parents if name not in both]
    children = [name for name in children if name not in both]
    bridge = sorted(both, key=lambda name: (-degree[name], name))

    visible = [focus] + parents + children + bridge
    sizes = {name: card_size(tables[name], compact=name != focus) for name in visible}

    gap_x = 180
    start_y = 150
    target_h = max(
        680,
        min(
            1800,
            total_stack_height(parents + bridge, sizes, 30) + 120,
            total_stack_height(children, sizes, 30) + 120,
        ),
    )

    left_pos, left_w, left_h = stack_columns(parents + bridge, sizes, 60, start_y, target_h, gap_x=46, gap_y=30)
    focus_x = 60 + max(left_w, 260) + gap_x
    focus_y = start_y + max(0, max(left_h, 420) // 2 - sizes[focus][1] // 2)
    right_x = focus_x + sizes[focus][0] + gap_x
    right_pos, right_w, right_h = stack_columns(children, sizes, right_x, start_y, target_h, gap_x=46, gap_y=30)

    positions = {**left_pos, focus: (focus_x, focus_y), **right_pos}
    rects = {
        name: (x, y, sizes[name][0], sizes[name][1])
        for name, (x, y) in positions.items()
    }
    width = max(1000, right_x + right_w + 70)
    height = max(720, start_y + max(left_h, right_h, focus_y + sizes[focus][1] - start_y) + 90)

    title = f"{focus} Neighborhood"
    subtitle = f"{len(parents) + len(bridge)} parent/lookup tables, {len(children)} child tables, {len(direct)} direct relationships"
    content = [
        f'  <text x="60" y="54" class="page-title">{escape(title)}</text>',
        f'  <text x="60" y="80" class="subtitle">{escape(subtitle)}</text>',
    ]
    if parents or bridge:
        content.append('  <text x="60" y="126" class="section">Parents and lookups</text>')
    if children:
        content.append(f'  <text x="{right_x}" y="126" class="section">Children and dependents</text>')
    content.append(render_edges(direct, rects, width, height, show_labels=True))
    for name in parents + bridge:
        x, y = positions[name]
        content.append(render_card(tables[name], apps_by_table[name], x, y, compact=True, external=True))
    x, y = positions[focus]
    content.append(render_card(tables[focus], apps_by_table[focus], x, y, compact=False, highlight=True))
    for name in children:
        x, y = positions[name]
        content.append(render_card(tables[name], apps_by_table[name], x, y, compact=True, external=True))
    return svg_shell(width, height, "\n".join(content)), width, height


def overview_diagram(
    tables_by_app: dict[str, list[str]],
    relationships: list[dict],
    apps_by_table: dict[str, str],
) -> tuple[str, int, int]:
    apps = sorted(tables_by_app, key=lambda app: (-len(tables_by_app[app]), app))
    card_w = 250
    card_h = 92
    gap_x = 72
    gap_y = 74
    cols = 4
    positions = {}
    for index, app in enumerate(apps):
        row = index // cols
        col = index % cols
        positions[app] = (60 + col * (card_w + gap_x), 150 + row * (card_h + gap_y))

    pair_counts: Counter[tuple[str, str]] = Counter()
    internal_counts: Counter[str] = Counter()
    for relation in relationships:
        src_app = apps_by_table[relation["src"]]
        dst_app = apps_by_table[relation["dst"]]
        if src_app == dst_app:
            internal_counts[src_app] += 1
        else:
            pair_counts[tuple(sorted((src_app, dst_app)))] += 1

    rows = math.ceil(len(apps) / cols)
    width = 60 + cols * card_w + (cols - 1) * gap_x + 60
    height = 150 + rows * card_h + max(0, rows - 1) * gap_y + 90
    content = [
        '  <text x="60" y="54" class="page-title">Factory App ER Overview</text>',
        f'  <text x="60" y="80" class="subtitle">{len(apps)} apps, {sum(len(v) for v in tables_by_app.values())} tables, {len(relationships)} relationships. Open an app or table from the sidebar for detail.</text>',
    ]

    for (app_a, app_b), count in pair_counts.items():
        if app_a not in positions or app_b not in positions:
            continue
        ax, ay = positions[app_a]
        bx, by = positions[app_b]
        sx, sy = boundary_point((ax, ay, card_w, card_h), (bx, by, card_w, card_h))
        ex, ey = boundary_point((bx, by, card_w, card_h), (ax, ay, card_w, card_h))
        stroke_w = min(7, 1 + count / 3)
        content.append(
            f'  <path d="M {sx:.1f} {sy:.1f} L {ex:.1f} {ey:.1f}" stroke="#94a3b8" stroke-width="{stroke_w:.1f}" fill="none" opacity=".34"/>'
        )
        if count >= 3:
            content.append(
                f'  <text class="edge-label" x="{(sx + ex) / 2:.1f}" y="{(sy + ey) / 2:.1f}" text-anchor="middle">{count}</text>'
            )

    for app in apps:
        x, y = positions[app]
        stroke, fill, header = color_for(app)
        content.extend(
            [
                f'  <g class="overview-app" data-app="{escape(app)}">',
                f'    <title>Open {escape(app)} ER slice</title>',
                f'    <rect class="overview-outline" x="{x}" y="{y}" width="{card_w}" height="{card_h}" rx="10" fill="#ffffff" stroke="{stroke}" stroke-width="2"/>',
                f'    <rect x="{x}" y="{y}" width="{card_w}" height="34" rx="10" fill="{header}" stroke="{stroke}" stroke-width="1"/>',
                f'    <rect x="{x}" y="{y + 26}" width="{card_w}" height="8" fill="{header}"/>',
                f'    <text x="{x + 14}" y="{y + 23}" class="card-title" fill="{stroke}">{escape(app)}</text>',
                f'    <text x="{x + 14}" y="{y + 58}" class="meta">{len(tables_by_app[app])} tables</text>',
                f'    <text x="{x + 14}" y="{y + 78}" class="meta">{internal_counts[app]} internal relationships</text>',
                "  </g>",
            ]
        )

    return svg_shell(width, height, "\n".join(content)), width, height


def build_index_html() -> str:
    return """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Factory App ER Explorer</title>
  <script src="schema.js"></script>
  <style>
    :root {
      color-scheme: light;
      --bg: #f8fafc;
      --panel: #ffffff;
      --line: #dbe3ef;
      --text: #0f172a;
      --muted: #64748b;
      --accent: #2563eb;
      --soft: #eff6ff;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: "Segoe UI", system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
      color: var(--text);
      background: var(--bg);
      height: 100vh;
      overflow: hidden;
    }
    .app {
      display: grid;
      grid-template-columns: 360px 1fr;
      height: 100vh;
      min-height: 0;
      overflow: hidden;
    }
    aside {
      border-right: 1px solid var(--line);
      background: var(--panel);
      min-width: 0;
      min-height: 0;
      overflow: hidden;
      display: flex;
      flex-direction: column;
    }
    header {
      padding: 18px 18px 14px;
      border-bottom: 1px solid var(--line);
      flex: 0 0 auto;
    }
    h1 {
      margin: 0 0 6px;
      font-size: 20px;
      line-height: 1.2;
      letter-spacing: 0;
    }
    .summary {
      margin: 0;
      color: var(--muted);
      font-size: 13px;
      line-height: 1.35;
    }
    .sidebar-body {
      flex: 1 1 auto;
      min-height: 0;
      overflow: auto;
      padding: 14px;
      overscroll-behavior: contain;
    }
    .section-title {
      margin: 14px 4px 8px;
      color: #334155;
      font-size: 12px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: .04em;
    }
    .search {
      width: 100%;
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 10px 11px;
      font: inherit;
      outline: none;
    }
    .search:focus {
      border-color: var(--accent);
      box-shadow: 0 0 0 3px rgba(37, 99, 235, .12);
    }
    .button-list {
      display: grid;
      gap: 6px;
    }
    button {
      font: inherit;
    }
    .nav-button {
      width: 100%;
      border: 1px solid transparent;
      background: transparent;
      color: var(--text);
      border-radius: 8px;
      padding: 9px 10px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 8px;
      cursor: pointer;
      text-align: left;
    }
    .nav-button:hover {
      background: #f1f5f9;
    }
    .nav-button.active {
      background: var(--soft);
      border-color: #bfdbfe;
      color: #1d4ed8;
    }
    .nav-name {
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
    .count {
      flex: 0 0 auto;
      color: var(--muted);
      font-size: 12px;
    }
    main {
      min-width: 0;
      min-height: 0;
      display: grid;
      grid-template-rows: auto 1fr auto;
      height: 100vh;
      overflow: hidden;
    }
    .toolbar {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      padding: 12px 16px;
      background: var(--panel);
      border-bottom: 1px solid var(--line);
    }
    .toolbar h2 {
      margin: 0;
      font-size: 17px;
      line-height: 1.25;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
    .toolbar-actions {
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .tool-button {
      border: 1px solid var(--line);
      background: #fff;
      border-radius: 8px;
      padding: 7px 10px;
      cursor: pointer;
      color: #1f2937;
      min-width: 36px;
    }
    .tool-button:hover {
      border-color: #93c5fd;
      color: #1d4ed8;
    }
    .tool-button:disabled {
      color: #94a3b8;
      cursor: wait;
      background: #f8fafc;
    }
    .tool-button.primary {
      border-color: #bfdbfe;
      background: #eff6ff;
      color: #1d4ed8;
      font-weight: 600;
    }
    .refresh-status {
      min-width: 150px;
      color: var(--muted);
      font-size: 12px;
      white-space: nowrap;
    }
    .refresh-status.error {
      color: #b91c1c;
    }
    .zoom-label {
      min-width: 62px;
      text-align: center;
      color: var(--muted);
      font-size: 13px;
    }
    .viewport {
      min-height: 0;
      overflow: auto;
      position: relative;
      background:
        linear-gradient(90deg, rgba(148, 163, 184, .18) 1px, transparent 1px),
        linear-gradient(rgba(148, 163, 184, .18) 1px, transparent 1px);
      background-size: 24px 24px;
      background-color: #f8fafc;
    }
    .scaled {
      position: relative;
      margin: 24px;
    }
    .diagram {
      transform-origin: top left;
      display: block;
      border: 1px solid var(--line);
      box-shadow: 0 16px 40px rgba(15, 23, 42, .08);
      background: #fff;
      overflow: hidden;
    }
    .details {
      border-top: 1px solid var(--line);
      background: var(--panel);
      padding: 11px 16px;
      display: grid;
      grid-template-columns: minmax(220px, 350px) 1fr;
      gap: 18px;
      max-height: 178px;
      overflow: auto;
    }
    .details h3 {
      margin: 0 0 4px;
      font-size: 14px;
    }
    .muted {
      color: var(--muted);
      font-size: 12px;
      line-height: 1.35;
    }
    .field-grid,
    .relationship-list {
      display: grid;
      gap: 4px;
      font-size: 12px;
      line-height: 1.35;
    }
    .field-row {
      display: grid;
      grid-template-columns: 52px minmax(90px, 1fr) 90px;
      gap: 8px;
      border-bottom: 1px solid #f1f5f9;
      padding: 2px 0;
      min-width: 0;
    }
    .field-row span {
      min-width: 0;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
    .tag {
      color: #1d4ed8;
      font-weight: 700;
    }
    .rel-row {
      border-bottom: 1px solid #f1f5f9;
      padding: 3px 0;
    }
    @media (max-width: 900px) {
      .app { grid-template-columns: 300px 1fr; }
      .details { grid-template-columns: 1fr; max-height: 220px; }
    }
  </style>
</head>
<body>
  <div class="app">
    <aside>
      <header>
        <h1>ER Explorer</h1>
        <p class="summary" id="summary"></p>
      </header>
      <div class="sidebar-body">
        <button class="nav-button active" id="overviewButton" type="button">
          <span class="nav-name">Overview</span>
          <span class="count">all</span>
        </button>
        <div class="section-title">Apps</div>
        <div class="button-list" id="appList"></div>
        <div class="section-title">Tables</div>
        <input class="search" id="search" placeholder="Search tables or fields">
        <div class="button-list" id="tableList" style="margin-top: 10px"></div>
      </div>
    </aside>
    <main>
      <div class="toolbar">
        <h2 id="diagramTitle">Overview</h2>
        <div class="toolbar-actions">
          <button class="tool-button primary" id="refreshEr" type="button">Refresh from DB</button>
          <span class="refresh-status" id="refreshStatus"></span>
          <button class="tool-button" id="zoomOut" type="button">-</button>
          <span class="zoom-label" id="zoomLabel">100%</span>
          <button class="tool-button" id="zoomIn" type="button">+</button>
          <button class="tool-button" id="zoomReset" type="button">Reset</button>
        </div>
      </div>
      <div class="viewport" id="viewport">
        <div class="scaled" id="scaled">
          <object class="diagram" id="diagram" type="image/svg+xml" aria-label="ER diagram"></object>
        </div>
      </div>
      <div class="details" id="details"></div>
    </main>
  </div>
  <script>
    const schema = window.ER_SCHEMA;
    const diagrams = schema.diagrams;
    const tablesByName = new Map(schema.tables.map((table) => [table.name, table]));
    const appsByName = new Map(schema.apps.map((app) => [app.name, app]));
    let activeKind = "overview";
    let activeName = "overview";
    let zoom = 1;

    const summary = document.getElementById("summary");
    const appList = document.getElementById("appList");
    const tableList = document.getElementById("tableList");
    const search = document.getElementById("search");
    const overviewButton = document.getElementById("overviewButton");
    const diagram = document.getElementById("diagram");
    const scaled = document.getElementById("scaled");
    const viewport = document.getElementById("viewport");
    const diagramTitle = document.getElementById("diagramTitle");
    const zoomLabel = document.getElementById("zoomLabel");
    const details = document.getElementById("details");
    const refreshEr = document.getElementById("refreshEr");
    const refreshStatus = document.getElementById("refreshStatus");

    summary.textContent = `${schema.stats.tables} tables, ${schema.stats.relationships} relationships. Generated ${schema.generatedAt} from ${schema.source}.`;

    function appTitle(name) {
      return name.replaceAll("_", " ");
    }

    function setActiveButtons() {
      overviewButton.classList.toggle("active", activeKind === "overview");
      document.querySelectorAll("[data-app]").forEach((button) => {
        button.classList.toggle("active", activeKind === "app" && button.dataset.app === activeName);
      });
      document.querySelectorAll("[data-table]").forEach((button) => {
        button.classList.toggle("active", activeKind === "table" && button.dataset.table === activeName);
      });
    }

    function currentDiagramId() {
      if (activeKind === "overview") return "overview";
      if (activeKind === "app") return `app:${activeName}`;
      return `table:${activeName}`;
    }

    function setZoom(value) {
      const previous = zoom;
      zoom = Math.max(.25, Math.min(4, value));
      const current = diagrams[currentDiagramId()];
      scaled.style.width = `${current.width * zoom}px`;
      scaled.style.height = `${current.height * zoom}px`;
      diagram.style.width = `${current.width}px`;
      diagram.style.height = `${current.height}px`;
      diagram.style.transform = `scale(${zoom})`;
      zoomLabel.textContent = `${Math.round(zoom * 100)}%`;
      if (previous !== zoom) {
        const factor = zoom / previous;
        viewport.scrollLeft = viewport.scrollLeft * factor;
        viewport.scrollTop = viewport.scrollTop * factor;
      }
    }

    function refreshUrl() {
      const path = "/api/v1/dev/er-explorer/refresh/";
      if (window.location.protocol === "file:") {
        return `http://127.0.0.1:8000${path}`;
      }
      return path;
    }

    async function refreshFromDatabase() {
      refreshEr.disabled = true;
      refreshStatus.classList.remove("error");
      refreshStatus.textContent = "Refreshing...";
      try {
        const response = await fetch(refreshUrl(), {
          method: "POST",
          headers: { "Accept": "application/json" },
        });
        const payload = await response.json().catch(() => ({}));
        if (!response.ok || !payload.ok) {
          throw new Error(payload.error || `Refresh failed with HTTP ${response.status}`);
        }
        refreshStatus.textContent = "Updated. Reloading...";
        window.location.reload();
      } catch (error) {
        refreshStatus.classList.add("error");
        refreshStatus.textContent = error.message || "Refresh failed";
      } finally {
        refreshEr.disabled = false;
      }
    }

    function installSvgInteractivity() {
      let doc;
      try {
        doc = diagram.contentDocument;
      } catch (error) {
        return;
      }
      const svg = doc && doc.querySelector("svg");
      if (!svg || svg.dataset.erHostInteractive === "1") return;
      svg.dataset.erHostInteractive = "1";
      const relations = Array.from(svg.querySelectorAll(".relation"));
      const cards = Array.from(svg.querySelectorAll(".card"));
      const overviewApps = Array.from(svg.querySelectorAll(".overview-app"));

      function clear() {
        relations.forEach((relation) => relation.classList.remove("active"));
        cards.forEach((card) => card.classList.remove("active-card"));
      }

      function highlight(relation) {
        const src = relation.dataset.src;
        const dst = relation.dataset.dst;
        relations.forEach((item) => {
          item.classList.toggle("active", item === relation);
        });
        cards.forEach((card) => {
          const connected = card.dataset.table === src || card.dataset.table === dst;
          card.classList.toggle("active-card", connected);
        });
      }

      relations.forEach((relation) => {
        relation.addEventListener("click", (event) => {
          event.stopPropagation();
          highlight(relation);
        });
      });
      overviewApps.forEach((appCard) => {
        appCard.addEventListener("click", (event) => {
          event.stopPropagation();
          const app = appCard.dataset.app;
          if (app && diagrams[`app:${app}`]) {
            showDiagram("app", app);
          }
        });
      });
      svg.addEventListener("click", clear);
    }

    function showDiagram(kind, name) {
      activeKind = kind;
      activeName = name;
      const item = diagrams[currentDiagramId()];
      diagram.data = item.src;
      diagramTitle.textContent = item.title;
      zoom = 1;
      setZoom(1);
      setActiveButtons();
      viewport.scrollTop = 0;
      viewport.scrollLeft = 0;
      renderDetails();
    }

    function renderApps() {
      appList.innerHTML = "";
      schema.apps.forEach((app) => {
        const button = document.createElement("button");
        button.type = "button";
        button.className = "nav-button";
        button.dataset.app = app.name;
        button.innerHTML = `<span class="nav-name">${appTitle(app.name)}</span><span class="count">${app.tableCount}</span>`;
        button.addEventListener("click", () => showDiagram("app", app.name));
        appList.appendChild(button);
      });
    }

    function matchesSearch(table, query) {
      if (!query) return true;
      const haystack = [
        table.name,
        table.app,
        ...table.fields.flatMap((field) => [field.name, field.type, field.tags.join(" "), field.notes.join(" ")]),
      ].join(" ").toLowerCase();
      return haystack.includes(query);
    }

    function renderTables() {
      const query = search.value.trim().toLowerCase();
      const appFilter = activeKind === "app" ? activeName : null;
      tableList.innerHTML = "";
      schema.tables
        .filter((table) => (!appFilter || table.app === appFilter) && matchesSearch(table, query))
        .slice(0, query ? 80 : 160)
        .forEach((table) => {
          const button = document.createElement("button");
          button.type = "button";
          button.className = "nav-button";
          button.dataset.table = table.name;
          button.innerHTML = `<span class="nav-name">${table.name}</span><span class="count">${table.app}</span>`;
          button.addEventListener("click", () => showDiagram("table", table.name));
          tableList.appendChild(button);
        });
      setActiveButtons();
    }

    function renderDetails() {
      if (activeKind === "overview") {
        details.innerHTML = `
          <div>
            <h3>Overview</h3>
            <div class="muted">Open an app for a module slice, or search and open a table for its direct neighborhood.</div>
          </div>
          <div class="relationship-list">
            <div class="rel-row">Large diagrams are split into lazily loaded SVG files, so the page only renders one slice at a time.</div>
          </div>
        `;
        renderTables();
        return;
      }

      if (activeKind === "app") {
        const app = appsByName.get(activeName);
        details.innerHTML = `
          <div>
            <h3>${appTitle(app.name)}</h3>
            <div class="muted">${app.tableCount} tables, ${app.relationshipCount} local/external relationships.</div>
          </div>
          <div class="relationship-list">
            <div class="rel-row">Use the table search to open a focused neighborhood when a relationship label is hard to inspect in the app slice.</div>
          </div>
        `;
        renderTables();
        return;
      }

      const table = tablesByName.get(activeName);
      const related = schema.relationships.filter((rel) => rel.src === table.name || rel.dst === table.name);
      const fieldRows = table.fields.map((field) => `
        <div class="field-row">
          <span class="tag">${field.tags.join("/")}</span>
          <span title="${field.name}">${field.name}</span>
          <span title="${field.type}">${field.type}</span>
        </div>
      `).join("") || `<div class="muted">No fields listed.</div>`;
      const relationshipRows = related.map((rel) => `
        <div class="rel-row">${rel.src} -> ${rel.dst} <span class="muted">(${rel.label})</span></div>
      `).join("") || `<div class="muted">No relationships found.</div>`;
      details.innerHTML = `
        <div>
          <h3>${table.name}</h3>
          <div class="muted">${table.app} / ${table.fields.length} fields / ${related.length} direct relationships</div>
          <div class="field-grid" style="margin-top: 8px">${fieldRows}</div>
        </div>
        <div>
          <h3>Direct Relationships</h3>
          <div class="relationship-list">${relationshipRows}</div>
        </div>
      `;
      renderTables();
    }

    overviewButton.addEventListener("click", () => showDiagram("overview", "overview"));
    diagram.addEventListener("load", installSvgInteractivity);
    search.addEventListener("input", renderTables);
    refreshEr.addEventListener("click", refreshFromDatabase);
    document.getElementById("zoomOut").addEventListener("click", () => setZoom(zoom - .15));
    document.getElementById("zoomIn").addEventListener("click", () => setZoom(zoom + .15));
    document.getElementById("zoomReset").addEventListener("click", () => setZoom(1));
    viewport.addEventListener("wheel", (event) => {
      if (!event.ctrlKey && !event.metaKey) return;
      event.preventDefault();
      setZoom(zoom + (event.deltaY < 0 ? .1 : -.1));
    }, { passive: false });

    renderApps();
    renderTables();
    showDiagram("overview", "overview");
  </script>
</body>
</html>
"""


def write_schema_js(
    tables: dict[str, dict],
    relationships: list[dict],
    tables_by_app: dict[str, list[str]],
    apps_by_table: dict[str, str],
    diagrams: dict[str, dict],
) -> None:
    app_relationships = Counter()
    for relation in relationships:
        app_relationships[apps_by_table[relation["src"]]] += 1
        app_relationships[apps_by_table[relation["dst"]]] += 1

    data = {
        "source": "docs/db_er_diagram.mmd",
        "generatedAt": datetime.now().isoformat(timespec="seconds"),
        "stats": {
            "tables": len(tables),
            "relationships": len(relationships),
            "apps": len(tables_by_app),
        },
        "apps": [
            {
                "name": app,
                "tableCount": len(tables_by_app[app]),
                "relationshipCount": app_relationships[app],
            }
            for app in sorted(tables_by_app)
        ],
        "tables": [
            {
                "name": name,
                "app": apps_by_table[name],
                "fields": tables[name]["fields"],
            }
            for name in sorted(tables)
        ],
        "relationships": relationships,
        "diagrams": diagrams,
    }
    (OUT_DIR / "schema.js").write_text(
        "window.ER_SCHEMA = " + json.dumps(data, indent=2) + ";\n",
        encoding="utf-8",
    )


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    APP_DIR.mkdir(parents=True, exist_ok=True)
    NEIGHBORHOOD_DIR.mkdir(parents=True, exist_ok=True)
    for directory in (APP_DIR, NEIGHBORHOOD_DIR):
        for old_svg in directory.glob("*.svg"):
            old_svg.unlink()

    tables, relationships = parse_mermaid(SOURCE.read_text(encoding="utf-8"))
    apps = discover_apps(tables)
    apps_by_table = {table: app_for(table, apps) for table in tables}
    tables_by_app: dict[str, list[str]] = defaultdict(list)
    for table in sorted(tables):
        tables_by_app[apps_by_table[table]].append(table)

    degree = Counter()
    for relation in relationships:
        degree[relation["src"]] += 1
        degree[relation["dst"]] += 1

    diagrams: dict[str, dict] = {}

    svg, width, height = overview_diagram(tables_by_app, relationships, apps_by_table)
    (OUT_DIR / "overview.svg").write_text(svg, encoding="utf-8")
    diagrams["overview"] = {"title": "Overview", "src": "overview.svg", "width": width, "height": height}

    for app in sorted(tables_by_app):
        svg, width, height = app_diagram(app, tables, apps_by_table, relationships, tables_by_app, degree)
        path = APP_DIR / f"{slug(app)}.svg"
        path.write_text(svg, encoding="utf-8")
        diagrams[f"app:{app}"] = {
            "title": f"{app.replace('_', ' ').title()}",
            "src": f"apps/{path.name}",
            "width": width,
            "height": height,
        }

    for table in sorted(tables):
        svg, width, height = neighborhood_diagram(table, tables, apps_by_table, relationships, degree)
        path = NEIGHBORHOOD_DIR / f"{slug(table)}.svg"
        path.write_text(svg, encoding="utf-8")
        diagrams[f"table:{table}"] = {
            "title": f"{table} Neighborhood",
            "src": f"neighborhoods/{path.name}",
            "width": width,
            "height": height,
        }

    write_schema_js(tables, relationships, tables_by_app, apps_by_table, diagrams)
    (OUT_DIR / "index.html").write_text(build_index_html(), encoding="utf-8")

    print(f"Wrote {OUT_DIR / 'index.html'}")
    print(f"Apps: {len(tables_by_app)} | tables: {len(tables)} | relationships: {len(relationships)}")
    print(f"SVGs: {1 + len(tables_by_app) + len(tables)}")


if __name__ == "__main__":
    main()
