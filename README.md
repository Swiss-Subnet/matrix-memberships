# Matrix Node Provider Audit Tool

Audit script to check which Swiss Subnet Node Providers have joined the required Matrix rooms.

## Required Rooms (per NP)

1. **General Discussion**: `#ic-node-providers:matrix.org`
2. **Announcements**: `#ic-node-providers-announcements:matrix.org`
3. **Incident Response**: `#ic-node-providers-incident-response:matrix.org`
4. **Their own NP room** (e.g., `#ic-node-provider-znw2p:matrix.org`)

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   
   Or use a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. Copy the example env file and add your Matrix access token:
   ```bash
   cp .env.example .env
   ```

3. Get your Matrix access token from Element:
   - Open Element (web or desktop)
   - Go to **Settings** → **Help & About** → **Advanced**
   - Click to reveal your **Access Token**
   - Copy it to your `.env` file

## Usage

```bash
python np_matrix_audit.py
```

This will:
1. Fetch membership data from Matrix API
2. Generate `np_audit_report.json`
3. Generate `np_audit_report.html`

Then open `np_audit_report.html` in your browser to view the results.

### Regenerate HTML Only

If you already have the JSON and just want to regenerate the HTML:

```bash
python generate_html_report.py
```

## Output Files

| File | Description |
|------|-------------|
| `np_audit_report.json` | Raw audit data in JSON format |
| `np_audit_report.html` | Beautiful HTML report for viewing in browser |

## Web App (GitHub Pages)

`index.html` is a self-contained browser app that runs the same audit without any server-side code.

**Run locally:**
```bash
python -m http.server 8000
# open http://localhost:8000
```

Enter your Matrix homeserver URL and access token in the UI, then click **Run Audit**. Results appear inline with color-coded cells for instant visual spot checks — red cells mark missing memberships immediately.

> The Matrix client-server API supports CORS, so the browser can call it directly without a proxy.

## Scripts

| Script | Purpose |
|--------|---------|
| `np_matrix_audit.py` | Main audit script - fetches data from Matrix API |
| `generate_html_report.py` | Generates HTML report from JSON data |

## Configuration

`config.json` is the single source of truth for room aliases and Node Provider handles. Both the Python script and the web app read from it. Edit this file to add/remove NPs or rooms.

## Important Notes

- Your Matrix account must be a **member of all rooms** you want to audit (or the rooms must be publicly viewable)
- If you get 403 errors, you may need to join those rooms first
- The script identifies NP members by checking who is in each NP's dedicated room, then cross-references with mandatory rooms