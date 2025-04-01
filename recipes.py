from bson.objectid import ObjectId
def save_recipe(mongo, recipe):

    return mongo.db.recipes.update_one({'_id': recipe.recipeID},
                                        {"$set": 
                                         {
                                         
                                          'owner': recipe.ownerID,
                                          'name' : recipe.name,
                                          'image' : recipe.image,
                                          'category' : recipe.category,
                                          'flavor' : recipe.flavor,
                                          'difficulty' : recipe.difficulty
                                          }
                                         },upsert=True)

def test_recipes_stuff(mongo):
    user = mongo.db.users.find_one({'email': 'daniel@email.com'})
    add_favorite(mongo, user['_id'],"test")
    print(mongo.db.users.update_one({'email':'daniel@email.com'},
                             {
                                 '$pull':{"favorites":"dd"}
                             }
                             ))

def search_recipes(mongo, name, category, flavor, difficulty):

    pass
    
def add_favorite(mongo, userid, recipeid):
    user = mongo.db.users.find_one({'_id': userid})
    if not user:
        return
    
    return mongo.db.users.update_one({'_id':userid},
                             {
                                 '$addToSet':{"favorites":recipeid}
                             }
                             )

def remove_favorite(mongo, userid, recipeid):
    user = mongo.db.users.find_one({'_id': userid})
    if not user:
        return
    
    return mongo.db.users.updateOne({'_id':userid},
                             {
                                 '$addToSet':{"favorites":recipeid}
                             }
                             )

def get_recipes(mongo, recipeid):
    
    return mongo.db.recipes.find()

class Recipe:
    recipeID = None
    ownerID = None
    name = None
    image = None
    category = None
    flavor = None
    difficulty = None
    
    def __init__(self):
        self.recipeID = ObjectId()
        pass