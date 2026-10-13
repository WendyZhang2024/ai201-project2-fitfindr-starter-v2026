# FitFindr

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first** — setup, every
> command, and what to do when something breaks.
>
> Once `python test.py` passes:
>
> ```bash
> python app.py listings --full -n 6      # read the data (Milestone 1)
> python app.py fields                    # what you can filter on
> python app.py ask 'vintage graphic tee under $30'
> ```
>
> All three tools are stubs, so that last command will do nothing useful yet.
> That's the starting position.
>
> **The rest of this file is your submission.** Fill it in as you go.

---



<!-- ═══════════════════════ UNIT 3 — THE BUILD ═══════════════════════ -->

## What This Does

FitFindr helps users find secondhand clothes and build outfits. You give it a natural language query. It searches the listings, picks one, combines it with your wardrobe to suggest a full outfit, and writes a fit card you could post. If nothing matches, it stops cleanly and reports that.


---

## Tool Inventory


### `search_listings`

- **What it does:** Filters the listings data by text keywords, size, and a maximum price.
- **Inputs:** `description` (str), `size` (str or None), `max_price` (float or None)
- **Returns:** A list of matching listing dicts, best match first, capped at config.SEARCH_RESULT_LIMIT. Each dict contains id, title, description, category, style_tags, size, condition, price, colors, brand, platform.
- **When it has nothing:**  Returns an empty list `[]`. Never None, never an exception.

### `suggest_outfit`

- **What it does:** Generates one or two outfit suggestions combining the new item with the user's wardrobe.
- **Inputs:** `new_item` (dict), `wardrobe` (dict, with an 'items' key that may be empty)
- **Returns:** A non-empty string (`str`) with outfit suggestions.
- **When it has nothing:** (Empty wardrobe) Returns general styling advice string, never raises an exception.

### `create_fit_card`

- **What it does:** Creates a short social-media caption for the thrifted item.
- **Inputs:** `outfit` (str), `new_item` (dict)
- **Returns:** A two-to-four sentence caption string (`str`).
- **When it has nothing:** (Empty `outfit` input) Returns a descriptive message string, never raises an exception.

---

## Planning Loop


**Branch rule:** If `search_listings` returns an empty list, put a message in the session and stop. Otherwise, take the first result and go to `suggest_outfit`.
 
**Where it lives:** `agent.py::run_agent`

**How the query is parsed:** Regex (`parse_query` in `agent.py`). A price pattern pulls out `max_price` (e.g. "under $30"), a size pattern pulls out `size` (e.g. "size M", "size XXS"), and whatever text is left becomes `description`. It does not call the model, so it costs nothing and gives the same result every time for the same query. The trade-off is that phrasing the patterns have not seen is missed: "nothing over thirty dollars" parses to no price, and the run silently ignores the ceiling.

**What moves through the session:** `query` → `parsed` (description, size, max_price) → `search_results` → `selected_item` (the first result) → `outfit_suggestion` → `fit_card`. Each tool's result is stored in the session and read back out for the next call. If the search is empty, `error` is set to a message naming what the user could change, and `suggest_outfit` and `create_fit_card` are never called, so `fit_card` stays `None`.

---

## Sample Run


**One full query**

