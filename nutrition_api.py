import requests


USDA_API_KEY = "kMAwFEYVrEHWy7gxddjpZe0VoWe1i1CDtdDg2KdD"
USDA_SEARCH_URL = "https://api.nal.usda.gov/fdc/v1/foods/search"


def search_usda_foods(query, page_size=8):
    params = {"query": query, "pageSize": page_size, "api_key": USDA_API_KEY}

    try:
        response = requests.get(USDA_SEARCH_URL, params=params)
        if response.status_code != 200:
            return []

        result = response.json()
        foods = []

        for food in result.get("foods", []):
            calories = protein = carbs = fat = 0

            for nutrient in food.get("foodNutrients", []):
                name = nutrient.get("nutrientName", "").lower()
                value = nutrient.get("value", 0)

                if "energy" in name:
                    calories = value
                elif "protein" in name:
                    protein = value
                elif "carbohydrate" in name:
                    carbs = value
                elif "fat" in name:
                    fat = value

            foods.append({
                "name": food.get("description", "Unknown"),
                "calories": calories,
                "protein": protein,
                "carbs": carbs,
                "fat": fat,
            })

        return foods
    except Exception:
        return []
