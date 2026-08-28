"""OKF (Open Knowledge Format) retrieval and navigation tools.

These tools allow the agent to navigate the Open Knowledge Format bundle:
first list what concepts exist (list_concepts), then read the relevant concept (read_concept).
"""
import os
import re
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any
import yaml

from app.config import settings

RESERVED_FILES = {"index.md", "log.md", "check_okf.py"}
FRONTMATTER_PATTERN = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)


@dataclass
class ConceptSummary:
    """Summary of a policy concept."""
    id: str
    title: str
    description: str


@dataclass
class ConceptDetail:
    """Detailed content and citation for a policy concept."""
    content: str
    title: str
    resource: Optional[str] = None


def parse_concept_file(file_path: str) -> tuple[Dict[str, Any], str]:
    """Helper to parse a markdown file with YAML frontmatter.
    
    Args:
        file_path: Absolute or relative file path to the markdown file.
        
    Returns:
        Tuple of (frontmatter_dict, markdown_body).
    """
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()
    match = FRONTMATTER_PATTERN.match(text)
    if not match:
        return {}, text
    try:
        data = yaml.safe_load(match.group(1)) or {}
    except yaml.YAMLError:
        data = {}
    body = text[match.end():]
    return data, body


def list_concepts(knowledge_dir: Optional[str] = None) -> Dict[str, List[Dict[str, str]]]:
    """List the policy concepts available in the OKF bundle.
    
    Args:
        knowledge_dir: Optional custom directory to load concepts from. Defaults to configured settings.knowledge_dir.

    Returns:
        {"concepts": [{"id": str, "title": str, "description": str}, ...]}
        where `id` is the concept path without the .md suffix,
        e.g. "01-paid-time-off-leave-operations/1.1-outpatient-sick-time-hospitalization-leave-singapore".
    """
    target_dir = os.path.abspath(knowledge_dir or settings.knowledge_dir)
    if not os.path.exists(target_dir):
        return {"concepts": []}

    concepts: List[ConceptSummary] = []
    for root, _, files in os.walk(target_dir):
        for file in files:
            if not file.endswith(".md") or file in RESERVED_FILES:
                continue
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, target_dir)
            concept_id = rel_path[:-3] if rel_path.endswith(".md") else rel_path
            fm, _ = parse_concept_file(full_path)
            concepts.append(
                ConceptSummary(
                    id=concept_id,
                    title=str(fm.get("title", "")),
                    description=str(fm.get("description", "")),
                )
            )

    concepts.sort(key=lambda x: x.id)
    return {"concepts": [asdict(c) for c in concepts]}


def read_concept(concept_id: str, knowledge_dir: Optional[str] = None) -> Dict[str, Any]:
    """Read an OKF policy concept's content, title, and citation source.

    Args:
        concept_id: The ID of the concept (e.g. "01-paid-time-off-leave-operations/1.1-outpatient-sick-time-hospitalization-leave-singapore" or "1.1-outpatient-sick-time-hospitalization-leave-singapore").
        knowledge_dir: Optional custom directory to read concept from. Defaults to configured settings.knowledge_dir.

    Returns:
        {"content": str, "title": str, "resource": str | None}
        where `content` is the markdown body (after the frontmatter) and
        `resource` is the frontmatter `source` (or `resource`) reference.
    """
    cleaned_id = concept_id.strip()
    if cleaned_id.endswith(".md"):
        cleaned_id = cleaned_id[:-3]

    base_dir = os.path.abspath(knowledge_dir or settings.knowledge_dir)
    target_path = os.path.abspath(os.path.join(base_dir, f"{cleaned_id}.md"))

    # Security: Path traversal protection
    if not target_path.startswith(base_dir + os.sep) and target_path != base_dir:
        return {
            "content": f"Error: Invalid concept_id '{concept_id}'. Path traversal is not allowed.",
            "title": "",
            "resource": None,
        }

    # If direct path not found, search by filename in subdirectories
    if not os.path.isfile(target_path):
        target_name = f"{os.path.basename(cleaned_id)}.md"
        found_path = None
        for root, _, files in os.walk(base_dir):
            if target_name in files:
                found_path = os.path.join(root, target_name)
                break
        if found_path and os.path.isfile(found_path):
            target_path = found_path
        else:
            return {
                "content": f"Error: Concept '{concept_id}' not found.",
                "title": "",
                "resource": None,
            }

    fm, body = parse_concept_file(target_path)
    resource = fm.get("source") or fm.get("resource")
    return {
        "content": body.strip(),
        "title": fm.get("title", ""),
        "resource": resource,
    }