```
$ python app.py ask 'vintage graphic tee under $30'

[1] parse_query
      in:  vintage graphic tee under $30
      out: dict with keys: description, size, max_price
[2] search_listings (via MCP)
      in:  dict with keys: description, size, max_price
      out: 10 items: Y2K Baby Tee — Butterfly Print, Graphic Tee — 2003 Tour Bootleg Style, Vintage Band Tee — Faded Grey … +7 more
      →    10 match(es)
[3] select_item
      out: Y2K Baby Tee — Butterfly Print ($18.0, depop)
[4] suggest_outfit
      in:  Y2K Baby Tee — Butterfly Print ($18.0, depop)
      out: Here are two outfit suggestions combining the Y2K butterfly baby tee with pieces already in your wardrobe, pla…
      →    10 wardrobe item(s)
[5] create_fit_card
      in:  Y2K Baby Tee — Butterfly Print ($18.0, depop)
      out: Obsessed with this Y2K butterfly baby tee, which is officially live on my depop for just $18.0! I love styling…

  Found:    Y2K Baby Tee — Butterfly Print — $18.0 on depop

  Outfit:   Here are two outfit suggestions combining the Y2K butterfly baby tee with pieces already in your wardrobe, playing into that early 2000s aesthetic:

### 1. The Casual Y2K Streetwear Look
* **Bottoms:** Baggy straight-leg jeans (dark wash)
* **Shoes:** Chunky white sneakers
* **Accessories/Layering:** Black crossbody bag + Vintage black denim jacket (worn off the shoulders or unbuttoned)
* **Why it works:** The tight silhouette of the baby tee balances the volume of the baggy dark-wash jeans, which is a signature proportion for Y2K style. Throwing on the black denim jacket and chunky sneakers keeps the look grounded in streetwear.

### 2. The Casual Contrast Look
* **Bottoms:** Wide-leg khaki trousers
* **Shoes:** Chunky white sneakers
* **Accessories/Layering:** Brown leather belt + Black crossbody bag
* **Why it works:** Pairing the ultra-feminine, fitted butterfly tee with structured, earthy wide-leg trousers creates a cool high-low contrast. Accessorizing with the brown belt ties in the earth tones of the khakis while adding a retro touch.

  Fit card: Obsessed with this Y2K butterfly baby tee, which is officially live on my depop for just $18.0! I love styling it with baggy dark-wash denim and chunky sneakers for an effortless street look, or dressing it down with wide-leg khakis for the ultimate 2000s contrast. Grab it before it’s gone! 🦋✨

2 model calls this session, 578 prompt + 326 output tokens

```

**The three tools, tested one at a time**

```
$ python -c "from tools import search_listings; print(search_listings('graphic tee', max_price=30))"

[{'id': 'lst_002', 'title': 'Y2K Baby Tee — Butterfly Print', 'description': 'Super cute early 2000s baby tee with butterfly graphic. Fitted crop length. Tag says medium but fits like a small.', 'category': 'tops', 'style_tags': ['y2k', 'vintage', 'graphic tee', 'cottagecore'], 'size': 'S/M', 'condition': 'excellent', 'price': 18.0, 'colors': ['white', 'pink', 'purple'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_006', 'title': 'Graphic Tee — 2003 Tour Bootleg Style', 'description': 'Vintage-style bootleg tee with faded graphic. Slightly boxy fit. 100% cotton, soft and worn-in.', 'category': 'tops', 'style_tags': ['graphic tee', 'vintage', 'grunge', 'streetwear', 'band tee'], 'size': 'L', 'condition': 'good', 'price': 24.0, 'colors': ['black'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_017', 'title': 'Mesh Long-Sleeve Top — Black', 'description': 'Sheer black mesh long-sleeve. Great for layering under a graphic tee or over a bralette. Stretchy material, fits true to size.', 'category': 'tops', 'style_tags': ['y2k', 'grunge', 'goth', 'layering'], 'size': 'S/M', 'condition': 'excellent', 'price': 15.0, 'colors': ['black'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_033', 'title': 'Vintage Band Tee — Faded Grey', 'description': 'Faded grey band-style tee with distressed graphic. Crew neck. Fits boxy. Well-loved but no holes or major damage.', 'category': 'tops', 'style_tags': ['vintage', 'grunge', 'band tee', 'graphic tee', 'streetwear'], 'size': 'L', 'condition': 'fair', 'price': 19.0, 'colors': ['grey', 'charcoal'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_011', 'title': 'Low-Rise Cargo Pants — Khaki', 'description': 'Y2K era low-rise cargo pants. Lots of pockets. Khaki color, slightly distressed at the hems. Great for layering with a long tee.', 'category': 'bottoms', 'style_tags': ['y2k', 'cargo', '2000s', 'streetwear'], 'size': 'W29', 'condition': 'fair', 'price': 27.0, 'colors': ['khaki', 'tan'], 'brand': None, 'platform': 'poshmark'}, {'id': 'lst_015', 'title': 'Vintage Graphic Hoodie — Faded Black', 'description': 'Faded black pullover hoodie with barely-visible vintage graphic on the chest. Cozy interior. Some pilling but adds to the worn-in look.', 'category': 'tops', 'style_tags': ['vintage', 'grunge', 'graphic', 'streetwear'], 'size': 'L', 'condition': 'fair', 'price': 26.0, 'colors': ['black', 'charcoal'], 'brand': None, 'platform': 'depop'}]
```

