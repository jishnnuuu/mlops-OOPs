from fastapi import FastAPI, Path, HTTPException, Query
from fastapi.responses import JSONResponse
"""
Path() function in FastAPI is used to provide metadata, validation rules, 
and documentation hints for path parameters in out API endpoints

HTTPException is a special built in exception in FastAPI used to return
custom HTTP error responses when something goes wrong in API.
"""
import json
from pydantic import BaseModel, Field, computed_field
from typing import Annotated, Literal, Optional

app = FastAPI()

class Patient(BaseModel):
    id : Annotated[str, Field(..., description='Id of the Patient', examples=['P002'])]
    name : Annotated[str, Field(..., description='Name of the Patient')]
    city : Annotated[str, Field(..., description='City where Patient belongs to')]
    age : Annotated[int, Field(..., description='Age of the Patient', gt=0, lt=120)]
    gender : Annotated[Literal['male','female','others'], Field(..., description='Gender of the Patient')]
    height : Annotated[float, Field(..., description='height of the Patient in metres', gt=0)]
    weight : Annotated[float, Field(..., description='weight of the Patient in kgs', gt=0)]

    @computed_field
    @property
    def bmi(self) -> float:
        return round((self.weight / self.height**2),2)
    
    @computed_field
    @property
    def verdict(self) -> str:
        if self.bmi < 18.5:
            return 'underweight'
        if self.bmi < 30:
            return 'normal'
        else:
            return 'obese'
        
class Patient_update(BaseModel):
    # id is commented because id is not modified, based on id we update other values
    # id : Annotated[Optional[str], Field(default=None)]
    name : Annotated[Optional[str], Field(default=None)]
    city : Annotated[Optional[str], Field(default=None)]
    age : Annotated[Optional[int],Field(default=None, gt=0)]
    gender : Annotated[Optional[Literal['male','female','others']], Field(default=None)]
    height : Annotated[Optional[float], Field(default=None, gt=0)]
    weight : Annotated[Optional[float], Field(default=None, gt=0)]


def load_data():
    with open('patients.json','r') as f:
        data = json.load(f)
    return data

def save_data(data):
    with open('patients.json', 'w') as f:
        json.dump(data, f)

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
def view_patient(patient_id: str = Path(..., description='ID of the patient in the DB', examples=['P002'])):
    # load all the patients
    data = load_data()
    
    if patient_id in data:
        return data[patient_id]
    return HTTPException(status_code=404, detail='Patient not found')

@app.get('/sort')
def sort_patients(sort_by: str = Query(..., description='sort on basis of height/weight/bmi'),
                    order: str = Query('asc', description='sort in asc/ desc order')):
    valid_fields = ['height', 'weight', 'bmi']
    
    if sort_by not in valid_fields:
        raise HTTPException(status_code=400, detail='Invalid field select from {valid_fields}')
    if order not in ['asc', 'desc']:
        raise HTTPException(status_code=400, detail='Invalid field select from asc/desc')
    
    data = load_data()
    
    sort_order = True if order=='desc' else False
    
    sorted_data = sorted(data.values(), key = lambda x: x.get(sort_by, 0), reverse=sort_order)
    
    return sorted_data

@app.post('/create')
def create_patient(patient : Patient):
    #load your data
    data = load_data()
    
    #check if the same id is present
    if patient.id in data:
        raise HTTPException(status_code=400, detail='Patient already exists')
    
    #add new patient into database
    data[patient.id] = patient.model_dump(exclude='id')
    
    #save the data into json file
    save_data(data)
    
    return JSONResponse(status_code=201, content={'message':'Patient created successfully'})


@app.put('/edit/{patient_id}')
def update_patient(patient_id : str, patient: Patient_update):
    #load data
    data = load_data()
    
    #check if the id is present
    if patient_id not in data:
        raise HTTPException(status_code=404, detail='Patient does not exists')
    
    # retrieving existing data
    existing_data = data[patient_id]
    
    # modifications from user and exclude_unset so not to get default values
    updated_data = patient.model_dump(exclude_unset=True)
    
    # updating the existing model with the updated_data
    for key, value in updated_data.items():
        existing_data[key] = value
    
    # computed fields has to be modified according to changes
    """ 
    existing_data -> pydantic object(Patient model) -> convert into dict -> update in the json
    but before sending into pydantic object we shall add id
    """
    existing_data['id'] = patient_id
    updated_data_computed = Patient(**existing_data)
    
    #removing id for updating into the data
    updated_data_computed_dict = updated_data_computed.model_dump(exclude='id')
    
    #updated the data of that particular patient_id
    data[patient_id] = updated_data_computed_dict
    
    save_data(data)
    return JSONResponse(status_code=200, content='data updated')

@app.delete('/delete/{patient_id}')
def delete_patient(patient_id : str):
    # load data
    data = load_data()
    
    #check if the id is present
    if patient_id not in data:
        raise HTTPException(status_code=404, detail='Patient does not exists')
    
    del data[patient_id]
    
    save_data(data)
    
    return JSONResponse(status_code=200, content='data deleted')