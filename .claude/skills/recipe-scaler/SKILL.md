---
name: recipe-scaler
description: Scales a recipe's ingredient quantities up or down to a target serving size. Handles fractional unit conversions, rounds to sensible measurements, and flags ingredients that don't scale linearly. Use when the user provides a recipe and wants it adjusted for a different number of servings.
---

# Recipe Scaler Skill

## When to Use
- The user provides a recipe (with ingredients and serving size) and asks to scale it up or down.
- The user specifies a target serving size that differs from the original.
- The user wants human-readable measurements after scaling (e.g. "1 tsp + ½ tsp" instead of "1.5 tsp").

## When NOT to Use
- The user only asks for a unit conversion without a serving-size change.
- No original serving size is provided and cannot be reasonably inferred.
- The recipe is for a non-food context (e.g. chemistry, cosmetics) where culinary rounding rules don't apply.

## Expected Inputs
- **Recipe ingredient list**: each ingredient with quantity, unit, and name (e.g. "2 cups flour").
- **Original serving size**: the number of servings the recipe currently makes.
- **Target serving size**: the number of servings the user wants.

## Step-by-Step Instructions
1. Parse the user's message to extract the ingredient list, original serving size, and target serving size.
2. Write the ingredient list to a plain-text file (`recipe.txt`), one ingredient per line in the format `<quantity> <unit> <name>`.
3. Run the scaling script — this is the core computational step:
   ```
   python scripts/scale_recipe.py recipe.txt <original_servings> <target_servings>
   ```
   The script handles all arithmetic: applying the scale factor, converting units to the most readable form, expressing remainders as culinary fractions (½, ¼, ⅓, ¾), rounding count-based items (eggs, cloves), and flagging non-linear ingredients.
4. Capture the script's stdout output.
5. Present the output to the user. If warnings were emitted, briefly explain why those ingredients need manual adjustment (leavening chemistry, flavor intensity, etc.) in plain language.

## Expected Output Format
Return a scaled ingredient list in the same order as the original, one ingredient per line:

```
Scaled Recipe (serves <target>):
- <quantity> <unit> <ingredient>
- <quantity> <unit> <ingredient>
...

Warnings:
- [non-linear] <ingredient>: scaling may affect texture/rise/flavor — adjust to taste.
```

If there are no warnings, omit the Warnings section.

## Limitations and Checks
- **Non-linear ingredients**: baking powder, baking soda, salt, yeast, spices, and leavening agents do not scale directly. Flag these and recommend tasting/adjusting rather than applying the scale factor blindly.
- **Very large or small scale factors**: if the factor is greater than 4x or less than 0.25x, add a note that results may need further testing, as cooking times and techniques may also need adjustment.
- **Unit boundaries**: do not output quantities like "0.03 cups" — convert down to a smaller unit (tsp/tbsp) when the result is below ¼ cup.
- **Whole-item ingredients**: items measured by count (e.g. "2 eggs") should be rounded to the nearest whole number with a note if rounding was significant (>0.25 of a unit off).
