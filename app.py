import os
from flask import Flask,render_template,request,jsonify
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from flask_uploads import UploadSet, configure_uploads, ALL
from bson.objectid import ObjectId
from datetime import datetime

# from flask_sqlalchemy import SQLAlchemy
# from flask import Flask, session, render_template, url_for, redirect, flash, request
# from wtforms import Form, fields,TextField, StringField, PasswordField, BooleanField,validators
# from wtforms.validators import InputRequired, Email, Length, DataRequired
# from flask_wtf import FlaskForm
# from flask_uploads import UploadSet, configure_uploads, IMAGES
# from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app=Flask(__name__)

app.config["MONGO_URI"] = "mongodb+srv://jkhyat25:RGrV9qHfheXVDf1d@cluster0.b7fa9cx.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

app.config['UPLOADED_FILES_DEST'] = 'uploads'
files = UploadSet('files', ALL)
configure_uploads(app, files)

# Initialize PyMongo
mongo = PyMongo(app)

if mongo is None:
    raise Exception("Failed to connect to the database")

# Define the collection
db=mongo.db.experiments

@app.route("/")
def first_function():
    return render_template('home.html')
    
@app.route("/datasub")
def datasub():
    return render_template('datasub.html')

# Endpoint to handle form submission
@app.route('/submit_data', methods=['POST'])
def submit_data():
    data = request.form
    required_fields = ['experiment_name', 'primary_researcher', 'PI_manager', 'starting_date', 'purpose']

    # Check for required fields
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"'{field}' is required"}), 400

    # Check if file is included
    if 'file' not in request.files:
        return jsonify({"error": "'file' is required"}), 400

    # Save the file
    file = request.files['file']
    if file and file.filename.endswith('.fcs'):
        file_path = files.save(file)
    else:
        return jsonify({"error": "Invalid file format. Only .fcs files are allowed"}), 400

    # Insert into MongoDB
    experiment_id = db.experiments.insert_one({
        'experiment_name': data['experiment_name'],
        'primary_researcher': data['primary_researcher'],
        'PI_manager': data['PI_manager'],
        'starting_date': data['starting_date'],
        'purpose': data['purpose'],
        'file_path': file_path,
        'end_date': data.get('end_date'),
        'comments': data.get('comments'),
        'keyword': data.get('keyword'),
        'organization': data.get('organization'),
        'created_at': datetime.utcnow()
    }).inserted_id

    return jsonify({"msg": "Experiment added", "id": str(experiment_id)}), 201

if __name__== "__main__":
  app.run(host='0.0.0.0',debug=True)
  