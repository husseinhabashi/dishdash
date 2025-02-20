from flask import Flask, render_template
# from pymongo import MongoClient

app = Flask(__name__)

# client = MongoClient("mongodb://")  

@app.route('/')
def index():
 return render_template('index.html')

@app.route('/profile')
def profile():
 return render_template('profile.html')

if __name__ == '__main__':
    app.run(debug=True)
