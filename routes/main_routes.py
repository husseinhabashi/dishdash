from flask import Blueprint, render_template, request, redirect, url_for, current_app
from dishdash.utils.helpers import get_current_user_document
import dishdash.models.recipe as recipe
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    user = get_current_user_document(current_app.users_collection)
    username = user['username'] if user else None
    profile_pic = user.get('profile_picture', 'default_picture.jpg') if user else 'default_picture.jpg'
    return render_template('index.html', username=username, profile_pic=f'img/uploads/{profile_pic}')

@main_bp.route('/recipes')
def recipes():
    
    return render_template('recipes.html',recipes = recipe.get_recipes(current_app.db))

@main_bp.route("/add_recipe")
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

