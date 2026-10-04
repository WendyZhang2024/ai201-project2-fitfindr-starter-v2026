"""
The three FitFindr tools.

Each one is a standalone function you can call and test on its own, before any
of them are wired into the loop. Build and test them one at a time — three
untested tools joined by a loop is one problem that looks like six, because you
can't tell which layer is lying to you.

    search_listings(description, size, max_price)  → list[dict]
    suggest_outfit(new_item, wardrobe)             → str
    create_fit_card(outfit, new_item)              → str

All three are stubs right now. They run and they do nothing — that's the
starting position and it's deliberate.

⚠️ Before you write any of them, fill in the **Tool Inventory** section of your
README (Milestone 2). Four lines per tool: what it does, each input with its
type, exactly what it returns, and what it returns when it has nothing to give.
That last line is what your loop branches on. "Returns a list" earns nothing —
the description has to say what is *in* the list.
"""
import re

import config  # noqa: F401 — you'll use this in search_listings
from generate import generate
from utils.data_loader import load_listings


# ── Tool 1: search_listings ───────────────────────────────────────────────────
_STOPWORDS = {
    "a", "an", "and", "the", "for", "with", "under", "over", "in", "of"
}

def _keywords(text: str) -> set[str]:
    """Lowercase words worth matching on, stopwords removed."""
    words = re.findall(r"[a-z0-9']+", (text or "").lower())
    return {w for w in words if w not in _STOPWORDS and len(w) > 1}

def _size_tokens(size: str) -> set[str]:
    cleaned = re.sub(r"\([^)]*\)", " ", size or "") # drop parentheticals
    parts = [p.strip().upper() for p in cleaned.split("/")]
    return {p for p in parts if p}

def _size_matches(wanted: str, listing_size: str) -> bool:
    if not wanted:
        return True
    listing_tokens = _size_tokens(listing_size)
    if any(token.startswith("ONE SIZE") for token in listing_tokens):
        return True
    return bool(_size_tokens(wanted) & listing_tokens)

def search_listings(
    description: str,
    size: str | None = None,
    max_price: float | None = None,
) -> list[dict]:
    """
    Search the listings data for items matching a description, and optionally a
    size and a price ceiling.

    This is the tool that doesn't call the model, which makes it the easiest one
    to test and the one to move onto MCP in unit 4.

    Args:
        description: keywords describing what the user wants
                     (e.g. "vintage graphic tee").
        size:        a size string to filter by, or None to skip size filtering.
                     Match case-insensitively — "M" should match "S/M".

                     ⚠️ Read the sizes in the data before you reach for a plain
                     substring test. `"s" in "us 9"` is True, and so is
                     `"l" in "xl"`. A filter that returns shoes when someone
                     asked for a small top reads like a broken search, and it
                     will quietly cost you in unit 4 when you test criterion 1.
                     What counts as a size match is part of your spec — decide
                     it and write it into your Tool Inventory.
        max_price:   maximum price, inclusive, or None to skip price filtering.

    Returns:
        A list of matching listing dicts, best match first.
        **Returns an empty list when nothing matches — an empty list, not None,
        and not an exception.** Your loop branches on this.

    Each listing dict has these fields:
        id, title, description, category, style_tags (list), size,
        condition, price (float), colors (list), brand (str or None), platform

    Note that `brand` is None for most listings. That is deliberate and
    realistic — thrift listings often have no brand. If something you write
    assumes a brand is always there, you will find out in unit 4.

    TODO:
        1. Load every listing with load_listings().
        2. Filter by max_price and by size, when each is provided.
        3. Score what's left by keyword overlap with `description`.
        4. Drop anything scoring zero.
        5. Sort by score, highest first, and return the listing dicts —
           at most config.SEARCH_RESULT_LIMIT of them.

    Test it from a terminal before you move on:
        python -c "from tools import search_listings; print(search_listings('graphic tee', max_price=30))"
    """
    # TODO: replace this with your implementation
    listings = load_listings()
    results = []

    for item in listings:
        if max_price is not None and item['price'] > max_price:
            continue
        if size is not None and not _size_matches(size, item['size']):
            continue
        results.append(item)
        
    desc_keywords = _keywords(description)
    scored_results = []

    for item in results:
        item_text = f"{item['title']} {item['description']} {' '.join(item['style_tags'])}"
        item_keywords = _keywords(item_text)
        overlap = len(desc_keywords.intersection(item_keywords))
        if overlap > 0:
            scored_results.append((overlap, item))
            
    scored_results.sort(key=lambda x: x[0], reverse=True)
    final_results = [item for score, item in scored_results]

    return final_results[:config.SEARCH_RESULT_LIMIT]


# ── Tool 2: suggest_outfit ────────────────────────────────────────────────────

