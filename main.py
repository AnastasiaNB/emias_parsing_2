from fastapi import FastAPI

app = FastAPI()

@app.get('/specialities')
def get_available_specialists(context):
    pass