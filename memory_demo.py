"""
Style memory demo: two runs, the second shaped by what the first stored.

    python memory_demo.py
"""
import memory
from agent import run_agent, _show
from utils.data_loader import get_empty_wardrobe

memory.clear()  # start from nothing so the demo is repeatable

print("=== Run 1: empty wardrobe, and the user keeps the item ===")
_show(run_agent(
    query="looking for a vintage graphic tee under $30",
    wardrobe=get_empty_wardrobe(),
    remember_item=True,
))

print("\n=== Run 2: empty wardrobe again, but the memory now has an item ===")
_show(run_agent(
    query="high-waisted jeans under $40",
    wardrobe=get_empty_wardrobe(),
))