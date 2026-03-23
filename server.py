# /// script
# dependencies = ["mcp[cli]", "arxiv"]
# ///

import arxiv
import json
import sqlite3
from pathlib import Path
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("arxiv-mcp")

DB_PATH = Path(__file__).parent / "reading_list.db"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("""
        CREATE TABLE IF NOT EXISTS papers (
            arxiv_id    TEXT PRIMARY KEY,
            title       TEXT,
            authors     TEXT,
            abstract    TEXT,
            published   TEXT,
            pdf_url     TEXT,
            note        TEXT,
            saved_at    DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    return conn

@mcp.tool()
def search_papers(query: str, max_results: int = 5) -> str:
    """Search arXiv for papers matching a query."""
    client = arxiv.Client()
    search = arxiv.Search(query=query, max_results=max_results)
    results = []
    for paper in client.results(search):
        results.append({
            "id": paper.entry_id.split("/")[-1],
            "title": paper.title,
            "authors": [a.name for a in paper.authors[:3]],
            "abstract": paper.summary[:300] + "...",
            "published": str(paper.published.date()),
            "url": paper.pdf_url,
        })
    return json.dumps(results, indent=2)

@mcp.tool()
def get_paper(arxiv_id: str) -> str:
    """Get full details for a specific paper by its arXiv ID (e.g. '2303.08774')."""
    client = arxiv.Client()
    search = arxiv.Search(id_list=[arxiv_id])
    paper = next(client.results(search))
    return json.dumps({
        "title": paper.title,
        "authors": [a.name for a in paper.authors],
        "abstract": paper.summary,
        "published": str(paper.published.date()),
        "categories": paper.categories,
        "pdf_url": paper.pdf_url,
    }, indent=2)

@mcp.tool()
def find_related(arxiv_id: str) -> str:
    """Find papers related to a given paper by searching its title."""
    client = arxiv.Client()
    paper = next(client.results(arxiv.Search(id_list=[arxiv_id])))
    related = arxiv.Search(query=paper.title, max_results=6)
    results = []
    for r in client.results(related):
        if r.entry_id.split("/")[-1] != arxiv_id:
            results.append({
                "id": r.entry_id.split("/")[-1],
                "title": r.title,
                "published": str(r.published.date()),
            })
    return json.dumps(results[:5], indent=2)

@mcp.tool()
def save_paper(arxiv_id: str) -> str:
    """Save a paper to the local reading list by its arXiv ID."""
    client = arxiv.Client()
    paper = next(client.results(arxiv.Search(id_list=[arxiv_id])))

    with get_db() as conn:
        conn.execute("""
            INSERT OR IGNORE INTO papers (arxiv_id, title, authors, abstract, published, pdf_url)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            arxiv_id,
            paper.title,
            json.dumps([a.name for a in paper.authors]),
            paper.summary,
            str(paper.published.date()),
            paper.pdf_url,
        ))

    return f"Saved '{paper.title}' to reading list."

@mcp.tool()
def list_saved() -> str:
    """List all papers saved to the reading list, including any notes."""
    with get_db() as conn:
        rows = conn.execute("""
            SELECT arxiv_id, title, published, note, saved_at
            FROM papers
            ORDER BY saved_at DESC
        """).fetchall()

    if not rows:
        return "Your reading list is empty."

    return json.dumps([dict(r) for r in rows], indent=2)

@mcp.tool()
def add_note(arxiv_id: str, note: str) -> str:
    """Add or update a personal note on a saved paper."""
    with get_db() as conn:
        updated = conn.execute("""
            UPDATE papers SET note = ? WHERE arxiv_id = ?
        """, (note, arxiv_id)).rowcount

    if updated == 0:
        return f"Paper {arxiv_id} isn't in your reading list yet. Save it first."

    return f"Note updated for {arxiv_id}."

if __name__ == "__main__":
    mcp.run()
