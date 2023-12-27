from apiResponse import APIResponse
from base64Image import Base64Image
from fastapi import FastAPI
#uvicorn main:app --reload
#windows:.\venv\Scripts\Activate
#Linux: source venv/bin/activate
import extract_info_from_passport
app = FastAPI()
#To increase max payload size, use: uvicorn myapp:app --limit-max-request-body 209715200


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/getPassportInfo")
async def getPassportInfo(base64Image:Base64Image):
    apiResponse = extract_info_from_passport.get_data(base64Image.base64Image)
    return apiResponse