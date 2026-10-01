import json
from pathlib import Path
from typing import List, Dict, Any
from ..models.schemas import Evidence

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

class InvestigationAgent:
    """Retrieves relevant facts from Knowledge Base, Past Tickets, and System Telemetry."""

    def __init__(self):
        self.kb_articles = self._load_json("kb_articles.json", [])
        self.past_tickets = self._load_json("past_tickets.json", [])
        self.system_status = self._load_json("system_status.json", {}).get("services", [])

    def _load_json(self, filename: str, default: Any) -> Any:
        path = DATA_DIR / filename
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return default

    def run(self, description: str, category: str) -> List[Evidence]:
        query_text = f"{description} {category}".lower()
        evidence_list: List[Evidence] = []
        ev_counter = 1

        # 1. Search Knowledge Base
        for kb in self.kb_articles:
            score = 0
            for tag in kb.get("tags", []):
                if tag in query_text:
                    score += 25
            if kb.get("category", "").lower() in query_text:
                score += 20
            
            if score > 0:
                relevance = min(score + 30, 98)
                evidence_list.append(Evidence(
                    id=f"ev-kb-{ev_counter}",
                    type="knowledge_base",
                    title=f"{kb['id']}: {kb['title']}",
                    content=kb['content'],
                    relevance=relevance,
                    source="Knowledge Base Runbook"
                ))
                ev_counter += 1

        # 2. Check System Status & Telemetry
        for svc in self.system_status:
            svc_name = svc.get("name", "").lower()
            svc_id = svc.get("id", "").lower()
            
            if ("vpn" in query_text and "vpn" in svc_id) or \
               ("proxy" in query_text and "proxy" in svc_id) or \
               ("git" in query_text and "proxy" in svc_id) or \
               ("sso" in query_text and "sso" in svc_id):
                
                status_desc = f"Service: {svc.get('name')}. Status: {svc.get('status')}."
                if "stale_locks_detected" in svc:
                    status_desc += f" Stale session locks detected: {svc['stale_locks_detected']}."
                if "last_crash" in svc:
                    status_desc += f" Last crash diagnostic: {svc['last_crash']}."
                
                evidence_list.append(Evidence(
                    id=f"ev-sys-{ev_counter}",
                    type="system_status",
                    title=f"Telemetry Check: {svc.get('name')}",
                    content=status_desc,
                    relevance=94,
                    source="Infrastructure Telemetry"
                ))
                ev_counter += 1

        # 3. Check Past Tickets
        for t in self.past_tickets:
            match_score = 0
            for tag in t.get("tags", []):
                if tag in query_text:
                    match_score += 30
            if match_score >= 30:
                evidence_list.append(Evidence(
                    id=f"ev-tkt-{ev_counter}",
                    type="ticket",
                    title=f"Historical Ticket: {t['id']} - {t['title']}",
                    content=f"Root cause: {t['root_cause']}. Resolution: {t['resolution_action']}.",
                    relevance=min(match_score + 25, 95),
                    source="Historical ITSM Bank"
                ))
                ev_counter += 1

        # Sort evidence by relevance
        evidence_list.sort(key=lambda x: x.relevance, reverse=True)
        return evidence_list[:4]

investigation_agent = InvestigationAgent()
