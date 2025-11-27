import requests
from flask import Flask, render_template, request
import os
from dotenv import load_dotenv


load_dotenv()
API_KEY = os.getenv("API_KEY")

app = Flask(__name__)

# FUNCTION TO GET COCKTAILS FROM API:
def get_cocktails(query="margarita"):
    url = f"https://www.thecocktaildb.com/api/json/v2/{API_KEY}/search.php?s={query}"
    response = requests.get(url)
    data = response.json()
    drinks = data.get("drinks", []) or []

    # Remove duplicates
    # unique_drinks = []
    # seen_names = set()

    # for drink in drinks:
    #     name = drink.get("strDrink")
    #     if name not in seen_names:
    #         seen_names.add(name)
    #         unique_drinks.append(drink)


    # BUILDING COCKTAIL LIST:
    cocktails = []

    for drink in drinks:
         cocktails.append({
              "id": drink.get("idDrink"),
              "name": drink.get("strDrink"),
              "image": drink.get("strDrinkThumb")

         })
                
    return cocktails

# FUNCTION TO GET FULL COCKTAIL DETAILS:
def get_cocktail_details(cocktail_id):
    url = f"https://www.thecocktaildb.com/api/json/v2/{API_KEY}/lookup.php?i={cocktail_id}"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print("Error fetching details", e)
        return None
    
    drinks = data.get("drinks") or []
    if not drinks:
        return None
    
    drink = drinks[0]

    # COLLECTING INGREDIENTS AND MEASURES:
    ingredients = []
    # COCKTAILDB HAS UP TO 15 INGREDIENTS:
    for i in range(1, 16):
        ingredient = drink.get(f"strIngredient{i}")
        measure = drink.get(f"strMeasure{i}")
        if ingredient and ingredient.strip():
            ingredients.append(f"{measure.strip() if measure else ''} {ingredient.strip()}".strip())

    return {
        "id": drink.get("idDrink"),
        "name": drink.get("strDrink"),
        "image": drink.get("strDrinkThumb"), 
        "alcoholic": drink.get("strAlcoholic"),
        "glass": drink.get("strGlass"),
        "instructions": drink.get("strInstructions"),
        "ingredients": ingredients
    }


# FUNCTION TO GET RANDOM COCKTAIL:
def get_random_cocktail():
    url = f"https://www.thecocktaildb.com/api/json/v2/{API_KEY}/random.php"
    response = requests.get(url)
    data = response.json()
    drinks = data.get("drinks", [])

    if not drinks:
        return None 
    
    drink = drinks[0]

    return {
        "id": drink.get("idDrink"),
        "name": drink.get("strDrink"),
        "image": drink.get("strDrinkThumb"), 
        
    }


# HOMEPAGE ROUTE:
@app.route('/', methods=["GET", "POST"])
def home():
    cocktails = []
    message = None

    if request.method == "POST":
        action = request.form.get("action")

        if action == "search":
            search_query = request.form.get("cocktail_name" or "").strip()

            if not search_query:
                message = "Please enter cocktail name."
            else:
                cocktails = get_cocktails(search_query)
                if not cocktails:
                    message = f"No results found for'{search_query}'."

        elif action == "random":
            cocktail = get_random_cocktail()
            if cocktail:
                cocktails = [cocktail]
            else:
                message = "No random cocktail found."

        return render_template('index.html', cocktails=cocktails, message=message)
        # ELSE STATEMENT FOR GET:
    else:
        return render_template('index.html', cocktails=[], message=None)
    

# COCKTAIL DETAILS ROUTE:
@app.route('/details/<cocktail_id>')
def cocktail_details(cocktail_id):
    cocktail = get_cocktail_details(cocktail_id)
    if not cocktail:
        message = "Unable to fetch details."
        return render_template('details.html', cocktail=None, message=message)
    return render_template('details.html', cocktail=cocktail)





if __name__ == '__main__':
    app.run(debug=True)
