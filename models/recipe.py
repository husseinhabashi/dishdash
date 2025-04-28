from bson.objectid import ObjectId
import pymongo

def save_recipe(db, recipe):
    return db.recipes.update_one({'_id': recipe.recipeID},
                               {"$set": 
                                {
                                    'owner': recipe.ownerID,
                                    'name': recipe.name,
                                    'image': recipe.image,
                                    'category': recipe.category,
                                    'dietary': recipe.dietary,
                                    'flavor': recipe.flavor,
                                    'difficulty': recipe.difficulty,
                                    'description': recipe.description,
                                    'favorites_count': recipe.favorites_count
                                }
                               },upsert=True)
def test_recipes_stuff(db):
    user = db.users.find_one({'email': 'daniel@email.com'})
    add_favorite(db, user['_id'],ObjectId("67dc6549376b70409e358a79"))

def search_recipes(db, name='', category='', flavor='', difficulty='', dietary='', use_text_search=False):
    query = {}
    
    if name:
        if use_text_search:
            if 'search_index' not in [idx['name'] for idx in db.recipes.list_indexes()]:
                db.recipes.create_index([('name', pymongo.TEXT)], name='search_index', default_language='english')
            query['$text'] = {'$search': name}
        else:
            # Case-insensitive partial name search (more flexible)
            query['name'] = {'$regex': name, '$options': 'i'}
    
    if category:
        query['category'] = {'$eq':category}
        
    if flavor:
        query['flavor'] = {'$eq':flavor}
        
    if difficulty:
        query['difficulty'] = {'$eq':difficulty}
    if dietary:
        query['dietary'] = {'$in':[dietary,"None"]}
    
    return [Recipe(x) for x in db.recipes.find(query)]
    
def get_favorites(db, userid):
    user = db.users.find_one({'_id': userid})
    if not user:
        return
    
    return [Recipe(x) for x in db.recipes.find({'_id':{'$in':user.get('favorites',[])}})]


def add_favorite(db, userid, recipeid):
    user = db.users.find_one({'_id': userid})
    if not user:
        return
    
    # Add to users favorites
    db.users.update_one({'_id':userid},
                      {'$addToSet':{"favorites":recipeid}})
    
    # Increase recipe favorites count
    db.recipes.update_one({'_id':recipeid},
                        {'$inc':{'favorites_count': 1}})

def remove_favorite(db, userid, recipeid):
    user = db.users.find_one({'_id': userid})
    if not user:
        return
    
    db.users.update_one({'_id':userid},
                      {'$pull':{"favorites":recipeid}})
    
    db.recipes.update_one({'_id':recipeid},
                        {'$inc':{'favorites_count': -1}})

def get_recipes(db):
    return [Recipe(x) for x in db.recipes.find()]

def get_recipe(db, id):
    recipe = db.recipes.find_one({'_id':ObjectId(id)})
    if recipe:
        return Recipe(recipe)
    
def get_user_recipes(db, userid):
    if not userid:
        return []
    return [Recipe(x) for x in db.recipes.find({'owner': userid})]

def delete_recipe(db, recipe_id):
    # string ID to objectId if needed
    if isinstance(recipe_id, str):
        recipe_id = ObjectId(recipe_id)

    return db.recipes.delete_one({'_id': recipe_id})



class Recipe:
    recipeID = None
    ownerID = None
    name = None
    description = None
    image = None
    category = None
    flavor = None
    difficulty = None
    dietary = None
    favorites_count = 0
    

    def __init__(self, recipe_cursor=None):
        self.recipeID = recipe_cursor and ObjectId(recipe_cursor['_id']) or ObjectId()
        if not recipe_cursor:
            return
        self.ownerID = recipe_cursor['owner']
        self.name = recipe_cursor['name']
        self.image = recipe_cursor['image']
        self.category = recipe_cursor['category']
        self.flavor = recipe_cursor['flavor']
        self.difficulty = recipe_cursor['difficulty']
        self.dietary = recipe_cursor.get('dietary',"None")
        self.description = recipe_cursor.get('description',"Default description!")
        self.favorites_count = recipe_cursor.get('favorites_count', 0)