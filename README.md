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

## Output

The script produces:
- A summary table showing which rooms each NP has joined
- A detailed gap list for non-compliant NPs
- A JSON report (`np_audit_report.json`) for further processing

## Important Notes

- Your Matrix account must be a **member of all rooms** you want to audit (or the rooms must be publicly viewable)
- If you get 403 errors, you may need to join those rooms first
- The script identifies NP members by checking who is in each NP's dedicated room, then cross-references with mandatory rooms

## Example Output

```
┌───────────────────────────────────┬────────┬─────────┬────────┬──────────┬──────────┐
│ Node Provider                     │  Own   │ General │ Announ │ Incident │  Status  │
├───────────────────────────────────┼────────┼─────────┼────────┼──────────┼──────────┤
│ Aitubi AG                         │   ✅   │   ✅    │   ✅   │    ✅    │   ✅ OK  │
│ AlpineDC SA                       │   ✅   │   ❌    │   ❌   │    ❌    │  ⚠ GAPS │
...
```
