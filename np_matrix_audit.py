#!/usr/bin/env python3
"""
Matrix Node Provider Room Membership Audit

For each Node Provider, checks:
1. Does their dedicated room exist?
2. Is the NP handle in General?
3. Is the NP handle in Announcements?
4. Is the NP handle in Incident Response?
"""

import os
import json
import requests
from typing import Optional, Set
from dotenv import load_dotenv

load_dotenv()

HOMESERVER = os.getenv("MATRIX_HOMESERVER", "https://matrix.org")
ACCESS_TOKEN = os.getenv("MATRIX_ACCESS_TOKEN")

MANDATORY_ROOMS = {
    "general": "#ic-node-providers:matrix.org",
    "announcements": "#ic-node-providers-announcements:matrix.org",
    "incident": "#ic-node-providers-incident-response:matrix.org",
}

NODE_PROVIDERS_ROOM = {
    "Aitubi AG": "#ic-node-provider-znw2p:matrix.org",
    "AlpineDC SA": "#ic-node-provider-mrfhx:matrix.org",
    "NOKU SA": "#ic-node-provider-64kb5:matrix.org",
    "Avalution AG": "#ic-node-provider-is2tg:matrix.org",
    "CoreLedger": "#ic-node-provider-g4gfo:matrix.org",
    "Blockchain Innovation Group": "#ic-node-provider-c3i3u:matrix.org",
    "LTIN AG": "#ic-node-provider-qpwbv:matrix.org",
    "achermann.swiss": "#ic-node-provider-gjsts:matrix.org",
    "Swiss Datalink AG": "#ic-node-provider-hycj4:matrix.org",
    "senseLAN": "#ic-node-provider-f5kd2:matrix.org",
    "vestra ICT AG": "#ic-node-provider-izdfy:matrix.org",
    "SolNet": "#ic-node-provider-mf6om:matrix.org",
    "Decentralized": "#ic-node-provider-hokzb:matrix.org",
}

NODE_PROVIDERS_HANDLE = {
    "Aitubi AG": "@ic.aitubi:matrix.org",
    "AlpineDC SA": "@???",
    "NOKU SA": "@???",
    "Avalution AG": "@???",
    "CoreLedger": "@???",
    "Blockchain Innovation Group": "@???",
    "LTIN AG": "@???",
    "achermann.swiss": "@???",
    "Swiss Datalink AG": "@???",
    "senseLAN": "@???",
    "vestra ICT AG": "@???",
    "SolNet": "@???",
    "Decentralized": "@???",
}


def get_headers():
    return {"Authorization": f"Bearer {ACCESS_TOKEN}"}


def resolve_room(alias: str) -> Optional[str]:
    """Resolve room alias to room ID. Returns None if room doesn't exist."""
    encoded = alias.replace("#", "%23").replace(":", "%3A")
    try:
        resp = requests.get(f"{HOMESERVER}/_matrix/client/v3/directory/room/{encoded}",
                          headers=get_headers(), timeout=30)
        if resp.status_code == 200:
            return resp.json().get("room_id")
    except:
        pass
    return None


def get_members(room_id: str) -> Set[str]:
    """Get room members."""
    try:
        resp = requests.get(f"{HOMESERVER}/_matrix/client/v3/rooms/{room_id}/joined_members",
                          headers=get_headers(), timeout=30)
        if resp.status_code == 200:
            return set(resp.json().get("joined", {}).keys())
    except:
        pass
    return set()


def run_audit():
    if not ACCESS_TOKEN or ACCESS_TOKEN == "your_access_token_here":
        print("❌ Set MATRIX_ACCESS_TOKEN in .env file")
        return

    print("=" * 70)
    print("Node Provider Matrix Audit")
    print("=" * 70)
    
    # Get mandatory room members
    print("\nFetching mandatory rooms...")
    mandatory = {}
    for key, alias in MANDATORY_ROOMS.items():
        room_id = resolve_room(alias)
        if room_id:
            members = get_members(room_id)
            mandatory[key] = members
            print(f"  {key}: {len(members)} members")
        else:
            mandatory[key] = set()
            print(f"  {key}: ⚠ could not resolve")
    
    # Check each NP
    print("\nChecking Node Providers...")
    report = []
    
    for np_name in NODE_PROVIDERS_ROOM.keys():
        np_room = NODE_PROVIDERS_ROOM[np_name]
        np_handle = NODE_PROVIDERS_HANDLE[np_name]
        
        # 1. Does room exist?
        room_id = resolve_room(np_room)
        room_exists = room_id is not None
        
        # Handle unknown?
        handle_unknown = np_handle == "@???"
        
        # 2-4. Is NP handle in mandatory rooms?
        if handle_unknown:
            in_general = None  # Unknown
            in_announcements = None
            in_incident = None
            fully_compliant = None
        else:
            in_general = np_handle in mandatory["general"]
            in_announcements = np_handle in mandatory["announcements"]
            in_incident = np_handle in mandatory["incident"]
            fully_compliant = all([room_exists, in_general, in_announcements, in_incident])
        
        report.append({
            "np_name": np_name,
            "np_room": np_room,
            "np_handle": np_handle,
            "room_exists": room_exists,
            "in_general": in_general,
            "in_announcements": in_announcements,
            "in_incident": in_incident,
            "fully_compliant": fully_compliant
        })
    
    # Print table
    compliant_count = sum(1 for r in report if r["fully_compliant"] == True)
    unknown_count = sum(1 for r in report if r["fully_compliant"] is None)
    
    print("\n┌" + "─"*35 + "┬" + "─"*8 + "┬" + "─"*9 + "┬" + "─"*8 + "┬" + "─"*10 + "┬" + "─"*10 + "┐")
    print(f"│ {'Node Provider':<33} │ {'Room':^6} │ {'General':^7} │ {'Announ':^6} │ {'Incident':^8} │ {'Status':^8} │")
    print("├" + "─"*35 + "┼" + "─"*8 + "┼" + "─"*9 + "┼" + "─"*8 + "┼" + "─"*10 + "┼" + "─"*10 + "┤")
    
    for r in report:
        room = "✅" if r["room_exists"] else "❌"
        
        if r["in_general"] is None:
            gen = "❓"
            ann = "❓"
            inc = "❓"
            status = "❓ ???"
        else:
            gen = "✅" if r["in_general"] else "❌"
            ann = "✅" if r["in_announcements"] else "❌"
            inc = "✅" if r["in_incident"] else "❌"
            status = "✅ OK" if r["fully_compliant"] else "⚠ GAPS"
        
        print(f"│ {r['np_name']:<33} │ {room:^6} │ {gen:^7} │ {ann:^6} │ {inc:^8} │ {status:^8} │")
    
    print("└" + "─"*35 + "┴" + "─"*8 + "┴" + "─"*9 + "┴" + "─"*8 + "┴" + "─"*10 + "┴" + "─"*10 + "┘")
    print(f"\n📊 {compliant_count} compliant, {unknown_count} unknown (missing handle)")
    
    # Save JSON
    with open("np_audit_report.json", "w") as f:
        json.dump({
            "node_providers": report,
            "summary": {
                "total": len(report),
                "compliant": compliant_count,
                "unknown": unknown_count,
                "with_gaps": len(report) - compliant_count - unknown_count
            }
        }, f, indent=2)
    print("📁 Saved: np_audit_report.json")
    
    # Generate HTML
    from generate_html_report import generate_html_report
    generate_html_report()


if __name__ == "__main__":
    run_audit()