```
$ python -c "from tools import suggest_outfit; from utils.data_loader import get_example_wardrobe, load_listings; print(suggest_outfit(load_listings()[0], get_example_wardrobe()))"

Here are two specific outfit suggestions that incorporate the vintage Levi’s 501s into your existing wardrobe, playing on their classic medium wash and straight-leg silhouette:

### 1. Off-Duty Minimal (Casual & Everyday)
* **Top:** White ribbed tank top
* **Outerwear:** Oversized grey crewneck sweatshirt (worn draped over the shoulders or layered on top)
* **Shoes:** Chunky white sneakers
* **Accessories:** Black crossbody bag + brown leather belt
* **Why it works:** Vintage Levi's 501s and a white tank top are a timeless, effortless combination. Tucking the tank into the medium-wash jeans and accenting with the brown leather belt adds a touch of classic polish, while the oversized grey crewneck and chunky white sneakers lean into a comfortable, streetwear-leaning everyday look.

### 2. Vintage Edge (Chunky & Textured)
* **Top:** Black cropped zip hoodie
* **Outerwear:** Vintage black denim jacket
* **Shoes:** Black combat boots
* **Accessories:** Brown leather belt + black crossbody bag
* **Why it works:** Pairing the medium-wash 501s with heavy black elements creates a great high-contrast, grungy aesthetic. The cropped zip hoodie balances the relaxed, straight-leg fit of the vintage jeans, and layering the black denim jacket on top adds depth and texture. Grounding the outfit with black combat boots and the brown leather belt ties the vintage-meets-streetwear vibe together seamlessly.
```

```
$ python -c "from tools import create_fit_card; from utils.data_loader import load_listings; print(create_fit_card('jeans and white sneakers', load_listings()[0]))"

Nothing beats the timeless fit of these vintage Levi's 501s—just pair them with your favorite crisp white sneakers for that effortlessly cool everyday look. Snag this medium wash staple for just $38.0 live on my depop shop right now! 👖✨ #vintage #classic #denim #streetwear
```

---

## How I Used AI

**Moment 1**

- *What I asked for:* I asked Claude to attack my `criteria.md` acceptance criteria and find logic flaws.
- *What came back:* It pointed out that my state criterion's reasoning was wrong: I blamed network hiccups, but `selected_item` is an in-memory Python assignment, and network problems only affect the model calls. It also said my own reasoning for criterion 2 (a deterministic branch must be 5/5) contradicted a 4/5 target here.
- *What I changed:* I raised the state criterion to 5 of 5 and rewrote the reasoning around deterministic variable assignment instead of network instability.

**Moment 2**

- *What I asked for:* I asked Claude to review my `tools.py` and find bugs.
- *What came back:* It found a missing `import re`, and that `.upper` in `_size_tokens` was missing its parentheses, so every search with a size filter would return `[]`.
- *What I changed:* I added `import re` and changed it to `.upper()`. I then ran the three terminal tests, and the size filter returned the right items (`size='M'` gave only the `S/M` listings).

**Moment 3**

- *What I asked for:* I wrote the `search_listings` description in `mcp_server.py` myself, then asked Claude to read it against `tools.py` and tell me whether it described what the code really does. (I used DeepSeek only to translate the milestone instructions into plain English.)
- *What came back:* Claude found two lines in my description that were wrong. I had written that matching covers category, brand and colors, but `tools.py` only matches title, description and style tags. I had also written "cheaper first among equal matches", but the code sorts by keyword overlap only and leaves ties in file order. It also pointed out that the result is capped at `config.SEARCH_RESULT_LIMIT`, which I had not mentioned.
- *What I changed:* I corrected the docstring in `mcp_server.py` and added the cap. I also removed a silent fallback to the direct call in `agent.py`, so a broken MCP connection shows up as an error instead of being hidden.

