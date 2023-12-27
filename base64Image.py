from pydantic import BaseModel
class Base64Image(BaseModel):
    base64Image: str