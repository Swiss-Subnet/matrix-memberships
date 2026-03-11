#!/usr/bin/env python3
"""
HTML Report Generator for Matrix NP Audit
"""

import json
from datetime import datetime


CSS = """
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

    body {
      font-family: system-ui, -apple-system, 'Segoe UI', sans-serif;
      background: #f4f4f5;
      color: #111;
      min-height: 100vh;
      font-size: 14px;
    }

    .page { max-width: 1100px; margin: 0 auto; padding: 40px 24px 80px; }

    .header { margin-bottom: 32px; }
    .header-eyebrow {
      font-size: 12px;
      font-weight: 600;
      letter-spacing: 0.02em;
      color: #888;
      margin-bottom: 8px;
    }
    .header h1 { font-size: 28px; font-weight: 700; line-height: 1.2; color: #111; }
    .header h1 span { color: #c62828; }
    .header .timestamp { font-size: 12px; color: #aaa; margin-top: 8px; }

    .summary {
      display: flex;
      gap: 0;
      background: #fff;
      border: 1px solid #e0e0e0;
      margin-bottom: 24px;
    }
    .summary-cell { flex: 1; padding: 16px 20px; border-right: 1px solid #e0e0e0; }
    .summary-cell:last-child { border-right: none; }
    .summary-cell .num { font-size: 28px; font-weight: 700; line-height: 1; }
    .summary-cell .lbl { font-size: 12px; font-weight: 500; color: #888; margin-top: 6px; }
    .summary-cell.ok .num      { color: #2e7d32; }
    .summary-cell.gap .num     { color: #c62828; }
    .summary-cell.unknown .num { color: #e65100; }
    .summary-cell.total .num   { color: #111; }

    .table-wrap { background: #fff; border: 1px solid #e0e0e0; overflow-x: auto; }
    table { width: 100%; border-collapse: collapse; }
    thead th {
      background: #fff;
      border-bottom: 2px solid #111;
      padding: 10px 14px;
      text-align: center;
      font-size: 12px;
      font-weight: 600;
      color: #555;
      white-space: nowrap;
    }
    thead th:first-child { text-align: left; min-width: 180px; }
    thead th:last-child { border-left: 1px solid #e0e0e0; }

    tbody td {
      padding: 10px 14px;
      border-bottom: 1px solid #f0f0f0;
      text-align: center;
      vertical-align: middle;
    }
    tbody td:first-child { text-align: left; }
    tbody td:last-child { border-left: 1px solid #e0e0e0; }
    tbody tr:last-child td { border-bottom: none; }

    .cell-ok      { background: #f1f8f1; color: #2e7d32; font-size: 15px; font-weight: 700; }
    .cell-gap     { background: #fdf0f0; color: #c62828; font-size: 15px; font-weight: 700; }
    .cell-unknown { background: #fdf7ee; color: #e65100; font-size: 15px; font-weight: 700; }

    .np-name { font-weight: 600; font-size: 13px; }
    .np-handle {
      font-size: 11px; color: #999;
      font-family: 'SF Mono', 'Fira Mono', monospace;
      margin-top: 2px;
    }
    .np-handle.missing { color: #e65100; }

    .badge { display: inline-block; padding: 3px 8px; font-size: 11px; font-weight: 700; letter-spacing: 0.04em; }
    .badge-ok      { background: #e8f5e9; color: #2e7d32; }
    .badge-gap     { background: #ffebee; color: #c62828; }
    .badge-unknown { background: #fff3e0; color: #e65100; }

    .gaps-section { margin-top: 24px; border: 1px solid #e0e0e0; background: #fff; }
    .gaps-heading {
      padding: 14px 16px;
      font-size: 13px;
      font-weight: 600;
      border-bottom: 1px solid #e0e0e0;
      color: #111;
    }
    .gaps-body { padding: 8px 16px 16px; }

    .gap-card {
      border-left: 3px solid #c62828;
      padding: 12px 16px;
      margin-top: 12px;
      background: #fdf0f0;
    }
    .gap-card.unknown-card { border-left-color: #e65100; background: #fdf7ee; }
    .gap-card h4 { font-size: 13px; font-weight: 600; margin-bottom: 4px; }
    .gap-card .gap-handles { font-size: 11px; font-family: 'SF Mono', 'Fira Mono', monospace; color: #666; margin-bottom: 6px; }
    .gap-card .gap-missing { font-size: 12px; color: #c62828; }
    .gap-card.unknown-card .gap-missing { color: #e65100; }
"""


def cell(value) -> str:
    if value is True:
        return '<td class="cell-ok">✓</td>'
    if value is False:
        return '<td class="cell-gap">✗</td>'
    return '<td class="cell-unknown">?</td>'


