import os
import sys
from flask import Flask, render_template, redirect, request, url_for, session, flash
from flask_pymongo import PyMongo
from bson.objectid import ObjectId 

DB_NAME = os.getenv("DB_NAME")
DB_URI = os.getenv("DB_URI")


app = Flask(__name__)
app.config["MONGO_DBNAME"] = DB_NAME
app.secret_key = os.urandom(24)
app.config["MONGO_URI"] = DB_URI

mongo = PyMongo(app)


#######################################Helper Functions######################################################
""" These functions are used to ensure that there is no duplicate data in the database before adding or editing
    users, locations or place names"""
    
def valid_user():
    username = request.form.get("user_name")
    if mongo.db.users.find_one({"userName": username}) is None:
        return True
    else:
        return False

        
def valid_location():
    locationName = request.form.get("location_name")
    if mongo.db.locations.find_one({"location_name": locationName}) is None:
        return True
    else:
        return False
        
def valid_place_name():
    engName = request.form.get("eng_name")
    if mongo.db.place_names.find_one({"eng_name": engName}) is None:
        return True
    else:
        return False
    
##########################################View Functions for place names###################################################
""" These functions provide the functionality to - view place names, add a place name, edit a place name and delete a place name"""
""" Except for get_place_names and sort_place_names all other place name functions require user or admin privileges"""

@app.route("/")
@app.route("/get_place_names")
def get_place_names():
    #active_place_name is the place name that is been added or edited -> allows the page to scroll to the correct point
    return render_template("placeNames.html", place_names=mongo.db.place_names.find(), active_place_name="Initial")

@app.route("/add_place_name")
def add_place_name():
    if "username" in session:
        return render_template("addPlaceName.html", locations=mongo.db.locations.find())
    else:
        return redirect(url_for("login_page"))
                           
@app.route("/insert_place_name", methods=["POST"])
def insert_place_name():
    if "username" in session:
        if valid_place_name():
            place_names = mongo.db.place_names
            place_names.insert_one(
            {
                "eng_name":request.form.get("eng_name"),
                "irl_name":request.form.get("irl_name"),
                "irl_meaning": request.form.get("irl_meaning"),
                "history": request.form.get("history"),
                "location":request.form.get("location"),
                "created_by":session['username'],
                "likes":0
            })
            the_active_place_name =request.form.get("eng_name")
            the_place_names =  mongo.db.place_names.find()
            return render_template("placeNames.html", place_names=the_place_names, active_place_name=the_active_place_name)
        else:
            #If its not a valid place name add error and return to page
            flash("Place Name '{}' already exists!".format(request.form.get("eng_name")))
            return redirect(url_for("add_place_name"))
    else:
        return redirect(url_for("login_page"))
    

@app.route("/edit_place_name/<place_name_id>")
def edit_place_name(place_name_id):
    if "username" in session:
        the_place_name =  mongo.db.place_names.find_one({"_id": ObjectId(place_name_id)})
        all_locations =  mongo.db.locations.find()
        return render_template("editPlaceName.html", place_name=the_place_name,
                               locations=all_locations) 
    else:
        return redirect(url_for("login_page"))
        
@app.route("/update_place_name/<place_name_id>", methods=["POST"])
def update_place_name(place_name_id):
    if "username" in session:
    
        #Checks to see if the primary key of the record has changed, if it has check to see if there is a conflicting name in the database
        #If not update the record else display an error
        if request.form.get("original_eng_name") == request.form.get("eng_name"):
            place_names = mongo.db.place_names
            place_names.update( {"_id": ObjectId(place_name_id)},{"$set" :
                {
                    "eng_name":request.form.get("eng_name"),
                    "irl_name":request.form.get("irl_name"),
                    "irl_meaning": request.form.get("irl_meaning"),
                    "history": request.form.get("history"),
                    "location":request.form.get("location")
                }})
            place_name = mongo.db.place_names.find_one({"_id": ObjectId(place_name_id)})
            the_active_place_name = place_name["eng_name"]
            the_place_names =  mongo.db.place_names.find()
            return render_template("placeNames.html", place_names=the_place_names, active_place_name=the_active_place_name)
        else:
            if valid_place_name():
                place_names = mongo.db.place_names
                place_names.update( {"_id": ObjectId(place_name_id)},{"$set" :
                {
                    "eng_name":request.form.get("eng_name"),
                    "irl_name":request.form.get("irl_name"),
                    "irl_meaning": request.form.get("irl_meaning"),
                    "history": request.form.get("history"),
                    "location":request.form.get("location")
                }})
                place_name = mongo.db.place_names.find_one({"_id": ObjectId(place_name_id)})
                the_active_place_name = place_name["eng_name"]
                the_place_names =  mongo.db.place_names.find()
                return render_template("placeNames.html", place_names=the_place_names, active_place_name=the_active_place_name)
            else:
                flash("Place Name '{}' already exists!".format(request.form.get("eng_name")))
                return redirect(url_for("edit_place_name", place_name_id=place_name_id))
    else:
        return redirect(url_for("login_page"))  
    
     

