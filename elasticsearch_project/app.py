from flask import Flask, render_template, request, jsonify
from elasticsearch import Elasticsearch
from functions import *  # Assuming functions.py contains your function definitions

app = Flask(__name__)

v_nameCollection = "hash_yourname"
v_phoneCollection = "phone_collection"  # Change this to a suitable name

# Initialize Elasticsearch
es = Elasticsearch([{'scheme': 'http', 'host': 'localhost', 'port': 9200}])

def createCollection(p_collection_name):
    if not es.indices.exists(index=p_collection_name):
        es.indices.create(index=p_collection_name)
        print(f"Index '{p_collection_name}' created.")
    else:
        print(f"Index '{p_collection_name}' already exists.")

@app.route('/')
def index():
    v_nameCollection = "hash_yourname"  # Define the name for your index
    v_phoneCollection = "phone_collection"  # Define the phone collection name
    createCollection(v_nameCollection)
    createCollection(v_phoneCollection)
    indexData(v_nameCollection, 'Department')  # Index your data
    indexData(v_phoneCollection, 'Gender')      # Index your data
    return render_template('index.html')



@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        column_name = request.form.get('column_name')
        column_value = request.form.get('column_value')
        results = searchByColumn(v_nameCollection, column_name, column_value)
        return render_template('search.html', results=results)
    return render_template('search.html', results=None)

@app.route('/get_department_data')
def get_department_data():
    global v_nameCollection
    department_data = getDepFacet(v_nameCollection)
    return jsonify(department_data)

if __name__ == '__main__':
    app.run(debug=True)
