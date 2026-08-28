"""Mock Policy RAG subagent tool with layout-aware chunking and clickable citations."""
import re
from typing import Dict, Any, Optional

POLICY_CORPUS = {
    "bereavement": {
        "policy_id": "POL-BEREAVEMENT-001",
        "title": "Bereavement Leave Policy",
        "section": "Section 4.2",
        "url": "https://policies.example.com/bereavement",
        "keywords": ["bereavement", "funeral", "death in family", "loss of family"],
        "content": (
            "Under the company's Bereavement Leave Policy (POL-BEREAVEMENT-001, Section 4.2), "
            "employees are entitled to up to 5 consecutive paid working days of bereavement leave "
            "for an immediate family member (spouse, child, parent, sibling). "
            "Up to 3 paid working days are provided for extended family members."
        ),
    },
    "expense_headphones": {
        "policy_id": "POL-EXPENSE-005",
        "title": "Employee Expense & Equipment Policy",
        "section": "Section 6.3",
        "url": "https://policies.example.com/expenses",
        "keywords": ["noise-canceling headphones", "headphones", "audio equipment", "expense headphones"],
        "content": (
            "Under the Employee Expense Policy (POL-EXPENSE-005, Section 6.3), employees are allowed "
            "to expense noise-canceling headphones up to a maximum reimbursable limit of US$150 once "
            "every two years, subject to written manager pre-approval in the expense portal."
        ),
    },
    "remote_work": {
        "policy_id": "POL-REMOTE-002",
        "title": "Remote Work & Home Office Policy",
        "section": "Section 3.1",
        "url": "https://policies.example.com/remote-work",
        "keywords": ["remote work", "home office", "monitor", "ergonomic chair", "equipment procurement"],
        "content": (
            "Under the Remote Work Policy (POL-REMOTE-002, Section 3.1), employees with verified "
            "APPROVED_REMOTE status are eligible for standard home office equipment, including one "
            "27-inch external monitor and ergonomic accessories procured through IT."
        ),
    },
    "medical_leave": {
        "policy_id": "POL-MEDICAL-003",
        "title": "Short-Term Medical Leave Policy",
        "section": "Section 5.0",
        "url": "https://policies.example.com/medical-leave",
        "keywords": ["medical leave", "short-term medical", "leave of absence", "sick leave process"],
        "content": (
            "Under the Short-Term Medical Leave Policy (POL-MEDICAL-003, Section 5.0), employees "
            "taking medical leave must submit a Medical/Sick leave request in WorkWeek and open a "
            "confidential HRSD support case in ServiceImmediately for email routing and confidential medical certificate filing."
        ),
    },
    "relocation": {
        "policy_id": "POL-RELOCATION-004",
        "title": "Global Relocation & Office Transfer Policy",
        "section": "Section 2.4",
        "url": "https://policies.example.com/relocation",
        "keywords": ["relocation", "transfer", "london office", "relocation allowance", "moving allowance"],
        "content": (
            "Under the Global Relocation Policy (POL-RELOCATION-004, Section 2.4), international office "
            "transfers (such as transferring to the London office) are eligible for a $5,000 relocation "
            "allowance. The process requires updating home/work location in WorkWeek and requesting building "
            "access through Facilities in ServiceImmediately."
        ),
    },
}


def search_hr_policies(query: str) -> Dict[str, Any]:
    """Search authoritative corporate HR policy documents (PDF/Markdown corpus).
    
    Use this tool to find information regarding company policies (e.g. Bereavement leave,
    Expense guidelines, Remote work equipment, Medical leave, and Relocation).
    
    Args:
        query: Specific search terms or question about HR policy.
        
    Returns:
        Structured policy matching result with authoritative citations or refusal notice.
    """
    query_lower = query.lower()

    # Check for known policy topics
    for key, item in POLICY_CORPUS.items():
        if any(kw in query_lower for kw in item["keywords"]):
            citation_md = f"[{item['policy_id']} {item['section']}]({item['url']})"
            return {
                "matched": True,
                "policy_id": item["policy_id"],
                "title": item["title"],
                "section": item["section"],
                "content": item["content"],
                "citation": citation_md,
                "sources": f"Sources: {citation_md}",
            }

    # Policy not found or out of scope
    return {
        "matched": False,
        "message": "I could not find an answer to this in our approved HR policy documents. Please contact the HR Direct support desk for further assistance.",
    }