**Moment 4**

- *What I asked for:* I asked Claude to check my first run-log table and verdicts against `criteria.md` and the results file, and to review the retry code I planned to add.
- *What came back:* My table had only four rows, my "empty wardrobe" row was really criterion 5 with the wrong target, and I had marked criterion 3 as MISSED because of a 503, even though `selected_item` was set correctly in all five pairs. Claude also showed that `generate.py` retried only rate limits (429) and raised 503/500 immediately, which was the real cause of the misses. My snippet had two flaws: a second retry loop duplicating the one already in `generate.py`, and `raise e`, which would have crashed the agent because `agent.py` only catches `ModelUnavailable`.
- *What I changed:* I rewrote the table with five rows and the targets from `criteria.md` (criteria 1 and 4 MISSED at 2/5, the rest MET), rewrote the diagnosis around `generate.py`, and extended the existing retry loop to cover 503/500 instead of adding a new one. The after run (`python run_eval.py --label after`) reached 5/5 on all five criteria; 10 of the 15 model tries needed at least one retry.

## Stretch Features

During the build I changed the design of two of the features. The final versions are what is described and demonstrated here (`compare_prices` is unchanged).

### 1. A fourth tool: `compare_prices`
- **Where:** `tools.py::compare_prices(item, limit=3)`, called from `agent.py::run_agent` and stored in `session["alternatives"]`.
- **Returns:** a list of listing dicts in the same category that share at least one style tag with the item and cost less, cheapest first, at most `limit` long. `[]` when nothing cheaper is similar. It does not call the model.
- **What it changed:** after an item is selected, the run now also reports cheaper alternatives.
- **Run where the agent called it** (`python agent.py`):

```
[3] select_item
      out: Y2K Baby Tee — Butterfly Print ($18.0, depop)
[4] compare_prices
      in:  Y2K Baby Tee — Butterfly Print ($18.0, depop)
      out: 3 items: Mesh Long-Sleeve Top — Black, Henley Long Sleeve — Washed Burgundy, Tie-Dye Long Sleeve — Pastel
      →    3 cheaper alternative(s)
```

### 2. A second branch: relax the size
- **Design change:** I first planned a budget fallback, but `search_listings` already filters by `max_price`, so results can never exceed it. I used the size filter instead.
- **Condition:** `search_listings` returns an empty list **and** the query set a size. **Path:** the loop retries once without the size. If that finds listings it continues, with a note in `session["notes"]`. If it is still empty it takes the original stop branch.
- **Where:** `agent.py::run_agent`.
- **What it changed:** a size that rules everything out no longer ends the run. The empty-search stop still happens when relaxing doesn't help (the `designer ballgown size XXS under $5` run).
- **Run where the branch was taken** (`graphic tee size XXS`):

```
[12] search_listings (via MCP)
      out: [] (empty)
      →    0 match(es)
[13] branch
      out: 6 items: Y2K Baby Tee — Butterfly Print, Graphic Tee — 2003 Tour Bootleg Style, Mesh Long-Sleeve Top — Black … +3 more
      →    search empty with size XXS: retried without size, 6 match(es)
[14] select_item
      out: Y2K Baby Tee — Butterfly Print ($18.0, depop)
  note:     Nothing was listed in size XXS, so these results are in other sizes.
```

### 3. Style memory
- **Design change:** instead of saving style tags, the agent saves the wardrobe, so the next outfit can name the actual piece.
- **How:** `run_agent(..., remember_item=True)` saves the selected item to `saved_wardrobe.json` as something the user now owns. A later run given an empty wardrobe uses the saved one instead. Code is in `memory.py` and `agent.py::run_agent`.
- **What it changed:** with an empty wardrobe the outfit used to be generic advice; now it can use pieces from earlier runs. Calling `suggest_outfit` directly is unchanged.
- **Two runs where the second is shaped by the first** (`python memory_demo.py`):

