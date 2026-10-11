from mcp.server.fastmcp import FastMCP

from tools import search_listings as _search_listings_impl

mcp = FastMCP("fitfindr", log_level="WARNING")


@mcp.tool()
def search_listings(
    description: str,
    size: str | None = None,
    max_price: float | None = None,
) -> list[dict]:
    """
    Searches a fixed catalog of 40 second-hand clothing listings and returns the matches.

    Args:
        description: Required. Free-text keywords (e.g. "vintage graphic tee"). Matched against
            each listing's title, description and style tags; a listing must share at least
            one keyword to be returned. Common filler words (a, an, and, the, for, with,
            under, over, in, of) are ignored.
        size: Optional string (e.g. "M"). Matched as a whole size token, so "M" matches "M",
            "S/M" and "M/L" but not "XL". Listings sized "One Size" match any request.
            Omit or pass null to skip size filtering.
        max_price: Optional number, in US dollars, inclusive (e.g. 30 returns listings priced
            $30 or less). Omit or pass null for no price ceiling.

    Returns:
        A list of at most 10 listing objects, ordered by number of matching keywords (most
        first). Ties keep the catalog's original order. Each has: id, title, description,
        category, style_tags, size, condition, price, colors, brand (often null), platform.

        Returns an empty list when nothing matches. It never returns null and never raises;
        an empty list is the normal way this tool says "no results".
    """
    return _search_listings_impl(description, size, max_price)


if __name__ == "__main__":
    mcp.run()