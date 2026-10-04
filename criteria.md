# Acceptance criteria — FitFindr

Five criteria that say what "working" means for this agent, written in unit 3
**before** any results existed.

An acceptance criterion names a target: a number, a count, a rate, or something
a person could plainly observe. *"The agent handles errors"* is an opinion.
*"When search returns nothing, the agent stops before calling the second tool,
in 5 of 5 tries"* is a criterion.

Under each one, write a sentence or two on **why that target** and not a
stricter one. A reason that says something about your tools, your loop, or the
data earns credit; *"80% seemed reasonable"* does not.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

**Two are written for you. You write three.**

---

## 1. A matching query completes all three tools

Given a query that matches at least one listing, the agent completes all three
tool calls and returns a fit card — in at least 4 of 5 tries.

**Why this target:**
I picked 4 of 5 because `suggest_outfit` and `create_fit_card` are two serial LLM calls, and the loop has no retry logic. If either one returns malformed output (for example, a fit card with no text), the run fails with nothing to recover it. One miss in 5 leaves room for that. I did not pick 5 of 5 because two chained non-deterministic calls multiply the failure chance, and I did not pick 3 of 5 because the search step is fixed by the pre-selected queries, so it should not be a source of failure.

---

## 2. An impossible query stops before the second tool

Given a query that matches no listings, the agent stops before calling
`suggest_outfit` and returns a message naming what to change — 5 of 5 tries.

**Why this target:**
I picked 5 of 5 because this path is deterministic code (an `if not search_results:` branch in `agent.py`), not a model call. An empty list from `search_listings` must always stop the loop. Any miss means a bug in my loop, so there is no tolerance. I use 5 different queries so that one hard-coded case cannot pass all 5 runs.
---

## 3. Something about state

Run two different queries in the same session. After the second run, `session["selected_item"]["id"]` equals the id of the first result of the second search, and does not equal the id from the first query — 5 of 5 pairs of queries.


**Why this target:**
I picked 5 of 5 because the selection is a deterministic in-memory assignment, with no model call or network step. If the id is stale, the loop failed to overwrite or reset `selected_item`, which is a code bug. Carrying state across turns is the easiest thing to forget in a loop, so a failure here would be a real defect and not noise. I use 5 pairs with different top results so the two ids always differ.

---

## 4. Something about the fit card
Given a valid item and outfit, run `create_fit_card` 5 times. At least 4 of the 5 outputs contain both the item's price digits (for example "24") and the platform name, and no two of the 5 outputs are word-for-word identical.


**Why this target:**
I picked 4 of 5 because price and platform go into the prompt as fixed fields, but the caption is written by the LLM. The model may drop the platform, or return a refusal such as "I cannot generate a card". The price match checks for the digits only, so "$24" and "about $24" both pass. I did not pick 5 of 5 because the facts are not inserted by code but depend on the model copying them. The "not identical" check is a separate, easy condition. With temperature above 0 it should always pass, and it would only fail if the output were cached or the temperature were 0.


---

## 5. Your choice

Given a user with an empty wardrobe, `suggest_outfit` raises no exception and returns a string of at least 50 characters that contains none of "please add", "no items", or "error" — in at least 4 of 5 tries.



**Why this target:**
I picked 4 of 5 because an empty wardrobe list goes into the prompt and the LLM decides what to write. The main failure I expect is a refusal such as "Please add clothes to your wardrobe first", which the keyword check catches. This is model behavior, not a code branch, so I do not require 5 of 5. I did not pick 3 of 5 because I explicitly tell the prompt to give general advice, so refusals should be rare.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 4 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath it, like this:

         ## 4. Something about the fit card

         The fit card is different every time.

         **Why this target:** ...

         > **Revised in unit 4:** For 5 different items, the 5 fit cards share
         > no opening sentence.
         >
         > **Why revised:** "different" wasn't checkable — two cards that
         > differed by one word still counted. The new version is something I
         > can actually score.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "I said the empty search stops it 5 of 5 times, but I got 3 of 5,
            so 3 of 5 is more realistic."

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.
     ───────────────────────────────────────────────────────────────────────── -->
