import os
from flask import Flask, render_template, redirect, request, url_for
from flask_pymongo import PyMongo
from bson.objectid import ObjectId 

app = Flask(__name__)
app.config["MONGO_DBNAME"] = 'place_names_site'
app.config["MONGO_URI"] = os.getenv('MONGO_URI', 'mongodb+srv://root:r00tUser@myfirstcluster-bhsq8.mongodb.net/place_names_site?retryWrites=true&w=majority')

mongo = PyMongo(app)


@app.route('/')
@app.route('/get_place_names')
def get_place_names():
    return render_template("placeNames.html", place_names=mongo.db.place_names.find())

@app.route('/add_place_name')
def add_place_name():
    return render_template('addPlaceName.html',
                           locations=mongo.db.locations.find())
                           
@app.route('/insert_place_name', methods=['POST'])
def insert_place_name():
    place_names = mongo.db.place_names
    place_names.insert_one(request.form.to_dict())
    return redirect(url_for('get_place_names'))
 

if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
            port=int(os.environ.get('PORT')),
            debug=True)