import requests
from flask import Flask, render_template, request

app = Flask(__name__)

# FUNCTION TO GET COCKTAILS FROM API
def get_cocktails(query="margarita"):
    url = f"https://www.thecocktaildb.com/api/json/v1/1/search.php?s={query}"
    # print("Fetching from URL:", url)
    response = requests.get(url)
    data = response.json()
    print(data)
    drinks = data.get("drinks", [])

    # if drinks == None:
    #     return []

    # Remove duplicates
    unique_drinks = []
    seen_names = set()

    for drink in drinks:
        name = drink.get("strDrink")
        if name not in seen_names:
            seen_names.add(name)
            unique_drinks.append(drink)


    # Building final list w/ details
    full_cocktail_list = []

    if unique_drinks:
        for drink in drinks:
            # collecting ingredients and measures
            ingredients = []
            #cocktailDB has upto 15 ingredients
            for i in range(1, 16):
                ingredient = drink.get(f"strIngredient{i}")
                measure = drink.get(f"strMeasure{i}")
                if ingredient and ingredient.strip():
                    ingredients.append(
                        f"{measure.strip() if measure else ''} {ingredient.strip()}".strip()
                        ) 
            full_cocktail_list.append({
                "name": drink.get("strDrink"),
                "image": drink.get("strDrinkThumb"), 
                "instructions": drink.get("strInstructions"),
                "ingredients": ingredients
            })
                
    return full_cocktail_list

# FUNCTION TO GET RANDOM COCKTAIL
def get_random_cocktail():
    url = "https://www.thecocktaildb.com/api/json/v1/1/random.php"
    response = requests.get(url)
    data = response.json()
    drinks = data.get("drinks", [])

    if not drinks:
        return None 
    
    drink = drinks[0]

    ingredients = []
    for i in range(1, 16):
                ingredient = drink.get(f"strIngredient{i}")
                measure = drink.get(f"strMeasure{i}")
                if ingredient and ingredient.strip():
                    ingredients.append(
                        f"{measure.strip() if measure else ''} {ingredient.strip()}".strip()
                        ) 
    return {
        "name": drink.get("strDrink"),
        "image": drink.get("strDrinkThumb"), 
        "instructions": drink.get("strInstructions"),
        "ingredients": ingredients
    }


# RANDOM ROUTE
# @app.route('/random')
# def random_cocktail():
#     cocktail = get_random_cocktail()
#     return render_template('index.html', cocktail=cocktail)

# HOMEPAGE ROUTE
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
        # ELSE STATEMENT FOR GET
    else:
        # pass
        return render_template('index.html', cocktails={})

if __name__ == '__main__':
    app.run(debug=True)
