from bson.objectid import ObjectId
import pymongo
def save_recipe(db, recipe):

    return db.recipes.update_one({'_id': recipe.recipeID},
                                        {"$set": 
                                         {
                                         
                                          'owner': recipe.ownerID,
                                          'name' : recipe.name,
                                          'image' : recipe.image,
                                          'category' : recipe.category,
                                          'flavor' : recipe.flavor,
                                          'difficulty' : recipe.difficulty,
                                          'description' : recipe.description
                                          }
                                         },upsert=True)

def test_recipes_stuff(db):
    user = db.users.find_one({'email': 'daniel@email.com'})
    add_favorite(db, user['_id'],ObjectId("67dc6549376b70409e358a79"))

def get_search_terms_from_post(request):
    if not request.method == "POST":
        raise TypeError("Request must be a post request")
    return request.form.get("category"), request.form.get("flavor"), request.form.get("difficulty"), request.form.get("name")

def search_recipes(db, name, category, flavor, difficulty):
    # create a text index for searching by name if one doesnt already exist
    db.recipes.create_index([('name', pymongo.TEXT)], name='search_index', default_language='english')
    return [Recipe(x) for x in db.recipes.find({'category':category,"flavor":flavor,"difficulty":difficulty,"$text":{"$search":name}})]

    
def get_favorites(db, userid):
    user = db.users.find_one({'_id': userid})
    if not user:
        return
    
    return [Recipe(x) for x in db.recipes.find({'_id':{'$in':user.get('favorites',[])}})]


def add_favorite(db, userid, recipeid):
    user = db.users.find_one({'_id': userid})
    if not user:
        return
    
    return db.users.update_one({'_id':userid},
                             {
                                 '$addToSet':{"favorites":recipeid}
                             }
                             )

def remove_favorite(db, userid, recipeid):
    user = db.users.find_one({'_id': userid})
    if not user:
        return
    
    return db.users.update_one({'_id':userid},
                             {
                                 '$pull':{"favorites":recipeid}
                             }
                             )

def get_recipes(db):
    
    return [Recipe(x) for x in db.recipes.find()]

def get_recipe(db, id):
    recipe = db.recipes.find_one({'_id':ObjectId(id)})
    if recipe:
        return Recipe(recipe)
    



class Recipe:
    recipeID = None
    ownerID = None
    name = None
    description = None
    image = None
    category = None
    flavor = None
    difficulty = None
    
    def __init__(self):
        self.recipeID = ObjectId()
        pass
    def __init__(self, recipe_cursor):
        self.recipeID = ObjectId(recipe_cursor['_id'])
        self.ownerID = recipe_cursor['owner']
        self.name = recipe_cursor['name']
        self.image = recipe_cursor['image']
        self.category = recipe_cursor['category']
        self.flavor = recipe_cursor['flavor']
        self.difficulty = recipe_cursor['difficulty']
        self.description = recipe_cursor.get('description',"Default description!")