```
=== Run 1: empty wardrobe, and the user keeps the item ===
[5] suggest_outfit
      →    0 wardrobe item(s)
[7] style memory
      →    selected item saved for the next run

=== Run 2: empty wardrobe again, but the memory now has an item ===
[8] style memory
      →    empty wardrobe replaced by 1 saved item(s)
[13] suggest_outfit
      →    1 wardrobe item(s)
  outfit:   Here is a specific outfit combination using your new corduroy wide-legged pants and your Y2K butterfly baby tee: ...
```

<!-- ═══════════════════════ UNIT 4 — THE TEST ═══════════════════════

     Don't fill these in during unit 3.
     ═══════════════════════════════════════════════════════════════════ -->

---

## Run Log — Before

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1. A matching query completes all three tools | 4 of 5 | FAIL | PASS | PASS | FAIL | FAIL | MISSED (2/5) |
| 2. An impossible query stops before the second tool | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 3. State: each run keeps its own selected item | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 4. The fit card keeps the facts and is not a copy | 4 of 5 | FAIL | PASS | PASS | FAIL | FAIL | MISSED (2/5) |
| 5. An empty wardrobe still gets styling advice | 4 of 5 | FAIL | PASS | PASS | PASS | PASS | MET (4/5) |

**Real output from one try:** criterion 1, Try 1 of `results/run_2026-10-14_0122_before.md` (query `vintage graphic tee under $30`). The trace is printed by `trace.step()` calls in `agent.py::run_agent`; the 503 is raised in `generate.py::generate` and caught in `agent.py::run_agent`.

```
[1] parse_query
      in:  vintage graphic tee under $30
      out: {'description': 'vintage graphic tee', 'size': None, 'max_price': 30.0}
[2] search_listings (via MCP)
      in:  {'description': 'vintage graphic tee', 'size': None, 'max_price': 30.0}
      out: 10 items: Y2K Baby Tee — Butterfly Print, Graphic Tee — 2003 Tour Bootleg Style, Vintage Band Tee — Faded Grey … +7 more
      →    10 match(es)
[3] select_item
      out: Y2K Baby Tee — Butterfly Print ($18.0, depop)
[4] compare_prices
      in:  Y2K Baby Tee — Butterfly Print ($18.0, depop)
      out: 3 items: Mesh Long-Sleeve Top — Black, Henley Long Sleeve — Washed Burgundy, Tie-Dye Long Sleeve — Pastel
      →    3 cheaper alternative(s)
[5] suggest_outfit
      in:  Y2K Baby Tee — Butterfly Print ($18.0, depop)
      out: Here are 2 specific outfit suggestions combining the Y2K butterfly baby tee with pieces from your current ward…
      →    10 wardrobe item(s)
[6] model unavailable
      →    stopping, search results kept
```

`session["error"]` for that try:

```
The model couldn't be reached, so the outfit and caption steps didn't run. The search worked — 10 listing(s) were found. The model service may be busy. Wait a minute and run the same query again.
What the service said: Couldn't reach the model: 503 UNAVAILABLE. {'error': {'code': 503, 'message': 'This model is currently experiencing high demand. Spikes in demand are usually temporary. Please try again later.', 'status': 'UNAVAILABLE'}}
```

---

## Verdicts and Diagnoses

| # | Criterion | Target | Verdict | How I decided |
|---|---|---|---|---|
| 1 | A matching query completes all three tools | 4 of 5 | MISSED | Only tries 2 and 3 ended with a fit card (2/5). Tries 1, 4 and 5 stopped at `[6]/[5] model unavailable` with a 503. |
| 2 | An impossible query stops before the second tool | 5 of 5 | MET | All 5 tries ended at `[4] branch` with `selected_item` none and no outfit or fit card. |
| 3 | State: each run keeps its own selected item | 5 of 5 | MET | Pairing try N of `matching query` with try N of `state`: in all 5 pairs `selected_item` was the first search result of its own run (Y2K Baby Tee vs Denim Jacket). This held even in try 2, where the run stopped later on a 503. |
| 4 | The fit card keeps the facts and is not a copy | 4 of 5 | MISSED | Scored on the 5 fit cards of the matching-query scenario. Tries 2 and 3 contain "18.0" and "depop"/"Depop" and differ from each other; tries 1, 4 and 5 produced no fit card (2/5). |
| 5 | An empty wardrobe still gets styling advice | 4 of 5 | MET | `suggest_outfit` returned 3,300+ characters with none of "please add", "no items", "error" in tries 2–5 (4/5). Try 1 failed at `suggest_outfit` with a 503. |

