"""Paper analysis tools."""

import requests
from bs4 import BeautifulSoup


def extract_text_from_pdf(url: str) -> str | None:
    """Extract text content from a PDF URL."""
    try:
        # This is a simplified implementation
        # In production, you'd use PyPDF2, pdfplumber, or similar
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            # For now, return a placeholder
            # Real implementation would parse PDF
            return f"PDF content from {url} (extraction not implemented)"
        return None
    except (OSError, ValueError) as e:
        print(f"PDF extraction failed: {e}")
        return None


def extract_text_from_web(url: str) -> str | None:
    """Extract text content from a web page."""
    try:
        response = requests.get(
            url, timeout=10, headers={"User-Agent": "Mozilla/5.0 (compatible; ResearchAgent/1.0)"}
        )

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")

            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.extract()

            # Get text
            text = soup.get_text()

            # Clean up whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = " ".join(chunk for chunk in chunks if chunk)

            return text[:5000]  # Limit text length
        return None
    except (requests.RequestException, ValueError) as e:
        print(f"Web text extraction failed: {e}")
        return None


def analyze_paper_content(paper: dict) -> dict:
    """Analyze the content of a research paper."""
    content = None

    # Try to extract content
    if paper.get("url", "").endswith(".pdf"):
        content = extract_text_from_pdf(paper["url"])
    elif paper.get("url"):
        content = extract_text_from_web(paper["url"])

    if not content and paper.get("abstract"):
        content = paper["abstract"]

    if not content:
        return {
            "summary": "Content extraction failed",
            "key_findings": [],
            "methodology": "Unknown",
            "limitations": ["Content not accessible"],
        }

    # Simple analysis (in production, use LLM or NLP tools)
    analysis = {
        "summary": content[:500] + "..." if len(content) > 500 else content,
        "key_findings": extract_key_findings(content),
        "methodology": extract_methodology(content),
        "limitations": extract_limitations(content),
    }

    return analysis


def extract_key_findings(text: str) -> list[str]:
    """Extract key findings from text (simplified)."""
    # Look for common patterns
    indicators = ["found that", "results show", "concluded that", "demonstrated that"]
    findings = []

    sentences = text.split(".")
    for sentence in sentences:
        sentence = sentence.strip().lower()
        if any(indicator in sentence for indicator in indicators):
            findings.append(sentence.capitalize())

    return findings[:5]  # Limit to 5 findings


def extract_methodology(text: str) -> str:
    """Extract methodology information (simplified)."""
    text_lower = text.lower()

    if "experiment" in text_lower:
        return "Experimental study"
    elif "survey" in text_lower:
        return "Survey-based research"
    elif "case study" in text_lower:
        return "Case study"
    elif "literature review" in text_lower:
        return "Literature review"
    elif "statistical analysis" in text_lower:
        return "Statistical analysis"
    else:
        return "Mixed methods"


def extract_limitations(text: str) -> list[str]:
    """Extract limitations from text (simplified)."""
    limitations = []
    text_lower = text.lower()

    if "however" in text_lower or "but" in text_lower:
        limitations.append("Some conflicting evidence found")

    if "small sample" in text_lower:
        limitations.append("Limited sample size")

    if "future research" in text_lower:
        limitations.append("Suggests need for further research")

    return limitations if limitations else ["Not explicitly stated"]


def calculate_paper_metrics(paper: dict) -> dict:
    """Calculate various metrics for a paper."""
    return {
        "title_length": len(paper.get("title", "")),
        "abstract_length": len(paper.get("abstract", "")),
        "author_count": len(paper.get("authors", [])),
        "has_url": bool(paper.get("url")),
        "has_year": bool(paper.get("year")),
        "estimated_citations": paper.get("citations", 0),
    }
