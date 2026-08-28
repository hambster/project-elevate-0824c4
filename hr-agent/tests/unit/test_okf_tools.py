"""Unit tests for OKF retrieval tools and policy search."""
import os
import tempfile
import pytest

from app.tools.okf_tool import list_concepts, read_concept, parse_concept_file
from app.tools.policy_tools import search_hr_policies


@pytest.fixture
def sample_knowledge_dir():
    """Create a temporary directory with mock OKF markdown files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        category_dir = os.path.join(tmpdir, "01-leave")
        os.makedirs(category_dir, exist_ok=True)
        
        # Concept file with valid frontmatter
        concept1 = os.path.join(category_dir, "1.1-sick-leave.md")
        with open(concept1, "w", encoding="utf-8") as f:
            f.write(
                "---\n"
                "type: HR Policy\n"
                "title: \"Sick Leave Policy\"\n"
                "description: \"Provides 14 days of paid outpatient sick leave.\"\n"
                "source: \"Handbook Section 1.1\"\n"
                "---\n\n"
                "# Sick Leave\n\n"
                "Employees receive up to 14 days of paid outpatient sick leave."
            )
            
        # Reserved file that should be ignored in listing
        index_file = os.path.join(tmpdir, "index.md")
        with open(index_file, "w", encoding="utf-8") as f:
            f.write("# Index\nTable of contents")

        yield tmpdir


def test_parse_concept_file(sample_knowledge_dir):
    file_path = os.path.join(sample_knowledge_dir, "01-leave", "1.1-sick-leave.md")
    fm, body = parse_concept_file(file_path)
    assert fm.get("title") == "Sick Leave Policy"
    assert fm.get("source") == "Handbook Section 1.1"
    assert "14 days of paid outpatient sick leave" in body


def test_list_concepts(sample_knowledge_dir):
    result = list_concepts(knowledge_dir=sample_knowledge_dir)
    assert "concepts" in result
    concepts = result["concepts"]
    assert len(concepts) == 1
    assert concepts[0]["id"] == "01-leave/1.1-sick-leave"
    assert concepts[0]["title"] == "Sick Leave Policy"
    assert "14 days" in concepts[0]["description"]


def test_read_concept_success(sample_knowledge_dir):
    # Test reading with full relative id
    res = read_concept("01-leave/1.1-sick-leave", knowledge_dir=sample_knowledge_dir)
    assert res["title"] == "Sick Leave Policy"
    assert res["resource"] == "Handbook Section 1.1"
    assert "14 days of paid outpatient sick leave" in res["content"]

    # Test reading with filename only (fuzzy resolution)
    res_short = read_concept("1.1-sick-leave", knowledge_dir=sample_knowledge_dir)
    assert res_short["title"] == "Sick Leave Policy"


def test_read_concept_not_found(sample_knowledge_dir):
    res = read_concept("non-existent-concept", knowledge_dir=sample_knowledge_dir)
    assert "not found" in res["content"].lower()
    assert res["resource"] is None


def test_read_concept_path_traversal_blocked(sample_knowledge_dir):
    res = read_concept("../../etc/passwd", knowledge_dir=sample_knowledge_dir)
    assert "traversal is not allowed" in res["content"].lower()
    assert res["resource"] is None


def test_search_hr_policies(sample_knowledge_dir):
    # Match query
    match = search_hr_policies("sick leave", knowledge_dir=sample_knowledge_dir)
    assert match["matched"] is True
    assert match["title"] == "Sick Leave Policy"
    assert "Handbook Section 1.1" in match["sources"]

    # Out of scope / ungrounded query
    no_match = search_hr_policies("space travel subsidy", knowledge_dir=sample_knowledge_dir)
    assert no_match["matched"] is False
    assert "could not find an answer" in no_match["message"]


def test_live_okf_corpus_loaded():
    """Verify that the real knowledge directory is discovered and readable."""
    result = list_concepts()
    assert len(result["concepts"]) > 10
    
    # Check outpatient sick leave exists
    sick_concept = read_concept("1.1-outpatient-sick-time-hospitalization-leave-singapore")
    assert "outpatient sick leave" in sick_concept["content"].lower()
    assert sick_concept["resource"] is not None