@app.route("/delete_place_name/<place_name_id>")
def delete_place_name(place_name_id):
    if "username" in session:
        mongo.db.place_names.remove({"_id": ObjectId(place_name_id)})
        return redirect(url_for("get_place_names"))
    else:
        return redirect(url_for("login_page")) 
    
@app.route("/sort_place_names", methods=["POST"])
def sort_place_names():
    #Sorts the results from the database based on the users selection
    #sorts decending if likes is selected ascending otherwise
    sortBy = request.form.get("sort_by")
    if sortBy == "likes":
        return render_template("placeNames.html", place_names=mongo.db.place_names.find().sort( sortBy ,-1), active_place_name="Initial")
    else:
        return render_template("placeNames.html", place_names=mongo.db.place_names.find().sort( sortBy ,1), active_place_name="Initial")

##########################################View functions for location##########################
""" These functions provide the functionality to - view locations, add a location, edit a location and delete a location"""
""" They are only accessible with admin privileges. This is checked before any action is taken """
    
@app.route("/get_locations")
def get_locations():
    try:
        if session["admin"] == "True":
            return render_template("locations.html", locations=mongo.db.locations.find())
    except:
            return redirect(url_for("login_page"))
      
                           
@app.route("/edit_location/<location_id>")
def edit_location(location_id):
    try:
        if session["admin"] == "True":
            return render_template("editLocation.html", location=mongo.db.locations.find_one({"_id": ObjectId(location_id)}))
    except:
            return redirect(url_for("login_page"))

@app.route("/update_location/<location_id>", methods=["POST"])
def update_location(location_id):
    try:
        if session["admin"] == "True":
            #Checks to see if the primary key of the record has changed, if it has check to see if there is a conflicting name in the database
            #If not update the record else display an error
            if request.form.get("original_location") == request.form.get("location_name"):
                return redirect(url_for("get_locations"))
            else:
                if valid_location():
                    mongo.db.locations.update(
                    {"_id": ObjectId(location_id)},
                    {"location_name": request.form.get("location_name")})
                    mongo.db.place_names.update( {"location": request.form.get("original_location")}, {"$set": { "location": request.form.get("location_name")}}, multi=True)
                    return redirect(url_for("get_locations"))
                else:
                    flash("Location Name '{}' already exists!".format(request.form.get("location_name")))
                    return redirect(url_for("edit_location", location_id=location_id))
    except:
            return redirect(url_for("login_page"))
        
    
@app.route("/delete_location/<location_id>")
def delete_location(location_id):
    try:
        if session["admin"] == "True":
            location=mongo.db.locations.find_one({"_id": ObjectId(location_id)})
            mongo.db.locations.remove({"_id": ObjectId(location_id)})
    
            #delete and place names that have been assigned the location
            mongo.db.place_names.remove({"location": location["location_name"]})
            return redirect(url_for("get_locations"))
    except:
            return redirect(url_for("login_page"))
    
@app.route("/insert_location", methods=["POST"])
def insert_location():
    try:
        if session["admin"] == "True":
            if valid_location():
                location_doc = {"location_name": request.form.get("location_name")}
                mongo.db.locations.insert_one(location_doc)
                return redirect(url_for("get_locations"))
            else:
                flash("Location Name '{}' already exists!".format(request.form.get("location_name")))
                return redirect(url_for("add_location"))
    except:
            return redirect(url_for("login_page"))

@app.route("/add_location")
def add_location():
    try:
        if session["admin"] == "True":
            return render_template("addLocation.html")
    except:
        return redirect(url_for("login_page"))

###########################################View functions for user##################
""" These functions provide the functionality to - view users, add a user, edit a user and delete a user"""
""" They are only accessible with admin privileges. This is checked before any action is taken """

@app.route("/get_users")
def get_users():
    try:
        if session["admin"] == "True":
            return render_template("users.html", users=mongo.db.users.find())  
    except:
            return redirect(url_for("login_page"))

@app.route("/add_user")
def add_user():
    try:
        if session["admin"] == "True":
            return render_template("addUser.html")  
    except:
            return redirect(url_for("login_page"))
    
    
