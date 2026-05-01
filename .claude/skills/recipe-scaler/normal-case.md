# Recipe Scaler — Normal Case Test

## Prompt

"I have a chocolate chip cookie recipe that makes 24 cookies: 2.25 cups flour, 1 tsp baking soda, 1 tsp salt, 1 cup butter, 0.75 cup granulated sugar, 0.75 cup brown sugar, 2 large eggs, 2 tsp vanilla extract, 2 cups chocolate chips. Scale this recipe to make 60 cookies."

---

## Original Recipe (serves 24)

- 2.25 cups flour
- 1 tsp baking soda
- 1 tsp salt
- 1 cup butter
- 0.75 cup granulated sugar
- 0.75 cup brown sugar
- 2 large eggs
- 2 tsp vanilla extract
- 2 cups chocolate chips

---

## Script Output

**Command run:**
```
python scripts/scale_recipe.py cookies.txt 24 60
```

**Scale factor:** 60 ÷ 24 = 2.5x

```
Scaled Recipe (serves 60):

  - 5 ⅝ cup flour
  - ⅞ tbsp baking soda
  - ⅞ tbsp salt
  - 2 ½ cup butter
  - 1 ⅞ cup granulated sugar
  - 1 ⅞ cup brown sugar
  - 5 large eggs
  - 1 ⅔ tbsp vanilla extract
  - 5 cup chocolate chips

Warnings (ingredients that may need manual adjustment):
  [!] baking soda: scaling may affect flavor/texture — adjust to taste.
  [!] salt: scaling may affect flavor/texture — adjust to taste.
  [!] vanilla extract: scaling may affect flavor/texture — adjust to taste.
```

---

## Warnings Explained

- **Baking soda** — a chemical leavener; too much causes a soapy taste and over-rise. Start around ⅝–¾ tbsp and adjust.
- **Salt** — flavor intensity does not scale linearly; ⅝–¾ tbsp is a safer starting point than the full ⅞ tbsp.
- **Vanilla extract** — aromatics amplify at scale; 1–1¼ tbsp may be sufficient before it becomes overpowering. Taste as you go.
