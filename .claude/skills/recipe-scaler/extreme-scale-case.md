# Recipe Scaler — Extreme Scale + Metric Units Test

## Prompt

"I want to scale my sourdough bread recipe that makes 1 loaf to make 10 loaves: 500g flour, 375g water, 100g sourdough starter, 10g salt, 5g yeast. Scale everything up for a commercial bakery run."

---

## Original Recipe (serves 1 loaf)

- 500g flour
- 375g water
- 100g sourdough starter
- 10g salt
- 5g yeast

---

## Script Output

**Command run:**
```
python scripts/scale_recipe.py sourdough.txt 1 10
```

**Scale factor:** 10 ÷ 1 = 10x

```
Scaled Recipe (serves 10):

  - 10 500g flour
  - 10 375g water
  - 10 100g sourdough starter
  - 10 10g salt
  - 10 5g yeast

Warnings (ingredients that may need manual adjustment):
  [!] 10g salt: scaling may affect flavor/texture — adjust to taste.
  [!] 5g yeast: scaling may affect flavor/texture — adjust to taste.

  [!] Scale factor is 10.00x. At this range, cooking times and techniques may also need adjustment — test before serving.
```

---

## Skill Limitation: Metric Units Not Supported

The script correctly identified the non-linear ingredients (salt, yeast) and correctly triggered the extreme scale factor warning (10x > 4x). However, it **failed to parse gram-based quantities**. The unit `g` is not in the script's unit table, so each ingredient line was treated as a single count item and multiplied by 10 as a whole string — producing output like `10 500g flour` instead of `5000g flour`.

**This is a known limitation of the current script.** It supports US customary culinary units only (tsp, tbsp, cup, oz, lb). Metric units (g, kg, ml, L) are not yet handled.

---

## Correct Scaled Output (manual calculation)

The arithmetic the script intended to perform:

| Ingredient         | Original | Scaled (×10) | Practical Label  |
|--------------------|----------|--------------|------------------|
| Flour              | 500g     | 5000g        | 5 kg             |
| Water              | 375g     | 3750g        | 3.75 kg          |
| Sourdough starter  | 100g     | 1000g        | 1 kg             |
| Salt               | 10g      | 100g         | 100g ⚠️          |
| Yeast              | 5g       | 50g          | 50g ⚠️           |

---

## Warnings Explained

- **Salt** — does not scale linearly at 10x. At commercial scale, over-salting is a common mistake. Start at 70–80g and adjust to taste before committing to the full 100g.
- **Yeast** — leavening power does not increase proportionally with quantity. At 10x, 50g of yeast may cause over-proofing or an unpleasant yeasty flavor. A professional baker's guideline is to use 60–70% of the linearly scaled yeast amount and adjust proofing time.
- **Extreme scale factor (10x)** — dough temperature, mixing time, fermentation behavior, and oven spring all change significantly at commercial batch sizes. These cannot be accounted for by ingredient scaling alone. Proofing time and baking time will need independent testing.

---

## Recommended Fix for the Script

To support this use case, add metric units to the unit tables in `scale_recipe.py`:

```python
# Metric volume (in ml as base)
METRIC_VOLUME = {"ml": 1, "milliliter": 1, "l": 1000, "liter": 1000}

# Metric weight (in grams as base)
METRIC_WEIGHT = {"g": 1, "gram": 1, "grams": 1, "kg": 1000, "kilogram": 1000}
```

And update the parser to recognize unit strings like `500g` (no space between quantity and unit), which is the standard way metric weights appear in recipes.
