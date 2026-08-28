"""Authoritative HR Policy Tools and OKF integration."""
import os
import re
from typing import Dict, Any, Optional

from app.config import settings
from app.tools.okf_tool import list_concepts, read_concept, parse_concept_file


def search_hr_policies(query: str, knowledge_dir: Optional[str] = None) -> Dict[str, Any]:
    """Search authoritative corporate HR policy documents in the OKF bundle.
    
    Use this tool to find information regarding company policies (e.g. Bereavement leave,
    Expense guidelines, Remote work equipment, Medical leave, Relocation, Conduct, etc.).
    
    Args:
        query: Specific search terms or question about HR policy.
        knowledge_dir: Optional path to the knowledge base.
        
    Returns:
        Structured policy matching result with authoritative citations or refusal notice.
    """
    query_lower = query.lower().strip()
    words = [w for w in re.split(r"\W+", query_lower) if len(w) > 2]
    if not words:
        words = [query_lower]

    target_dir = os.path.abspath(knowledge_dir or settings.knowledge_dir)
    if not os.path.exists(target_dir):
        return {
            "matched": False,
            "message": "I could not find an answer to this in our approved HR policy documents. Please contact the HR Direct support desk for further assistance.",
        }

    best_match = None
    best_score = 0

    # Search through markdown files in knowledge directory
    for root, _, files in os.walk(target_dir):
        for file in files:
            if not file.endswith(".md") or file in {"index.md", "log.md", "check_okf.py"}:
                continue
            full_path = os.path.join(root, file)
            fm, body = parse_concept_file(full_path)
            
            title = str(fm.get("title", "")).lower()
            desc = str(fm.get("description", "")).lower()
            body_lower = body.lower()
            
            score = 0
            for w in words:
                if w in title:
                    score += 5
                if w in desc:
                    score += 3
                if w in body_lower:
                    score += 1
            
            if score > best_score and score >= 2:
                best_score = score
                resource = fm.get("source") or fm.get("resource") or fm.get("title")
                best_match = {
                    "matched": True,
                    "title": fm.get("title", file[:-3]),
                    "description": fm.get("description", ""),
                    "content": body.strip(),
                    "source": resource,
                    "citation": f"[{resource}]({fm.get('url', 'https://policies.example.com')})" if resource else None,
                    "sources": f"Sources: {resource}" if resource else "Sources: Company HR Policy Handbook",
                }

    if best_match:
        return best_match

    return {
        "matched": False,
        "message": "I could not find an answer to this in our approved HR policy documents. Please contact the HR Direct support desk for further assistance.",
    }
