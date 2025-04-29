from flask import Blueprint, render_template, request, redirect, url_for, current_app, session
from ..utils.helpers import get_current_user_document
import dishdash.models.recipe as recipe
from ..utils.helpers import allowed_file, get_current_user_document
from werkzeug.utils import secure_filename
import os
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
        recipe_of_the_day = featured_recipes[0]  # For now just use the first recipe
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
    
    return render_template('recipes.html', recipes=filtered_recipes, selected_category=category, selected_flavor=flavor, selected_dietary=dietary, selected_difficulty=difficulty, name=name)

@main_bp.route('/my_recipes')
def my_recipes():
    user = get_current_user_document(current_app.users_collection)
    if not user:
        return redirect(url_for('auth.login'))
    
    # Get recipes created by the user
    user_recipes = recipe.get_user_recipes(current_app.db, user['_id'])
    
    return render_template('my_recipes.html', recipes=user_recipes)

@main_bp.route("/add_recipe", methods=['GET', 'POST'])
def add_recipe():
    if request.method == 'POST':
        users_collection = current_app.users_collection

        user = get_current_user_document(users_collection)
        if not user:
            return
        newRecipe = recipe.Recipe()
        newRecipe.ownerID = user['_id']
        newRecipe.name = request.form.get("title")
        newRecipe.description = request.form.get("description")
        newRecipe.category = request.form.get("category")
        newRecipe.flavor = request.form.get("flavor")
        newRecipe.difficulty = request.form.get("difficulty")
        newRecipe.dietary = request.form.get("dietary")
        newRecipe.favorites_count = 0


        file = request.files.get("image")
        if file and allowed_file(file.filename, current_app.config["ALLOWED_EXTENSIONS"]):
            ext = file.filename.rsplit('.', 1)[1].lower()
            new_filename = secure_filename(f"{newRecipe.recipeID}.{ext}")
            file_path = os.path.join(current_app.config["UPLOAD_FOLDER"], new_filename)
            
            try:
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                file.save(file_path)
                newRecipe.image = os.path.join("img/uploads/",new_filename)

            except Exception as e:
                print("profile_routes error: ", e)
                return
            recipe.save_recipe(current_app.db,newRecipe)
    return render_template('add_recipe.html')

@main_bp.route('/edit_recipe/<recipe_id>', methods=['GET', 'POST'])
def edit_recipe(recipe_id):
    gotten_recipe = recipe.get_recipe(current_app.db, recipe_id)
    if not gotten_recipe:
        return redirect(url_for('main.recipes'))
    
    user = get_current_user_document(current_app.users_collection)
    if not user or str(user['_id']) != str(gotten_recipe.ownerID):
        return redirect(url_for('main.recipe_from_id', recipe_id=recipe_id))
    
    if request.method == 'POST':
        gotten_recipe.name = request.form.get("title")
        gotten_recipe.description = request.form.get("description")
        gotten_recipe.category = request.form.get("category")
        gotten_recipe.flavor = request.form.get("flavor")
        gotten_recipe.difficulty = request.form.get("difficulty")
        gotten_recipe.dietary = request.form.get("dietary")
        
        file = request.files.get("image")
        if file and file.filename and allowed_file(file.filename, current_app.config["ALLOWED_EXTENSIONS"]):
            ext = file.filename.rsplit('.', 1)[1].lower()
            new_filename = secure_filename(f"{gotten_recipe.recipeID}.{ext}")
            file_path = os.path.join(current_app.config["UPLOAD_FOLDER"], new_filename)
            
            try:
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                file.save(file_path)
                gotten_recipe.image = os.path.join("img/uploads/", new_filename)
            except Exception as e:
                print("edit_recipe error: ", e)
        
        recipe.save_recipe(current_app.db, gotten_recipe)
        
        return redirect(url_for('main.recipe_from_id', recipe_id=recipe_id))
    
    return render_template('edit_recipe.html', recipe=gotten_recipe)

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

@main_bp.route('/delete_recipe/<recipe_id>')
def delete_recipe(recipe_id):
    # Get recipe
    gotten_recipe = recipe.get_recipe(current_app.db, recipe_id)
    if not gotten_recipe:
        return redirect(url_for('main.recipes'))
    
    # ensure user is the creator of the recipe
    user = get_current_user_document(current_app.users_collection)
    if not user:
        return redirect(url_for('main.recipes'))
    
    if str(user['_id']) == str(gotten_recipe.ownerID):
        # Delete
        recipe.delete_recipe(current_app.db, recipe_id)
        
    return redirect(url_for('main.recipes'))

