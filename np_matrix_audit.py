#!/usr/bin/env python3
"""
Matrix Node Provider Room Membership Audit Script

This script checks which Node Providers (NPs) have joined the mandatory Matrix rooms
and their own dedicated NP room.

Usage:
    1. Copy .env.example to .env and add your Matrix access token
    2. Run: python np_matrix_audit.py
"""

import os
import json
import requests
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

# Configuration
HOMESERVER = os.getenv("MATRIX_HOMESERVER", "https://matrix.org")
ACCESS_TOKEN = os.getenv("MATRIX_ACCESS_TOKEN")

# Mandatory rooms all NPs must join
MANDATORY_ROOMS = {
    "general": "#ic-node-providers:matrix.org",
    "announcements": "#ic-node-providers-announcements:matrix.org",
    "incident": "#ic-node-providers-incident-response:matrix.org",
}

# Node Providers and their dedicated rooms
NODE_PROVIDERS = {
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


@dataclass
class RoomInfo:
    alias: str
    room_id: Optional[str] = None
    members: list = None
    error: Optional[str] = None

    def __post_init__(self):
        if self.members is None:
            self.members = []


class MatrixClient:
    def __init__(self, homeserver: str, access_token: str):
        self.homeserver = homeserver.rstrip("/")
        self.access_token = access_token
        self.headers = {"Authorization": f"Bearer {access_token}"}

    def resolve_room_alias(self, alias: str) -> Optional[str]:
        """Resolve a room alias to a room ID."""
        encoded_alias = alias.replace("#", "%23").replace(":", "%3A")
        url = f"{self.homeserver}/_matrix/client/v3/directory/room/{encoded_alias}"
        
        try:
            resp = requests.get(url, headers=self.headers, timeout=30)
            if resp.status_code == 200:
                return resp.json().get("room_id")
            else:
                print(f"  ⚠ Failed to resolve {alias}: {resp.status_code} - {resp.text[:100]}")
                return None
        except Exception as e:
            print(f"  ⚠ Error resolving {alias}: {e}")
            return None

    def get_room_members(self, room_id: str) -> list:
        """Get list of joined members in a room."""
        url = f"{self.homeserver}/_matrix/client/v3/rooms/{room_id}/joined_members"
        
        try:
            resp = requests.get(url, headers=self.headers, timeout=30)
            if resp.status_code == 200:
                joined = resp.json().get("joined", {})
                return list(joined.keys())
            elif resp.status_code == 403:
                return self._get_members_via_state(room_id)
            else:
                print(f"  ⚠ Failed to get members for {room_id}: {resp.status_code}")
                return []
        except Exception as e:
            print(f"  ⚠ Error getting members: {e}")
            return []

    def _get_members_via_state(self, room_id: str) -> list:
        """Alternative method to get members via room state."""
        url = f"{self.homeserver}/_matrix/client/v3/rooms/{room_id}/members"
        params = {"membership": "join"}
        
        try:
            resp = requests.get(url, headers=self.headers, params=params, timeout=30)
            if resp.status_code == 200:
                members = []
                for event in resp.json().get("chunk", []):
                    if event.get("content", {}).get("membership") == "join":
                        members.append(event.get("state_key"))
                return members
            else:
                return []
        except Exception:
            return []

    def get_room_info(self, alias: str) -> RoomInfo:
        """Get full room info including members."""
        info = RoomInfo(alias=alias)
        info.room_id = self.resolve_room_alias(alias)
        if not info.room_id:
            info.error = "Could not resolve room alias"
            return info
        info.members = self.get_room_members(info.room_id)
        return info


def run_audit():
    """Run the full NP Matrix room audit."""
    
    if not ACCESS_TOKEN or ACCESS_TOKEN == "your_access_token_here":
        print("❌ Error: Please set MATRIX_ACCESS_TOKEN in your .env file")
        print("\nTo get your access token:")
        print("  1. Open Element")
        print("  2. Go to Settings > Help & About > Advanced")
        print("  3. Click to reveal and copy your Access Token")
        return

    print("=" * 70)
    print("Matrix Node Provider Room Membership Audit")
    print("=" * 70)
    
    client = MatrixClient(HOMESERVER, ACCESS_TOKEN)
    
    # Step 1: Get members of mandatory rooms
    print("\n📋 Fetching mandatory room memberships...")
    mandatory_room_info = {}
    mandatory_members = {}
    
    for key, alias in MANDATORY_ROOMS.items():
        print(f"  Checking {key}: {alias}")
        info = client.get_room_info(alias)
        mandatory_room_info[key] = info
        mandatory_members[key] = set(info.members)
        print(f"    → {len(info.members)} members")
    
    # Step 2: Get members of each NP room
    print("\n📋 Fetching NP room memberships...")
    np_room_info = {}
    
    for np_name, alias in NODE_PROVIDERS.items():
        print(f"  Checking {np_name}: {alias}")
        info = client.get_room_info(alias)
        np_room_info[np_name] = info
        if info.error:
            print(f"    → ⚠ {info.error}")
        else:
            print(f"    → {len(info.members)} members")
    
    # Step 3: Build gap assessment
    print("\n" + "=" * 70)
    print("GAP ASSESSMENT REPORT")
    print("=" * 70)
    
    np_to_members = {}
    for np_name, info in np_room_info.items():
        np_to_members[np_name] = set(info.members)
    
    report = []
    compliant_count = 0
    
    for np_name in NODE_PROVIDERS.keys():
        np_members = np_to_members.get(np_name, set())
        
        in_general = bool(np_members & mandatory_members.get("general", set()))
        in_announcements = bool(np_members & mandatory_members.get("announcements", set()))
        in_incident = bool(np_members & mandatory_members.get("incident", set()))
        in_own_room = len(np_members) > 0
        fully_compliant = all([in_own_room, in_general, in_announcements, in_incident])
        
        if fully_compliant:
            compliant_count += 1
        
        np_handles = list(np_members) if np_members else ["(no members found)"]
        
        report.append({
            "np_name": np_name,
            "np_room": NODE_PROVIDERS[np_name],
            "members": np_handles,
            "in_own_room": in_own_room,
            "in_general": in_general,
            "in_announcements": in_announcements,
            "in_incident": in_incident,
            "fully_compliant": fully_compliant
        })
    
    # Print summary table
    print("\n┌" + "─" * 35 + "┬" + "─" * 8 + "┬" + "─" * 9 + "┬" + "─" * 8 + "┬" + "─" * 10 + "┬" + "─" * 10 + "┐")
    print(f"│ {'Node Provider':<33} │ {'Own':^6} │ {'General':^7} │ {'Announ':^6} │ {'Incident':^8} │ {'Status':^8} │")
    print("├" + "─" * 35 + "┼" + "─" * 8 + "┼" + "─" * 9 + "┼" + "─" * 8 + "┼" + "─" * 10 + "┼" + "─" * 10 + "┤")
    
    for r in report:
        own = "✅" if r["in_own_room"] else "❌"
        gen = "✅" if r["in_general"] else "❌"
        ann = "✅" if r["in_announcements"] else "❌"
        inc = "✅" if r["in_incident"] else "❌"
        status = "✅ OK" if r["fully_compliant"] else "⚠ GAPS"
        print(f"│ {r['np_name']:<33} │ {own:^6} │ {gen:^7} │ {ann:^6} │ {inc:^8} │ {status:^8} │")
    
    print("└" + "─" * 35 + "┴" + "─" * 8 + "┴" + "─" * 9 + "┴" + "─" * 8 + "┴" + "─" * 10 + "┴" + "─" * 10 + "┘")
    
    print(f"\n📊 Summary: {compliant_count}/{len(report)} Node Providers fully compliant")
    
    # Detailed gaps
    print("\n" + "=" * 70)
    print("DETAILED GAP LIST")
    print("=" * 70)
    
    for r in report:
        if not r["fully_compliant"]:
            print(f"\n🔸 {r['np_name']}")
            print(f"   Room: {r['np_room']}")
            print(f"   Members found: {', '.join(r['members'])}")
            gaps = []
            if not r["in_own_room"]:
                gaps.append("Not in own NP room")
            if not r["in_general"]:
                gaps.append("Missing from #ic-node-providers (General)")
            if not r["in_announcements"]:
                gaps.append("Missing from #ic-node-providers-announcements")
            if not r["in_incident"]:
                gaps.append("Missing from #ic-node-providers-incident-response")
            print(f"   Gaps: {', '.join(gaps)}")
    
    # Export to JSON
    output_file = "np_audit_report.json"
    with open(output_file, "w") as f:
        json.dump({
            "mandatory_rooms": {k: {"alias": v.alias, "member_count": len(v.members)} 
                               for k, v in mandatory_room_info.items()},
            "node_providers": report,
            "summary": {
                "total": len(report),
                "compliant": compliant_count,
                "with_gaps": len(report) - compliant_count
            }
        }, f, indent=2)
    print(f"\n📁 JSON report saved to: {output_file}")
    
    # Generate HTML report
    from generate_html_report import generate_html_report
    generate_html_report()


if __name__ == "__main__":
    run_audit()