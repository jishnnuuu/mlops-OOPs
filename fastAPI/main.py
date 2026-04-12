from fastapi import FastAPI, Path, HTTPException
"""
Path() function in FastAPI is used to provide metadata, validation rules, 
and documentation hints for path parameters in out API endpoints

HTTPException is a special built in exception in FastAPI used to return
custom HTTP error responses when something goes wrong in API.
"""
import json

app = FastAPI()

def load_data():
    with open('patients.json','r') as f:
        data = json.load(f)
    return data

@app.get('/')
def hello():
    return {
        'message' : 'Patient Management System API'
    }

@app.get('/about')
def about():
    return {
        'message' : 'A fully functional API to manage your patient records'
    }

@app.get('/view')
def view():
    data = load_data()
    return data

#path params(dynamic)
@app.get('/patient/{patient_id}')
def view_patient(patient_id: str = Path(..., description='ID of the patient in the DB', example='P002')):
    # load all the patients
    data = load_data()
    
    if patient_id in data:
        return data[patient_id]
    return HTTPException(status_code=404, detail='Patient not found')