def badge(r: dict) -> str:
    if r["fully_compliant"] is True:
        return '<span class="badge badge-ok">OK</span>'
    if r["fully_compliant"] is False:
        return '<span class="badge badge-gap">GAPS</span>'
    return '<span class="badge badge-unknown">???</span>'


def handles_html(handles: list) -> str:
    if not handles:
        return '<div class="np-handle missing">No handles configured</div>'
    return "".join(f'<div class="np-handle">{h}</div>' for h in handles)


def generate_html_report(input_file: str = "np_audit_report.json", output_file: str = "np_audit_report.html"):
    """Generate HTML report from JSON data."""
    try:
        with open(input_file, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"❌ Error: {input_file} not found. Run np_matrix_audit.py first.")
        return
    except json.JSONDecodeError:
        print(f"❌ Error: {input_file} is not valid JSON.")
        return

    report   = data.get("node_providers", [])
    summary  = data.get("summary", {})
    total    = summary.get("total", len(report))
    compliant = summary.get("compliant", 0)
    unknown  = summary.get("unknown", 0)
    gaps     = summary.get("with_gaps", total - compliant - unknown)
    ts       = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Table rows
    rows = []
    for r in report:
        handles = r.get("np_handles", [])
        rows.append(f"""
            <tr>
              <td>
                <div class="np-name">{r['np_name']}</div>
                {handles_html(handles)}
              </td>
              {cell(r.get("in_own_room"))}
              {cell(r.get("in_general"))}
              {cell(r.get("in_announcements"))}
              {cell(r.get("in_incident"))}
              {cell(r.get("in_swiss_subnet"))}
              <td>{badge(r)}</td>
            </tr>""")

    # Gap cards
    gap_cards = []
    for r in report:
        if r.get("fully_compliant") is True:
            continue
        handles = r.get("np_handles", [])
        if r.get("fully_compliant") is None:
            gap_cards.append(f"""
            <div class="gap-card unknown-card">
              <h4>{r['np_name']}</h4>
              <div class="gap-missing">No handles configured — cannot check room membership</div>
            </div>""")
        else:
            missing = []
            if not r.get("in_own_room"):      missing.append("Own room")
            if not r.get("in_general"):       missing.append("#ic-node-providers")
            if not r.get("in_announcements"): missing.append("#ic-node-providers-announcements")
            if not r.get("in_incident"):      missing.append("#ic-node-providers-incident-response")
            if not r.get("in_swiss_subnet"):  missing.append("#ic-rented-subnet-swiss")
            handles_str = ", ".join(handles)
            gap_cards.append(f"""
            <div class="gap-card">
              <h4>{r['np_name']}</h4>
              <div class="gap-handles">{handles_str}</div>
              <div class="gap-missing">Missing: {", ".join(missing)}</div>
            </div>""")

    gaps_section = ""
    if gap_cards:
        gaps_section = f"""
    <div class="gaps-section">
      <div class="gaps-heading">Detailed Gap List</div>
      <div class="gaps-body">{"".join(gap_cards)}
      </div>
    </div>"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Matrix Room Compliance Audit</title>
  <style>{CSS}
  </style>
</head>
<body>
<div class="page">

  <div class="header">
    <div class="header-eyebrow">Swiss Subnet · Internet Computer</div>
    <h1>Matrix Room <span>Compliance</span> Audit</h1>
    <div class="timestamp">Generated: {ts}</div>
  </div>

  <div class="summary">
    <div class="summary-cell ok">
      <div class="num">{compliant}</div>
      <div class="lbl">Fully Compliant</div>
    </div>
    <div class="summary-cell gap">
      <div class="num">{gaps}</div>
      <div class="lbl">With Gaps</div>
    </div>
    <div class="summary-cell unknown">
      <div class="num">{unknown}</div>
      <div class="lbl">Unknown Handle</div>
    </div>
    <div class="summary-cell total">
      <div class="num">{total}</div>
      <div class="lbl">Total NPs</div>
    </div>
  </div>

  <div class="table-wrap">
    <table>
      <thead>
        <tr>
          <th>Node Provider</th>
          <th>Own Room</th>
          <th>General</th>
          <th>Announcements</th>
          <th>Incident</th>
          <th>Swiss Subnet</th>
          <th>Status</th>
        </tr>
      </thead>
      <tbody>{"".join(rows)}
      </tbody>
    </table>
  </div>
{gaps_section}
</div>
</body>
</html>"""

    with open(output_file, "w") as f:
        f.write(html)
    print(f"✅ HTML report generated: {output_file}")


if __name__ == "__main__":
    generate_html_report()
