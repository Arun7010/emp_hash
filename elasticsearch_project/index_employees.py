from elasticsearch import Elasticsearch
import pandas as pd
from datetime import datetime

# Connect to Elasticsearch
es = Elasticsearch([{'host': 'localhost', 'port': 9200, 'scheme': 'http'}])

# Create an index
index_name = 'employees'
es.indices.create(index=index_name, ignore=400)  # Ignore error if index already exists

# Load the dataset with a specified encoding
try:
    employee_data = pd.read_csv('employee_sample_data.csv', encoding='ISO-8859-1')
except UnicodeDecodeError as e:
    print(f"Error reading the CSV file: {e}")

# Function to clean up the salary field
def clean_salary(salary):
    try:
        return float(salary.replace('$', '').replace(',', '').strip())
    except ValueError:
        print(f"Invalid salary format: {salary}")
        return None  # Return None if salary can't be converted

# Function to clean up the hire date field
def clean_hire_date(date_str):
    try:
        return pd.to_datetime(date_str).isoformat()  # Convert to ISO format
    except Exception as e:
        print(f"Invalid date format: {date_str}, Error: {e}")
        return None  # Return None if date can't be converted

# Index data into Elasticsearch
for index, row in employee_data.iterrows():
    try:
        doc = {
            'employee_id': row['Employee ID'],
            'full_name': row['Full Name'],
            'job_title': row['Job Title'],
            'department': row['Department'],
            'business_unit': row['Business Unit'],
            'gender': row['Gender'],
            'ethnicity': row['Ethnicity'],
            'age': row['Age'],
            'hire_date': clean_hire_date(row['Hire Date']),
            'annual_salary': clean_salary(row['Annual Salary']),
            'bonus_percentage': row['Bonus %'],
            'country': row['Country'],
            'city': row['City']
        }
        # Check for None values and skip indexing if any required field is missing
        if None not in [doc['employee_id'], doc['full_name'], doc['hire_date'], doc['annual_salary']]:
            es.index(index=index_name, id=row['Employee ID'], document=doc)
        else:
            print(f"Skipping row {index} due to missing required fields: {doc}")
    except Exception as e:
        print(f"Error indexing row {index}: {e}")
        print(f"Row data: {row}")  # Print the problematic row for debugging

print("Employee data indexed successfully.")
