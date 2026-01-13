#!/usr/bin/env python3
"""
HTML Report Generator for Matrix NP Audit
Styled to match Swiss Subnet branding (subnet.ch)
"""

import json
from datetime import datetime


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
    
    report = data.get("node_providers", [])
    summary = data.get("summary", {})
    compliant_count = summary.get("compliant", 0)
    total_count = summary.get("total", len(report))
    unknown_count = summary.get("unknown", 0)
    gap_count = summary.get("with_gaps", total_count - compliant_count - unknown_count)
    
    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Node Provider Matrix Audit Report</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #ffffff;
            min-height: 100vh;
            padding: 60px 40px;
            color: #1a1a1a;
            line-height: 1.6;
        }
        .container { max-width: 1100px; margin: 0 auto; }
        .header { margin-bottom: 50px; }
        .logo {
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 40px;
        }
        .logo-icon {
            width: 32px;
            height: 32px;
            background: #E53935;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
            font-size: 18px;
        }
        .logo-text {
            font-size: 0.75rem;
            font-weight: 600;
            letter-spacing: 0.5px;
            text-transform: uppercase;
            line-height: 1.2;
        }
        h1 {
            font-size: 3.5rem;
            font-weight: 700;
            line-height: 1.1;
            margin-bottom: 20px;
            color: #1a1a1a;
        }
        h1 span { color: #E53935; }
        .subtitle {
            font-size: 1.1rem;
            color: #666;
            max-width: 500px;
        }
        .summary {
            display: flex;
            gap: 40px;
            margin: 50px 0;
            padding: 30px 0;
            border-top: 1px solid #eee;
            border-bottom: 1px solid #eee;
        }
        .summary-card { text-align: left; }
        .summary-card .number {
            font-size: 3rem;
            font-weight: 700;
            color: #1a1a1a;
            line-height: 1;
        }
        .summary-card.warning .number { color: #E53935; }
        .summary-card.success .number { color: #2E7D32; }
        .summary-card.unknown .number { color: #FF9800; }
        .summary-card .label {
            color: #888;
            font-size: 0.85rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-top: 8px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 30px;
        }
        th {
            text-align: left;
            padding: 12px 16px;
            font-weight: 600;
            text-transform: uppercase;
            font-size: 0.75rem;
            letter-spacing: 0.5px;
            color: #888;
            border-bottom: 2px solid #1a1a1a;
        }
        th:not(:first-child) { text-align: center; }
        td {
            padding: 16px;
            border-bottom: 1px solid #eee;
            font-size: 0.95rem;
        }
        td:not(:first-child) { text-align: center; }
        tr:hover { background: #fafafa; }
        .status-ok { color: #2E7D32; font-weight: 600; }
        .status-gap { color: #E53935; font-weight: 600; }
        .status-unknown { color: #FF9800; font-weight: 600; }
        .check { color: #2E7D32; font-size: 1.1rem; }
        .cross { color: #E53935; font-size: 1.1rem; }
        .unknown { color: #FF9800; font-size: 1.1rem; }
        .np-name { font-weight: 600; color: #1a1a1a; }
        .np-handle {
            font-size: 0.75rem;
            color: #999;
            font-family: 'SF Mono', Monaco, monospace;
            margin-top: 4px;
        }
        .np-handle.missing { color: #FF9800; }
        .legend {
            margin-top: 30px;
            color: #888;
            font-size: 0.85rem;
        }
        .legend span { margin-right: 24px; }
        .timestamp {
            margin-top: 40px;
            color: #ccc;
            font-size: 0.8rem;
        }
        .gap-section {
            margin-top: 60px;
            padding-top: 40px;
            border-top: 1px solid #eee;
        }
        .gap-section h2 {
            font-size: 1.5rem;
            font-weight: 700;
            margin-bottom: 24px;
            color: #1a1a1a;
        }
        .gap-item {
            background: #fff;
            border-left: 3px solid #E53935;
            padding: 20px 24px;
            margin-bottom: 16px;
        }
        .gap-item.unknown { border-left-color: #FF9800; }
        .gap-item h3 {
            color: #1a1a1a;
            font-size: 1rem;
            font-weight: 600;
            margin-bottom: 8px;
        }
        .gap-item p {
            color: #666;
            font-size: 0.9rem;
            margin: 4px 0;
        }
        .gap-item code {
            background: #f5f5f5;
            padding: 2px 6px;
            border-radius: 3px;
            font-size: 0.8rem;
        }
        .gap-item .missing { color: #E53935; font-weight: 500; }
        .all-compliant {
            background: #E8F5E9;
            border-left: 3px solid #2E7D32;
            padding: 24px;
        }
        .all-compliant h2 { color: #2E7D32; margin: 0; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo">
                <div class="logo-icon">+</div>
                <div class="logo-text">Swiss Subnet<br>Node Provider Audit</div>
            </div>
            <h1>Matrix Room<br><span>Compliance</span></h1>
            <p class="subtitle">Audit report showing which Node Providers have joined the required Matrix communication channels.</p>
        </div>
        
        <div class="summary">
            <div class="summary-card success">
                <div class="number">COMPLIANT_COUNT</div>
                <div class="label">Fully Compliant</div>
            </div>
            <div class="summary-card warning">
                <div class="number">GAP_COUNT</div>
                <div class="label">With Gaps</div>
            </div>
            <div class="summary-card unknown">
                <div class="number">UNKNOWN_COUNT</div>
                <div class="label">Unknown Handle</div>
            </div>
            <div class="summary-card">
                <div class="number">TOTAL_COUNT</div>
                <div class="label">Total NPs</div>
            </div>
        </div>
        
        <table>
            <thead>
                <tr>
                    <th>Node Provider</th>
                    <th>Room</th>
                    <th>General</th>
                    <th>Announcements</th>
                    <th>Incident</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
TABLE_ROWS
            </tbody>
        </table>
        
        <div class="legend">
            <span>✓ Yes</span>
            <span>✗ No</span>
            <span>? Unknown</span>
        </div>

GAP_SECTION
        
        <p class="timestamp">Generated: TIMESTAMP</p>
    </div>
</body>
</html>"""
    
    # Generate table rows
    rows = []
    for r in report:
        room = '<span class="check">✓</span>' if r.get("room_exists") else '<span class="cross">✗</span>'
        
        handle = r.get("np_handle", "@???")
        handle_class = "np-handle missing" if handle == "@???" else "np-handle"
        
        if r.get("in_general") is None:
            gen = '<span class="unknown">?</span>'
            ann = '<span class="unknown">?</span>'
            inc = '<span class="unknown">?</span>'
            status = '<span class="status-unknown">???</span>'
        else:
            gen = '<span class="check">✓</span>' if r["in_general"] else '<span class="cross">✗</span>'
            ann = '<span class="check">✓</span>' if r["in_announcements"] else '<span class="cross">✗</span>'
            inc = '<span class="check">✓</span>' if r["in_incident"] else '<span class="cross">✗</span>'
            status = '<span class="status-ok">OK</span>' if r.get("fully_compliant") else '<span class="status-gap">GAPS</span>'
        
        row = f"""                <tr>
                    <td>
                        <div class="np-name">{r['np_name']}</div>
                        <div class="{handle_class}">{handle}</div>
                    </td>
                    <td>{room}</td>
                    <td>{gen}</td>
                    <td>{ann}</td>
                    <td>{inc}</td>
                    <td>{status}</td>
                </tr>"""
        rows.append(row)
    
    # Generate gap section
    gap_items = []
    for r in report:
        if r.get("fully_compliant") == True:
            continue
            
        handle = r.get("np_handle", "@???")
        
        if r.get("in_general") is None:
            # Unknown handle
            gap_items.append(f"""            <div class="gap-item unknown">
                <h3>{r['np_name']}</h3>
                <p>Room: <code>{r.get('np_room', 'N/A')}</code></p>
                <p class="missing">⚠ Missing Matrix handle - cannot check room membership</p>
            </div>""")
        else:
            gaps = []
            if not r.get("room_exists"):
                gaps.append("Room doesn't exist")
            if not r.get("in_general"):
                gaps.append("#ic-node-providers")
            if not r.get("in_announcements"):
                gaps.append("#ic-node-providers-announcements")
            if not r.get("in_incident"):
                gaps.append("#ic-node-providers-incident-response")
            
            if gaps:
                gap_items.append(f"""            <div class="gap-item">
                <h3>{r['np_name']}</h3>
                <p>Handle: <code>{handle}</code></p>
                <p class="missing">Missing: {', '.join(gaps)}</p>
            </div>""")
    
    if gap_items:
        gap_section = f"""
        <div class="gap-section">
            <h2>Detailed Gap List</h2>
{"".join(gap_items)}
        </div>"""
    else:
        gap_section = """
        <div class="gap-section">
            <div class="all-compliant">
                <h2>All Node Providers are fully compliant</h2>
            </div>
        </div>"""
    
    # Fill in template
    html = html.replace("COMPLIANT_COUNT", str(compliant_count))
    html = html.replace("GAP_COUNT", str(gap_count))
    html = html.replace("UNKNOWN_COUNT", str(unknown_count))
    html = html.replace("TOTAL_COUNT", str(total_count))
    html = html.replace("TABLE_ROWS", "\n".join(rows))
    html = html.replace("GAP_SECTION", gap_section)
    html = html.replace("TIMESTAMP", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    with open(output_file, "w") as f:
        f.write(html)
    
    print(f"✅ HTML report generated: {output_file}")


if __name__ == "__main__":
    generate_html_report()