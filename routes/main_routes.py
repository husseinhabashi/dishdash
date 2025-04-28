from flask import Blueprint, render_template, request, redirect, url_for, current_app
from dishdash.utils.helpers import get_current_user_document
import dishdash.models.recipe as recipe
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    user = get_current_user_document(current_app.users_collection)
    username = user['username'] if user else None
    profile_pic = user.get('profile_picture', 'default_picture.jpg') if user else 'default_picture.jpg'

    all_recipes = recipe.get_recipes(current_app.db)


    # Get featured recipes for the home page
    featured_recipes = all_recipes[:3] if all_recipes else []
    
    # Get recipe of the day for the home page
    recipe_of_the_day = None
    if featured_recipes:
        recipe_of_the_day = featured_recipes[0]  # For now, just use the first recipe
    return render_template('index.html', username=username, profile_pic=f'img/uploads/{profile_pic}', featured_recipes=featured_recipes, recipe_of_the_day=recipe_of_the_day)

@main_bp.route('/recipes')
def recipes():
    category = request.args.get('category', '')
    flavor = request.args.get('flavor', '')
    dietary = request.args.get('dietary', '')
    difficulty = request.args.get('difficulty', '')
    name = request.args.get('name','')

    # Get recipes with filters
    filtered_recipes = recipe.search_recipes(current_app.db, name=name, category=category, flavor=flavor, difficulty=difficulty,dietary = dietary) if (category or flavor or difficulty or dietary or name) else recipe.get_recipes(current_app.db)
    
    # If search_recipes returns None, fall back to all recipes
    if filtered_recipes is None:
        filtered_recipes = recipe.get_recipes(current_app.db)
    
    return render_template('recipes.html', recipes=filtered_recipes, selected_category=category, selected_flavor=flavor, selected_dietary=dietary, selected_difficulty=difficulty, name = name)

@main_bp.route("/add_recipe", methods=['GET', 'POST'])
def add_recipe():
    return render_template('add_recipe.html')

@main_bp.route('/recipes/<recipe_id>')
def recipe_from_id(recipe_id):
    gotten_recipe = recipe.get_recipe(current_app.db,recipe_id)
    if not gotten_recipe:
        return redirect(url_for('main.recipes'))
        
    user = get_current_user_document(current_app.users_collection)
    favorite_info = "none"
    if user:
        favorite_info = "add"
        if gotten_recipe.recipeID in user.get('favorites',[]):
            favorite_info = "remove"
    return render_template('recipe_details.html',recipe = gotten_recipe,favorite_info=favorite_info)

@main_bp.route('/favorites/<recipe_id>')
def favorite_toggle(recipe_id):
    gotten_recipe = recipe.get_recipe(current_app.db,recipe_id)
    user = get_current_user_document(current_app.users_collection)
    if not user or not gotten_recipe:
        return redirect(url_for('main.recipe_from_id',recipe_id=recipe_id))
    print(gotten_recipe.recipeID in user.get('favorites',[]))
    if gotten_recipe.recipeID in user.get('favorites',[]):
        recipe.remove_favorite(current_app.db,user['_id'],gotten_recipe.recipeID)
    else:
        recipe.add_favorite(current_app.db,user['_id'],gotten_recipe.recipeID)
        
    return redirect(url_for('main.recipe_from_id',recipe_id=recipe_id))


@main_bp.route('/favorites')
def favorites():
    user = get_current_user_document(current_app.users_collection)
    if not user:
        return redirect(url_for('auth.login'))
    return render_template('favorites.html',recipes = recipe.get_favorites(current_app.db,user['_id']))