**Diagnoses**

**Criterion 1 (MISSED, 2/5) and Criterion 4 (MISSED, 2/5) are one problem.** Tries 1, 4 and 5 of the matching-query scenario ended on a `503 UNAVAILABLE` from the model service. In tries 1 and 4 `suggest_outfit` had succeeded and the failure was in `create_fit_card` (`[6] model unavailable`, no fit card); in try 5 it was `suggest_outfit` itself. Criterion 4 missed on the same three tries because no fit card existed to score. Where: the model call inside `tools.py::suggest_outfit` / `create_fit_card`, which goes through `generate.py::generate`. Mechanism: `generate()` only retries on rate limiting (429); any other error, including 503 and 500, is raised immediately as `ModelUnavailable` (`generate.py`, the `if not rate_limited: raise ModelUnavailable(...)` branch), and `agent.py::run_agent` catches it and stops. A spike in demand that "usually lasts a few seconds" therefore ends the run on the first attempt. The tools and the loop behaved correctly; the missing retry for transient server errors is the cause. The same thing hit the empty-wardrobe scenario (a 503 in try 1 and a `500 INTERNAL` in try 3).

---

## Loop Trace


**Happy path**

```
[1] parse_query
      in:  vintage graphic tee under $30
      out: {'description': 'vintage graphic tee', 'size': None, 'max_price': 30.0}
[2] search_listings (via MCP)
      in:  {'description': 'vintage graphic tee', 'size': None, 'max_price': 30.0}
      out: 10 items: Y2K Baby Tee — Butterfly Print, Graphic Tee — 2003 Tour Bootleg Style, Vintage Band Tee — Faded Grey … +7 more
      →    10 match(es)
[3] select_item
      out: Y2K Baby Tee — Butterfly Print ($18.0, depop)
[4] compare_prices
      in:  Y2K Baby Tee — Butterfly Print ($18.0, depop)
      out: 3 items: Mesh Long-Sleeve Top — Black, Henley Long Sleeve — Washed Burgundy, Tie-Dye Long Sleeve — Pastel
      →    3 cheaper alternative(s)
[5] suggest_outfit
      in:  Y2K Baby Tee — Butterfly Print ($18.0, depop)
      out: Here are two outfit suggestions combining the Y2K butterfly baby tee with pieces already in your wardrobe, pla…
      →    10 wardrobe item(s)
[6] create_fit_card
      in:  Y2K Baby Tee — Butterfly Print ($18.0, depop)
      out: Channeling major 2000s off-duty energy today by styling this butterfly baby tee with baggy dark wash denim and…
```

(Produced by `python app.py ask 'vintage graphic tee under $30' --trace`; the `trace.step()` calls are in `agent.py::run_agent`.)

**Empty search**

```
[1] parse_query
      in:  designer ballgown size XXS under $5
      out: {'description': 'designer ballgown', 'size': 'XXS', 'max_price': 5.0}
[2] search_listings (via MCP)
      in:  {'description': 'designer ballgown', 'size': 'XXS', 'max_price': 5.0}
      out: [] (empty)
      →    0 match(es)
[3] branch
      in:  {'description': 'designer ballgown', 'size': None, 'max_price': 5.0}
      out: [] (empty)
      →    search empty with size XXS: retried without size, 0 match(es)
[4] branch
      →    search returned []: stopping before suggest_outfit
```

**The three failure modes, triggered one at a time**

