# Matrix Room Compliance Audit

Checks which Swiss Subnet Node Providers have joined the required Matrix rooms.

## Web App

The primary way to run the audit. No installation required — runs directly in the browser.

**Live:** [swiss-subnet.github.io/matrix-memberships](https://swiss-subnet.github.io/matrix-memberships)

Enter your Matrix homeserver URL and access token, click **Run Audit**. Results appear as a color-coded table — red cells mark missing memberships at a glance. Credentials are saved in your browser's local storage so you don't have to re-enter them on every visit.

To get your Matrix access token from Element:
- Go to **Settings** → **Help & About** → **Advanced**
- Click to reveal your **Access Token**

**Run locally:**
```bash
python -m http.server 8000
# open http://localhost:8000
```

> The Matrix client-server API supports CORS, so the browser calls it directly — no proxy or server needed.

## Configuration

`config.json` is the single source of truth for room aliases and Node Provider handles. Edit this file to add, remove, or update NPs and rooms. Both the web app and the Python script read from it.

## Required Rooms (per NP)

1. **General Discussion**: `#ic-node-providers:matrix.org`
2. **Announcements**: `#ic-node-providers-announcements:matrix.org`
3. **Incident Response**: `#ic-node-providers-incident-response:matrix.org`
4. **Swiss Subnet**: `#ic-rented-subnet-swiss:matrix.org`
5. **Their own NP room** (e.g., `#ic-node-provider-znw2p:matrix.org`)

## Python Script (deprecated)

> The Python script is being decommissioned. Use the web app above.

<details>
<summary>Python script usage</summary>

Install dependencies:
```bash
pip install -r requirements.txt
```

Copy the example env file and add your Matrix access token:
```bash
cp .env.example .env
```

Run the audit:
```bash
python np_matrix_audit.py
```

This fetches membership data from the Matrix API and generates `np_audit_report.json` and `np_audit_report.html`.

To regenerate the HTML from existing JSON:
```bash
python generate_html_report.py
```

</details>
