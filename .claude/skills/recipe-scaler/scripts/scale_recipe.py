#!/usr/bin/env python3
"""
scale_recipe.py

Scales a recipe from its original serving size to a target serving size.

Usage:
    python scale_recipe.py <recipe_file> <original_servings> <target_servings>

Recipe file format (plain text, one ingredient per line):
    <quantity> <unit> <ingredient name>

Example:
    2 cups flour
    1 tsp baking powder
    0.5 tsp salt
    2 eggs
    1 cup milk
"""

import sys
import re
from fractions import Fraction

# ---------------------------------------------------------------------------
# Unit tables — volume and weight kept separate so we never cross the two
# ---------------------------------------------------------------------------

# Volume units expressed in teaspoons
VOLUME_TO_TSP = {
    "tsp": 1, "teaspoon": 1, "teaspoons": 1,
    "tbsp": 3, "tablespoon": 3, "tablespoons": 3,
    "cup": 48, "cups": 48,
    "pint": 96, "pints": 96,
    "quart": 192, "quarts": 192,
    "gallon": 768, "gallons": 768,
}

# Volume ladder: largest → smallest (cup is the ceiling for typical kitchen use)
VOLUME_LADDER = [
    ("cup",  48),
    ("tbsp", 3),
    ("tsp",  1),
]

# Weight units expressed in ounces
WEIGHT_TO_OZ = {
    "oz": 1, "ounce": 1, "ounces": 1,
    "lb": 16, "pound": 16, "pounds": 16,
}

# Weight ladder: largest → smallest (stay in weight)
WEIGHT_LADDER = [
    ("lb", 16),
    ("oz", 1),
]

ALL_UNITS = {**VOLUME_TO_TSP, **WEIGHT_TO_OZ}

# Common culinary fractions (decimal → unicode symbol)
FRACTION_MAP = [
    (Fraction(1, 8), "⅛"),
    (Fraction(1, 4), "¼"),
    (Fraction(1, 3), "⅓"),
    (Fraction(3, 8), "⅜"),
    (Fraction(1, 2), "½"),
    (Fraction(5, 8), "⅝"),
    (Fraction(2, 3), "⅔"),
    (Fraction(3, 4), "¾"),
    (Fraction(7, 8), "⅞"),
]

