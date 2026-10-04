# FitFindr
<!-- test commit -->
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

<!-- Five criteria, five tries each, in this exact format.

     Five, because your criteria are written out of five. Mark each try PASS
     or FAIL, count the passes, and read that count against your target — a
     row targeting 4 of 5 with three PASS cells is MISSED (3/5).

     `python run_eval.py --label before` runs everything and writes the table
     into results/. Paste it here and fill in the verdicts. -->

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |  |  |
| 2.  |  |  |  |  |  |  |  |
| 3.  |  |  |  |  |  |  |  |
| 4.  |  |  |  |  |  |  |  |
| 5.  |  |  |  |  |  |  |  |

**Real output from one try**, pasted as text, naming the file and function
that produced it:

```

```

---

## Verdicts and Diagnoses

<!-- MET or MISSED per criterion against LAST UNIT's target, plus a sentence on
     how you decided.

     Then, for every miss: which of the four places it happened — a tool, the
     loop's branch, the session, or the model's output — AND the mechanism.

     Not a diagnosis:  "The fit card was bad."
     A diagnosis:      "The fit card criterion missed on 2 of 5 items. Both had
                        an empty brand field. My prompt puts the brand in the
                        first sentence, so the card opened with a blank and read
                        like a fragment. The tool worked; the prompt assumed a
                        field that isn't always there."

     Look for a pattern. Three misses on the same tool is one problem, not
     three. -->

| # | Criterion | Target | Verdict | How I decided |
|---|---|---|---|---|
| 1 |  |  |  |  |
| 2 |  |  |  |  |
| 3 |  |  |  |  |
| 4 |  |  |  |  |
| 5 |  |  |  |  |

**Diagnoses**



---

## Loop Trace

<!-- One full run, printed step by step, with the MCP call visible in it.

     `python app.py ask '...' --trace` once you've added the trace.step()
     calls in Milestone 2.

     Worth pasting BOTH the happy path and the empty-search path. The empty
     one should be visibly shorter, because it stops. If your two traces are
     the same length, your branch isn't working — and this is the fastest way
     anyone will ever find that out. -->

**Happy path**

```

```

**Empty search**

```

```

**On the MCP move:** <!-- what changed in your code, and whether anything
behaved differently afterwards. If the rewire didn't work, say exactly where it
broke — the error text and the last thing that worked. That earns the point in
full. -->



---

## The Improvement

<!-- What you changed, why your diagnosis pointed at it, and the after-run in
     the same table format. One change, measured properly.

     `python run_eval.py --label after` -->

**What I changed:**

**Which failure it was meant to fix:**

### Run Log — After

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |  |  |
| 2.  |  |  |  |  |  |  |  |
| 3.  |  |  |  |  |  |  |  |
| 4.  |  |  |  |  |  |  |  |
| 5.  |  |  |  |  |  |  |  |

**Did it help, and how do I know:**

<!-- If it made things worse, say that. Honestly reported, that earns full
     credit and is more interesting than one that worked. -->



---

## What's Still Broken

<!-- For each criterion still missed: what you'd do, and why you stopped where
     you did. "I ran out of time" is fine if it's true. Pretending nothing is
     left is not. -->



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