1. **Empty search** — `python app.py ask 'designer ballgown size XXS under $5'` (trace above). The loop retried without the size, found nothing, stopped before `suggest_outfit`, and said:

   > Nothing in the listings matched description 'designer ballgown', size XXS, under $5.
   > Things to change: try broader words — 'jacket' finds more than 'cropped corduroy jacket'; drop the size, or try a neighbouring one; raise the price ceiling above $5.

2. **Empty wardrobe** — `python app.py ask 'denim jacket under $50' --empty-wardrobe`. `suggest_outfit` received 0 wardrobe items and returned general styling advice instead of crashing or returning an empty string (it opens "Since this is your very first piece of clothing…"); `create_fit_card` still ran.

3. **Model unavailable** — I changed one character of `GEMINI_API_KEY` in `.env` and ran a query I had not asked before (`python app.py ask 'red wool coat under $60'`). The search and `compare_prices` ran, then the loop stopped at `[5] model unavailable` with no stack trace:

   > The model couldn't be reached, so the outfit and caption steps didn't run. The search worked — 2 listing(s) were found. Check GEMINI_API_KEY in your .env, then run the same query again.
   > What the service said: The model rejected your API key. Check GEMINI_API_KEY in your .env file, or create a fresh key at aistudio.google.com.

   Handling it showed me a flaw: the first version of this message always told the user to check their key. During this unit the model returned a real `503 UNAVAILABLE` (service overloaded) when running `test.py`, and for that the key advice would be wrong. `agent.py` now picks the advice from the cause: a rejected key says to check `.env`; anything else says the service may be busy and to retry in a minute.

**On the MCP move:** I registered `search_listings` as the only tool in `mcp_server.py`. It wraps the existing implementation in `tools.py`, imported under the alias `_search_listings_impl` so the registered function doesn't call itself. In `agent.py`, the direct call `search_listings(description, size, max_price)` was replaced with `mcp_client.call_tool("search_listings", {...})`, inside a small helper `_search()` that both the main search and the size-relaxed retry use. I removed the earlier silent fallback to the direct call, so a broken MCP connection shows up as an error instead of being hidden.

`python mcp_client.py` lists `search_listings` with its description and inputs (`description: string`, `size: string, optional`, `max_price: number, optional`), matching the Tool Inventory. Behaviour did not change after the move: for `vintage graphic tee under $30` the search still returns 10 matches, with the same top three titles and the same selected item (`Y2K Baby Tee — Butterfly Print`) as before. The call changed shape; what it returns did not.

Writing the contract showed me what the tool really does, and two lines I first wrote were wrong. Matching uses only title, description and style tags (not category, brand or colors), and results are ordered by number of matching keywords only, not by price. Matching is also loose: a listing needs just one shared keyword, so `graphic tee` returns `Mesh Long-Sleeve Top — Black` because its description mentions "graphic tee". I corrected the docstring in `mcp_server.py` to say what the code does.


---

## The Improvement

**What I changed:** one change, in `generate.py::generate`. The retry loop used to retry only rate limiting (429); every other error, including `503 UNAVAILABLE` and `500 INTERNAL`, was raised immediately as `ModelUnavailable`. It now also treats those transient server errors (messages containing "503", "unavailable", "500" or "internal") as retryable, with the existing backoff (1, 2, 4, 8, 16 seconds, five attempts). If the retries run out on a transient error it still raises `ModelUnavailable`, so the readable message from Milestone 2 is unchanged. I also replaced a fragile `"rate" in str(error)` check with a `last_was_rate_limited` flag. Nothing else changed: the scenarios, the criteria, `agent.py` and the tools are the same as in the before run.

**Which failure it was meant to fix:** the diagnosis for criteria 1 and 4: the three tries that ended on a `503` at `[5]`/`[6] model unavailable` because `generate()` gave up on the first non-429 error. The same cause also stopped three of five empty-wardrobe tries and one of five state tries in the before run.

### Run Log — After

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1. A matching query completes all three tools | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 2. An impossible query stops before the second tool | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 3. State: each run keeps its own selected item | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 4. The fit card keeps the facts and is not a copy | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 5. An empty wardrobe still gets styling advice | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |

