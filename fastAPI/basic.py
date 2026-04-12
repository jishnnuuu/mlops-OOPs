from fastapi import FastAPI

# app is object of fast-api
app = FastAPI()

@app.get("/")
def hello():
    return {
        'message' : 'Hello world'
    }

@app.get('/about')
def about():
    return {
        'message' : 'I am student of MTech IIITB'
    }