"""
Style memory: a wardrobe that survives between runs.

The wardrobe is saved as JSON next to the project. It is only read when a run
is given an empty wardrobe, and only written when run_agent is called with
remember_item=True.
"""
import json

import config

PATH = config.ROOT / "saved_wardrobe.json"


def load_wardrobe() -> dict:
    """Return the saved wardrobe, or {'items': []} if there is none."""
    try:
        data = json.loads(PATH.read_text(encoding="utf-8"))
        items = data.get("items")
        return {"items": items if isinstance(items, list) else []}
    except (OSError, ValueError, AttributeError):
        return {"items": []}


def save_wardrobe(wardrobe: dict) -> None:
    PATH.write_text(
        json.dumps({"items": wardrobe.get("items") or []}, indent=2),
        encoding="utf-8",
    )


def add_item(listing: dict) -> dict:
    """Store a thrifted listing as an owned item and return the new wardrobe."""
    wardrobe = load_wardrobe()
    name = listing["title"]
    if not any(w.get("name") == name for w in wardrobe["items"]):
        wardrobe["items"].append(
            {
                "name": name,
                "category": listing.get("category"),
                "colors": listing.get("colors") or [],
                "style_tags": listing.get("style_tags") or [],
            }
        )
        save_wardrobe(wardrobe)
    return wardrobe


def clear() -> None:
    """Forget everything (used by the demo so it starts from nothing)."""
    try:
        PATH.unlink()
    except OSError:
        pass