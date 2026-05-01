# Recipe Scaler — Edge Case Test (Fractional Egg)

## Prompt

"Scale this pancake recipe that serves 4 down to serve 1: 1 cup flour, 2 tsp baking powder, 0.5 tsp salt, 1 cup milk, 1 egg, 2 tbsp butter. Make sure to handle the egg carefully since you can't use a fraction of an egg."

---

## Original Recipe (serves 4)

- 1 cup flour
- 2 tsp baking powder
- 0.5 tsp salt
- 1 cup milk
- 1 egg
- 2 tbsp butter

---

## Script Output

**Command run:**
```
python scripts/scale_recipe.py pancakes.txt 4 1
```

**Scale factor:** 1 ÷ 4 = 0.25x

```
Scaled Recipe (serves 1):

  - ¼ cup flour
  - ½ tsp baking powder
  - ⅛ tsp salt
  - ¼ cup milk
  - 1 egg
  - ½ tbsp butter

Warnings (ingredients that may need manual adjustment):
  [!] baking powder: scaling may affect flavor/texture — adjust to taste.
  [!] salt: scaling may affect flavor/texture — adjust to taste.
  [!] egg (scaled to 0.25, rounded to 1 — verify this is acceptable): scaling may affect flavor/texture — adjust to taste.
```

---

## Warnings Explained

- **Egg** — the script correctly flagged this: a true quarter-egg (0.25) is not practical, so it rounded up to 1 whole egg. This is the right call for a single serving — one egg is standard for a small batch of pancakes. The batter may be slightly richer or more bound than the original per-serving ratio, but it will work. If you want to stay closer to the original ratio, you could beat the egg first and use roughly a quarter of it (~1 tablespoon).
- **Baking powder** — leavening does not scale perfectly; ½ tsp is a reasonable amount for one serving but taste and texture may vary slightly from the full batch.
- **Salt** — ⅛ tsp is the mathematically correct scaled amount and is fine at this scale, but flavor sensitivity means you may want a small pinch rather than a precise measure.
