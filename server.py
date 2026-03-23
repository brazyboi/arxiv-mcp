# /// script
# dependencies = ["mcp[cli]", "arxiv"]
# ///

import arxiv
import json
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("arxiv-mcp")

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
    """Get full details for a specific paper by its arXiv ID."""
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

if __name__ == "__main__":
    mcp.run()