# Ingredients that do not scale linearly
NON_LINEAR = {
    "baking powder", "baking soda", "salt", "yeast", "instant yeast",
    "active dry yeast", "cream of tartar", "vinegar", "lemon juice",
    "vanilla", "vanilla extract", "cayenne", "chili powder",
    "black pepper", "white pepper", "nutmeg", "cloves",
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def parse_quantity(raw: str) -> float:
    """Parse '1.5', '1/2', or '1 1/2' into a float."""
    raw = raw.strip()
    mixed = re.match(r"^(\d+)\s+(\d+)/(\d+)$", raw)
    if mixed:
        whole, num, den = int(mixed.group(1)), int(mixed.group(2)), int(mixed.group(3))
        return whole + num / den
    simple = re.match(r"^(\d+)/(\d+)$", raw)
    if simple:
        return int(simple.group(1)) / int(simple.group(2))
    return float(raw)


def format_quantity(value: float) -> str:
    """
    Convert a float into a human-readable culinary string.
    Remainder expressed as the nearest common fraction symbol.
    e.g. 1.5 → "1 ½", 0.25 → "¼", 2.0 → "2"
    """
    whole = int(value)
    remainder = value - whole

    if remainder < 0.01:
        return str(whole) if whole > 0 else "0"

    best_symbol, best_diff = None, float("inf")
    for frac, symbol in FRACTION_MAP:
        diff = abs(remainder - float(frac))
        if diff < best_diff:
            best_diff, best_symbol = diff, symbol

    # Remainder is very close to 1 — carry over to whole
    if best_diff > 0.09:
        best_symbol = f"{remainder:.2g}"

    return best_symbol if whole == 0 else f"{whole} {best_symbol}"


def best_volume_unit(tsp_value: float):
    """Pick the largest volume unit where the result is >= ¼."""
    for unit, factor in VOLUME_LADDER:
        converted = tsp_value / factor
        if converted >= 0.25:
            return format_quantity(converted), unit
    return format_quantity(tsp_value), "tsp"


def best_weight_unit(oz_value: float):
    """Pick the largest weight unit where the result is >= ¼."""
    for unit, factor in WEIGHT_LADDER:
        converted = oz_value / factor
        if converted >= 0.25:
            return format_quantity(converted), unit
    return format_quantity(oz_value), "oz"


def is_non_linear(name: str) -> bool:
    name_lower = name.lower()
    return any(term in name_lower for term in NON_LINEAR)


# ---------------------------------------------------------------------------
# Core logic
# ---------------------------------------------------------------------------

def parse_recipe(lines: list) -> list:
    """
    Parse recipe lines into ingredient dicts.
    Fields: quantity (float), unit (str|None), unit_type ('volume'|'weight'|None),
            name (str), count_item (bool)
    """
    ingredients = []
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        # Quantity: integer, decimal, simple fraction, or mixed number
        qty_pattern = r"([\d]+(?:\s+[\d]+/[\d]+|/[\d]+|\.\d+)?)"
        # Unit: one alphabetic word immediately after the quantity
        match = re.match(rf"^{qty_pattern}\s+([a-zA-Z]+)\s+(.+)$", line)

        if match:
            qty_str, word, rest = match.group(1), match.group(2), match.group(3)
            try:
                qty = parse_quantity(qty_str)
            except ValueError:
                qty = 1.0

            word_lower = word.lower()
            if word_lower in VOLUME_TO_TSP:
                unit, unit_type, name = word_lower, "volume", rest.strip()
            elif word_lower in WEIGHT_TO_OZ:
                unit, unit_type, name = word_lower, "weight", rest.strip()
            else:
                # Unrecognized word is part of the ingredient name (e.g. "eggs", "cloves")
                unit, unit_type, name = None, None, f"{word} {rest}".strip()

            ingredients.append({
                "quantity": qty, "unit": unit, "unit_type": unit_type,
                "name": name, "count_item": unit is None,
            })
        else:
            # No recognizable quantity+unit — treat whole line as a count item
            qty_only = re.match(r"^([\d]+(?:/[\d]+|\.\d+)?)\s+(.+)$", line)
            if qty_only:
                qty = parse_quantity(qty_only.group(1))
                name = qty_only.group(2).strip()
            else:
                qty, name = 1.0, line
            ingredients.append({
                "quantity": qty, "unit": None, "unit_type": None,
                "name": name, "count_item": True,
            })

    return ingredients


def scale_ingredients(ingredients: list, factor: float):
    results, warnings = [], []

    for ing in ingredients:
        scaled_qty = ing["quantity"] * factor
        name = ing["name"]

        if is_non_linear(name):
            warnings.append(name)

        if ing["unit_type"] == "volume":
            tsp_value = scaled_qty * VOLUME_TO_TSP[ing["unit"]]
            display_qty, display_unit = best_volume_unit(tsp_value)

        elif ing["unit_type"] == "weight":
            oz_value = scaled_qty * WEIGHT_TO_OZ[ing["unit"]]
            display_qty, display_unit = best_weight_unit(oz_value)

        else:
            # Count-based item — round to nearest whole number
            rounded = round(scaled_qty)
            rounded = max(1, rounded)
            diff = abs(scaled_qty - rounded)
            display_qty = str(rounded)
            display_unit = ""
            if diff > 0.25:
                warnings.append(
                    f"{name} (scaled to {scaled_qty:.2f}, rounded to {rounded} — verify this is acceptable)"
                )

        results.append({"display_qty": display_qty, "display_unit": display_unit, "name": name})

    return results, warnings


def format_output(scaled: list, warnings: list, target: int, factor: float) -> str:
    lines = [f"Scaled Recipe (serves {target}):", ""]
    for item in scaled:
        unit_part = f" {item['display_unit']}" if item["display_unit"] else ""
        lines.append(f"  - {item['display_qty']}{unit_part} {item['name']}")

    if warnings:
        lines.append("")
        lines.append("Warnings (ingredients that may need manual adjustment):")
        for w in warnings:
            lines.append(f"  [!] {w}: scaling may affect flavor/texture — adjust to taste.")

    if factor > 4 or factor < 0.25:
        lines.append("")
        lines.append(
            f"  [!] Scale factor is {factor:.2f}x. At this range, cooking times and "
            "techniques may also need adjustment — test before serving."
        )

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python scale_recipe.py <recipe_file> <original_servings> <target_servings>")
        sys.exit(1)

    recipe_file = sys.argv[1]
    try:
        original = int(sys.argv[2])
        target = int(sys.argv[3])
    except ValueError:
        print("Error: original_servings and target_servings must be integers.")
        sys.exit(1)

    if original <= 0 or target <= 0:
        print("Error: serving sizes must be positive integers.")
        sys.exit(1)

    try:
        with open(recipe_file, "r") as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"Error: file '{recipe_file}' not found.")
        sys.exit(1)

    factor = target / original
    ingredients = parse_recipe(lines)
    scaled, warnings = scale_ingredients(ingredients, factor)
    print(format_output(scaled, warnings, target, factor))
