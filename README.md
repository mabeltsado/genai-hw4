# Recipe Scaler Skill — HW4

## What the Skill Does

The recipe-scaler skill takes any recipe and adjusts all ingredient quantities up or down to match a target serving size. It goes beyond simple multiplication — it converts scaled quantities into human-readable culinary measurements (e.g. `1.5 tsp` becomes `1 tsp + ½ tsp`), rounds count-based ingredients like eggs to the nearest whole number, and flags ingredients that are known to not scale linearly, such as salt, baking powder, yeast, and spices.

---

## Why I Chose It

I am always looking up new recipes, but I constantly run into the same problem: a recipe serves 6 and I only need 2, or I want to cook for a crowd and need to triple it. Adjusting serving sizes by hand is tedious and error-prone, especially when fractions get involved. Beyond the quantities, I also find it hard to think about how scaling affects nutrition — when a recipe doubles, so do the calories, but when leavening agents or salt double, the result can taste completely different. I wanted a tool that handles the math reliably and at least flags the places where human judgment still needs to step in.

---

## How to Use It

1. Have a recipe ready with an ingredient list, the original serving size, and your target serving size.
2. Write the ingredients to a plain-text file, one per line, in the format:
   ```
   <quantity> <unit> <ingredient name>
   ```
   Example:
   ```
   2 cups flour
   1 tsp baking powder
   2 eggs
   ```
3. Run the script from the terminal:
   ```
   python .claude/skills/recipe-scaler/scripts/scale_recipe.py <recipe_file> <original_servings> <target_servings>
   ```
4. Review the scaled output. Pay attention to any warnings — those ingredients may need manual tasting and adjustment rather than strict adherence to the scaled amount.

---

## What the Script Does

`scale_recipe.py` is the computational core of the skill. It handles everything that would be tedious or error-prone to do by hand:

- **Parses** each ingredient line, separating the quantity, unit, and name
- **Applies** the scale factor (`target ÷ original`) to every quantity
- **Keeps volume and weight in their own unit families** — volume stays in tsp/tbsp/cup and weight stays in oz/lb, so you never get an output like "⅓ gallon of flour"
- **Picks the most readable unit** for the result — e.g. 6 tsp becomes 2 tbsp, 48 tsp becomes 1 cup
- **Formats remainders as culinary fractions** (½, ¼, ⅓, ¾, ⅛) instead of decimals
- **Rounds count-based items** (eggs, cloves, etc.) to the nearest whole number and flags them if the rounding is significant
- **Flags non-linear ingredients** — baking powder, baking soda, salt, yeast, vanilla, and spices are automatically identified and marked with a warning
- **Warns on extreme scale factors** — anything above 4x or below 0.25x gets an advisory that cooking times and techniques may also need adjustment

The model's role is to parse the user's request, call the script, and interpret the warnings conversationally. The script does all the deterministic math.

---

## What Worked Well

- **Fraction formatting** produced clean, realistic outputs like `2 ½ cup butter` and `⅛ tsp salt` that match how recipes are actually written
- **Non-linear ingredient detection** worked correctly across all three test cases — baking powder, salt, yeast, and vanilla were all flagged without any false positives on neutral ingredients like flour or chocolate chips
- **Count-item handling** for eggs worked exactly as intended: the script rounded 0.25 eggs to 1, flagged it with the exact decimal value, and the model explained the practical workaround (beating the egg and using a tablespoon)
- **Extreme scale factor warning** triggered correctly at 10x (sourdough test), prompting useful guidance about proofing and baking time adjustments at commercial scale
- **Unit separation** between volume and weight prevented nonsensical cross-unit conversions

---

## Limitations That Remain

- **No metric unit support** — the script only understands US customary units (tsp, tbsp, cup, oz, lb). Gram- and kilogram-based recipes (common in professional baking and most non-US recipes) are not parsed correctly, as the sourdough test demonstrated. Adding `g`, `kg`, `ml`, and `L` to the unit tables is the most important remaining fix.
- **No-space metric format** — recipes often write `500g` with no space between the number and unit. The parser currently requires a space and will not recognize this format even if grams are added to the unit table.
- **No calorie scaling** — a natural extension of this skill would be to scale nutritional information alongside ingredients. Right now the skill adjusts quantities but does not calculate or display per-serving or total calories, which was part of the original motivation for building it.
- **Serving size is always an integer** — the script requires whole numbers for serving sizes and cannot handle inputs like "scale from 4 to 6.5 servings."
- **No support for ingredient ranges** — recipes sometimes specify ranges like "1–2 tsp vanilla." The parser does not handle this format.
- **Unit ladder caps at cup** — for very large batches (restaurant or commercial scale), the output stays in cups even when quarts or gallons would be more practical. The ladder was intentionally capped at cup for home cooking but could be made configurable.