@app.route("/insert_user", methods=["POST"])
def insert_user():
    try:
        if session["admin"] == "True":
            if valid_user():
                user_doc = {"name": request.form.get("name"),"userName": request.form.get("user_name"),"dob": request.form.get("dob"),"admin": "False"}
                mongo.db.users.insert_one(user_doc)
                return redirect(url_for("get_users"))
            else:
                flash("User Name '{}' already exists!".format(request.form.get("user_name")))
                return redirect(url_for("add_user"))
    except:
            return redirect(url_for("login_page"))
                           
@app.route("/edit_user/<user_id>")
def edit_user(user_id):
    try:
        if session["admin"] == "True":
            return render_template("editUser.html", user=mongo.db.users.find_one({"_id": ObjectId(user_id)}))
    except:
        return redirect(url_for("login_page"))

@app.route("/update_user/<user_id>", methods=["POST"])
def update_user(user_id):
    
    try:
        if session["admin"] == "True":
        
            #Checks to see if the primary key of the record has changed, if it has check to see if there is a conflicting name in the database
            #If not update the record else display an error
            if request.form.get("original_user_name") == request.form.get("user_name"):
       
                user_doc = {"name": request.form.get("name"),"userName": request.form.get("user_name"),"dob": request.form.get("dob"),"admin": "False"}
                mongo.db.users.update({"_id": ObjectId(user_id)}, user_doc)
                return redirect(url_for("get_users"))
        
            else:     
       
                if valid_user():
                    user_doc = {"name": request.form.get("name"),"userName": request.form.get("user_name"),"dob": request.form.get("dob"),"admin": "False"}
                    #Change to username on the place names table 
                    mongo.db.place_names.update( {"created_by": request.form.get("original_user_name")}, { "$set": {"created_by": request.form.get("user_name")}}, multi=True)
                    mongo.db.users.update({"_id": ObjectId(user_id)}, user_doc)
                    return redirect(url_for("get_users"))
                else:
                    flash("New User Name '{}' already exists!".format(request.form.get("user_name")))
                    return redirect(url_for("edit_user", user_id=user_id))
    except:
        return redirect(url_for("login_page"))
    
@app.route("/delete_user/<user_id>")
def delete_user(user_id):
    try:
        if session["admin"] == "True":
            user=mongo.db.users.find_one({"_id": ObjectId(user_id)})
            #Remove and place names created by that user
            mongo.db.place_names.remove({"created_by": user["userName"]})
            mongo.db.users.remove({"_id": ObjectId(user_id)})
            return redirect(url_for("get_users"))
    except:
        return redirect(url_for("login_page"))
    


#################################################View functions to login and logout############

@app.route("/login_page")
def login_page():
    #clear the session if returned to the login page
    session.clear()
    return render_template("login.html")
    
@app.route("/login", methods=["POST"])
def login():
   
    session.clear()
    users = mongo.db.users
    user = users.find_one({"userName": request.form["username"]})
    #If the username exists in the database set up the session data otherwise return to the page
    #and display an error
    if user:
        session['username'] = request.form['username']
        name = user["name"].split(" ")[0]
        session['name'] = name
       
        if user["admin"]=="True":
            session['admin'] = user["admin"]
        
        return redirect(url_for("get_place_names"))
    else:
        flash("Username '{}' is invalid.".format(request.form["username"]))
        return render_template("login.html")
        
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('get_place_names'))

###############################################View functions to add likes###############################    
"""Toggles like or dislike and returns to the active place name in the page"""

@app.route("/add_like/<place_name_id>")
def add_like(place_name_id):
    place_name = mongo.db.place_names.find_one({"_id": ObjectId(place_name_id)})
    current_likes = place_name["likes"]
    updated_likes = current_likes + 1
    mongo.db.place_names.update( {"_id": ObjectId(place_name_id)}, { "$set": {"likes": updated_likes}})
    the_active_place_name = place_name["eng_name"]
    the_place_names =  mongo.db.place_names.find()
    return render_template("placeNames.html", place_names=the_place_names, active_place_name=the_active_place_name) 
    
@app.route("/add_dislike/<place_name_id>")
def add_dislike(place_name_id):
    place_name = mongo.db.place_names.find_one({"_id": ObjectId(place_name_id)})
    current_likes = place_name["likes"]
    updated_likes = current_likes - 1
    mongo.db.place_names.update( {"_id": ObjectId(place_name_id)}, { "$set": {"likes": updated_likes}})
    the_active_place_name = place_name["eng_name"]
    the_place_names =  mongo.db.place_names.find()
    return render_template("placeNames.html", place_names=the_place_names, active_place_name=the_active_place_name) 
    
###############################################################################


if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
            port=int(os.environ.get('PORT')))