def suggest_outfit(new_item: dict, wardrobe: dict) -> str:
    """
    Given a thrifted item and the user's wardrobe, suggest one or two outfits.

    This one calls the model, through `generate()`. You don't need to think
    about rate limits — the adapter handles pacing for you.

    Args:
        new_item: a listing dict — the item the user is considering.
        wardrobe: a wardrobe dict with an 'items' key holding a list of items.
                  **It may be empty.** Handle that.

    Returns:
        A non-empty string with outfit suggestions.
        With an empty wardrobe, return general styling advice rather than
        raising or returning "". Unit 4 has you trigger the empty wardrobe on
        purpose, so decide now what it should do.

    TODO:
        1. Check whether wardrobe['items'] is empty.
        2. If it is, ask the model for general styling ideas for this item.
        3. If it isn't, format the wardrobe items into the prompt and ask for
           specific combinations naming pieces the user already owns.
        4. Return the model's response.

    Test it from a terminal before you move on:
        python -c "from tools import suggest_outfit; from utils.data_loader import get_example_wardrobe, load_listings; print(suggest_outfit(load_listings()[0], get_example_wardrobe()))"
    """
    # TODO: replace this with your implementation
    if not wardrobe or not wardrobe.get('items'):
        prompt = f"The user is considering buying this secondhand item: {new_item['title']} (Price: ${new_item['price']}). The user currently has no other clothes. Please provide general styling advice, such as what types of pants or shoes to pair with it."
    else:
        items_str = "\n".join([f"- {w['name']} ({', '.join(w['colors'])}, {', '.join(w['style_tags'])})" for w in wardrobe['items']])
        prompt = f"The user is considering buying this secondhand item: {new_item['title']} (Price: ${new_item['price']}, Platform: {new_item['platform']}).\n\nThe user's current wardrobe includes:\n{items_str}\n\nPlease provide 1-2 specific outfit suggestions combining the new item with the specific pieces the user already owns."
    
    return generate(prompt)


# ── Tool 3: create_fit_card ───────────────────────────────────────────────────

def create_fit_card(outfit: str, new_item: dict) -> str:
    """
    Write a short caption someone would actually post about the find.

    This calls the model too.

    Args:
        outfit:   the outfit suggestion string from suggest_outfit().
        new_item: the listing dict for the item.

    Returns:
        A two-to-four sentence caption.
        If `outfit` is empty or whitespace, return a descriptive message rather
        than raising.

    The caption should read like a real post rather than a product description,
    mention the item and its price and platform once each, and be specific about
    the vibe.

    It should also come out **differently for different inputs**. If you run
    this three times on the same item and get three word-for-word identical
    strings, it's one of two things, and both are near the top of `config.py`:

        • CACHE_ENABLED — the adapter handed back an answer it already had
        • TEMPERATURE   — at 0.0 the model gives the same words every time

    TODO:
        1. Guard against an empty or whitespace-only `outfit`.
        2. Build a prompt with the item details and the outfit.
        3. Call generate() and return the response.

    Test it from a terminal before you move on:
        python -c "from tools import create_fit_card; from utils.data_loader import load_listings; print(create_fit_card('jeans and white sneakers', load_listings()[0]))"
    """
    # TODO: replace this with your implementation
    if not outfit or not outfit.strip():
        return "No outfit suggestions available to create a fit card."

    prompt = f"Write a 2-4 sentence social media caption for this secondhand item.\n\nItem details:\n- Title: {new_item['title']}\n- Price: ${new_item['price']}\n- Platform: {new_item['platform']}\n- Tags: {', '.join(new_item['style_tags'])}\n\nOutfit suggestion:\n{outfit}\n\nRequirements: Write it like a real outfit share, and you must mention the price ({new_item['price']}) and platform ({new_item['platform']}) once each."

    return generate(prompt)

# ── Tool 4: compare_prices ── 
 
def compare_prices(item: dict, limit: int = 3) -> list[dict]:
    """
    Find cheaper listings that could stand in for `item`.
 
    A listing counts when it is in the same category, shares at least one
    style tag with `item`, and costs less. Does not call the model.
 
    Args:
        item:  a listing dict (the selected item).
        limit: the most alternatives to return.
 
    Returns:
        A list of listing dicts, cheapest first, at most `limit` long.
        Returns [] when nothing cheaper is similar — an empty list, not None.
    """
    tags = set(item.get("style_tags") or [])
    price = float(item["price"])
 
    matches = []
    for other in load_listings():
        if other["id"] == item["id"]:
            continue
        if other.get("category") != item.get("category"):
            continue
        if float(other["price"]) >= price:
            continue
        if not tags & set(other.get("style_tags") or []):
            continue
        matches.append(other)
 
    matches.sort(key=lambda x: float(x["price"]))
    return matches[:limit]