(Produced by `python run_eval.py --label after`, results in `results/run_2026-10-14_0255_after.md`. Criterion 4 is scored on the five fit cards of the matching-query scenario: all five contain "18" and "depop" and no two are identical. Criterion 5: `suggest_outfit` returned 3,100+ characters in every try with none of "please add", "no items", "error".)

**Did it help, and how do I know:** yes. In the before run the model call ended a run early in 7 of the 15 tries that use the model (3 of 5 matching, 3 of 5 empty wardrobe, 1 of 5 state), and criteria 1 and 4 were MISSED at 2/5. In the after run none of the 15 stopped early, and criteria 1 and 4 went to 5/5. The retry lines in the terminal show that the service was still pushing back: 10 of the 15 model tries hit at least one server error (`[retry] service pushed back (server error)`), the worst needing four retries (1 + 2 + 4 + 8 seconds) before it succeeded. Before the change each of those would have ended the run. Limits of this evidence: it is one run of five tries per scenario, and the service may also have been less busy than during the before run. The retries cover about 31 seconds in total, so a longer outage would still stop the agent, with the readable message.



---

## What's Still Broken

No criterion was missed in the after run (all five at 5/5), so nothing below is a failed target. These are the weaknesses I can show evidence for that the criteria do not catch.

**1. The targets were too loose.** Criteria 1, 4 and 5 were set at 4 of 5 to leave room for model failures. After the retry fix all three reached 5/5, so the targets did not constrain the agent. I would tighten criteria 1, 4 and 5 to 5 of 5. I did not change them: a target is only revised when it could not be measured, and this one could.

**2. A long model outage still stops the agent.** The retries cover about 31 seconds in total (1 + 2 + 4 + 8 + 16 s). A longer outage ends the run with the readable "model couldn't be reached" message, but no outfit or fit card. If I had more time I would return the search results and the cheaper alternatives together with that message, so the user still gets something. I stopped because the retry fixes the failure I observed, and "partial output when the model is down" needs its own criterion that this unit did not set.

**3. The query parser misreads some phrasings.** `parse_query` in `agent.py` is a regex. "nothing over thirty dollars" gives no price ceiling and is silently ignored, and `jacket over $30` is parsed as a ceiling of $30, which is the opposite of what the user asked. I would detect "over" / "more than" and either reject the query with a message or support a minimum price. I stopped because changing the parser would have changed the inputs between the before and after runs.

**4. Search matching is loose.** A listing only needs one shared keyword, so `graphic tee` returns `Mesh Long-Sleeve Top — Black` (its description mentions "graphic tee"), and `compare_prices` suggests long-sleeve tops as "cheaper alternatives" to a baby tee. I would weight title and style-tag matches above description matches and require a minimum score. I stopped because no criterion measures relevance, so I could not have shown it helped.



<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 3

       [ ] criteria.md has five numbered criteria, each with a target
       [ ] Each criterion has a reason underneath it
       [ ] All five unit 3 sections above have real content
       [ ] Tool Inventory: all three tools, inputs WITH TYPES, a specific
           return value, and the empty case
       [ ] Planning Loop names the branch rule and agent.py::run_agent
       [ ] Sample Run: one full query plus the three per-tool tests, as text
       [ ] At least four new commits
       [ ] Repository URL submitted — WRITE IT DOWN, you submit the same one
           next unit

     SUBMISSION CHECKLIST — unit 4

       [ ] mcp_server.py exists with one tool registered
           (or a written record of exactly where the rewire broke)
       [ ] Run Log — Before, five criteria, five tries each
       [ ] Real output pasted underneath, naming file and function
       [ ] A verdict on every criterion
       [ ] A diagnosis for every miss, naming a place AND a mechanism
       [ ] Loop Trace, with the MCP call visible in it
       [ ] All three failure modes triggered and handled
       [ ] One improvement, with Run Log — After in the same format
       [ ] What's Still Broken
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository. Your commit history is what
     shows your criteria existed before your results did.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
