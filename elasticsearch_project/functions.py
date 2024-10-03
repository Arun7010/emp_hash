from elasticsearch import Elasticsearch
import pandas as pd
import chardet

def indexData(collection_name, some_parameter):
    # Detect the file encoding
    with open('employee_sample_data.csv', 'rb') as f:
        result = chardet.detect(f.read())
        encoding = result['encoding']
        print(f"Detected encoding: {encoding}")

    # Read the CSV file with the detected encoding
    employee_data = pd.read_csv('employee_sample_data.csv', encoding=encoding)

# Connect to Elasticsearch
es = Elasticsearch([{'scheme': 'http', 'host': 'localhost', 'port': 9200}])

def createCollection(p_collection_name):
    # Create an index (collection) in Elasticsearch
    es.indices.create(index=p_collection_name, ignore=400)  # Ignore error if index already exists

def indexData(p_collection_name, p_exclude_column):
    # Load employee data
    employee_data = pd.read_csv('employee_sample_data.csv')
    
    # Exclude specified column
    if p_exclude_column in employee_data.columns:
        employee_data = employee_data.drop(columns=[p_exclude_column])
    
    # Index data into Elasticsearch
    for _, row in employee_data.iterrows():
        doc = row.to_dict()
        es.index(index=p_collection_name, id=row['Employee ID'], document=doc)

def searchByColumn(p_collection_name, p_column_name, p_column_value):
    # Search for records where column matches the value
    query = {
        "query": {
            "match": {
                p_column_name: p_column_value
            }
        }
    }
    res = es.search(index=p_collection_name, body=query)
    return [hit['_source'] for hit in res['hits']['hits']]

def getEmpCount(p_collection_name):
    # Get the total count of employees in the specified collection
    res = es.count(index=p_collection_name)
    return res['count']

def delEmpById(p_collection_name, p_employee_id):
    # Delete an employee by ID
    es.delete(index=p_collection_name, id=p_employee_id, ignore=[404])

def getDepFacet(p_collection_name):
    # Retrieve count of employees grouped by department
    aggs = {
        "department_count": {
            "terms": {
                "field": "Department.keyword"
            }
        }
    }
    res = es.search(index=p_collection_name, body={"size": 0, "aggs": aggs})
    return res['aggregations']['department_count']['buckets']

# Function Execution
if __name__ == '__main__':
    v_nameCollection = 'Hash_<Your Name>'  # Replace <Your Name> with your actual name
    v_phoneCollection = 'Hash_<Your Phone last four digits>'  # Replace with your phone's last four digits

    # Execute functions in the specified order
    createCollection(v_nameCollection)
    createCollection(v_phoneCollection)
    emp_count_before = getEmpCount(v_nameCollection)
    print(f'Employee count in {v_nameCollection}: {emp_count_before}')

    indexData(v_nameCollection, 'Department')
    indexData(v_phoneCollection, 'Gender')

    delEmpById(v_nameCollection, 'E02003')
    emp_count_after = getEmpCount(v_nameCollection)
    print(f'Employee count in {v_nameCollection} after deletion: {emp_count_after}')

    it_employees = searchByColumn(v_nameCollection, 'Department', 'IT')
    print(f'Employees in IT: {it_employees}')

    male_employees = searchByColumn(v_nameCollection, 'Gender', 'Male')
    print(f'Male employees: {male_employees}')

    it_employees_phone = searchByColumn(v_phoneCollection, 'Department', 'IT')
    print(f'Employees in IT from phone collection: {it_employees_phone}')

    department_facet = getDepFacet(v_nameCollection)
    print(f'Department facet for {v_nameCollection}: {department_facet}')

    department_facet_phone = getDepFacet(v_phoneCollection)
    print(f'Department facet for {v_phoneCollection}: {department_facet_phone}')
