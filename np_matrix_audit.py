#!/usr/bin/env python3
"""
Matrix Node Provider Room Membership Audit

For each Node Provider, checks:
1. Is the NP handle in their own room?
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

_config_path = os.path.join(os.path.dirname(__file__), "config.json")
with open(_config_path) as _f:
    _config = json.load(_f)

MANDATORY_ROOMS = _config["mandatory_rooms"]
NODE_PROVIDERS_ROOM = {np["name"]: np["room"] for np in _config["node_providers"]}
NODE_PROVIDERS_HANDLE = {np["name"]: np["handle"] for np in _config["node_providers"]}


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
        
        # Handle unknown?
        handle_unknown = np_handle == "@???"
        
        if handle_unknown:
            in_general = None
            in_announcements = None
            in_incident = None
            in_swiss_subnet = None
            fully_compliant = None
        else:
            # 1. Is NP in their own room?
            own_room_id = resolve_room(np_room)
            if own_room_id:
                own_room_members = get_members(own_room_id)
                in_own_room = np_handle in own_room_members
            else:
                in_own_room = False
            
            # 2-4. Is NP in mandatory rooms?
            in_general = np_handle in mandatory["general"]
            in_announcements = np_handle in mandatory["announcements"]
            in_incident = np_handle in mandatory["incident"]
            in_swiss_subnet = np_handle in mandatory["swiss_subnet"]
            fully_compliant = all([in_own_room, in_general, in_announcements, in_incident, in_swiss_subnet])
        
        report.append({
            "np_name": np_name,
            "np_room": np_room,
            "np_handle": np_handle,
            "in_own_room": in_own_room,
            "in_general": in_general,
            "in_announcements": in_announcements,
            "in_incident": in_incident,
            "in_swiss_subnet": in_swiss_subnet,
            "fully_compliant": fully_compliant
        })
    
    # Print table
    compliant_count = sum(1 for r in report if r["fully_compliant"] == True)
    unknown_count = sum(1 for r in report if r["fully_compliant"] is None)
    
    print("\n┌" + "─"*35 + "┬" + "─"*10 + "┬" + "─"*9 + "┬" + "─"*8 + "┬" + "─"*10 + "┬" + "─"*14 + "┬" + "─"*10 + "┐")
    print(f"│ {'Node Provider':<33} │ {'Own Room':^8} │ {'General':^7} │ {'Announ':^6} │ {'Incident':^8} │ {'Swiss Subnet':^12} │ {'Status':^8} │")
    print("├" + "─"*35 + "┼" + "─"*10 + "┼" + "─"*9 + "┼" + "─"*8 + "┼" + "─"*10 + "┼" + "─"*14 + "┼" + "─"*10 + "┤")
        
    for r in report:
        if r["in_general"] is None:
            own = "❓"
            gen = "❓"
            ann = "❓"
            inc = "❓"
            swiss = "❓"
            status = "❓ ???"
        else:
            own = "✅" if r["in_own_room"] else "❌"
            gen = "✅" if r["in_general"] else "❌"
            ann = "✅" if r["in_announcements"] else "❌"
            inc = "✅" if r["in_incident"] else "❌"
            swiss = "✅" if r["in_swiss_subnet"] else "❌"
            status = "✅ OK" if r["fully_compliant"] else "⚠ GAPS"
        
        print(f"│ {r['np_name']:<33} │ {own:^8} │ {gen:^7} │ {ann:^6} │ {inc:^8} │ {swiss:^12} │ {status:^8} │")
    
    print("└" + "─"*35 + "┴" + "─"*10 + "┴" + "─"*9 + "┴" + "─"*8 + "┴" + "─"*10 + "┴" + "─"*14 + "┴" + "─"*10 + "┘")
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
