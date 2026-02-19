from __future__ import annotations

PAGE_SIZE = 10


def paginate(items: list, page: int = 1) -> dict:
    page = max(1, page)
    total = len(items)
    total_pages = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)
    start = (page - 1) * PAGE_SIZE
    end = start + PAGE_SIZE
    return {
        "items": items[start:end],
        "page": page,
        "total_pages": total_pages,
        "total": total,
    }
