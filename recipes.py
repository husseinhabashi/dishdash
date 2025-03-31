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