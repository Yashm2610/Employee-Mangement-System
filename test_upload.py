import requests
import pandas as pd

# Create a test CSV
data = {
    'emp_id': ['T-01', 'T-02', ''],
    'emp_name': ['Test One', 'Test Two', 'Test Three'],
    'email': ['test1@example.com', 'invalid-email', 'test3@example.com'],
    'basic_salary': [50000, 60000, 70000]
}
df = pd.DataFrame(data)
df.to_csv('test_import.csv', index=False)

# Send POST request
with open('test_import.csv', 'rb') as f:
    r = requests.post('http://127.0.0.1:5000/upload', files={'csv_file': ('test_import.csv', f, 'text/csv')})
    
print("Status Code:", r.status_code)
print("Response JSON:", r.json())
