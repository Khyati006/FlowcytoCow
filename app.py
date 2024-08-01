import os
from flask import Flask, render_template, request, jsonify,flash,redirect, url_for,get_flashed_messages
from bson.objectid import ObjectId
from flask_uploads import UploadSet, configure_uploads, ALL
from datetime import datetime
from flask_pymongo import PyMongo
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

app = Flask(__name__)

app.secret_key = '731cb1ec216c770a52d6b2b2bf733e2d' 

# Configuration for MongoDB Atlas

uri = "mongodb+srv://jkhyat25:1BUtbyJ1ekzEoGss@cluster1.nonxkwd.mongodb.net/?retryWrites=true&w=majority&appName=Cluster1"

# Initialize the MongoDB client
client = MongoClient(uri, server_api=ServerApi('1'))

db = client['mydatabase']
collection = db['mycollection']


# Configuration for file uploads
app.config['UPLOADED_FILES_DEST'] = 'uploads'
files = UploadSet('files', ALL)
configure_uploads(app, files)


@app.route("/")
def first_function():
    return render_template('home.html')

@app.route("/datasub")
def datasub():
    messages = get_flashed_messages(with_categories=True)
    return render_template('datasub.html', messages=messages)


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
    experiment_id = collection.insert_one({
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


    flash("Experiment added successfully.", 'success')
    return redirect(url_for('result', message="Experiment added successfully.", category='success'))

@app.route('/result')
def result():
    message = request.args.get('message')
    category = request.args.get('category')
    return render_template('sub_result.html', message=message, category=category)


@app.route('/check')
def home():
    try:
        # Test the connection by sending a ping command
        client.admin.command('ping')
        return jsonify(message="Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        return jsonify(message=f"An error occurred: {str(e)}"), 500


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
