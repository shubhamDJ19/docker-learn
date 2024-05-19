from typing import Union
from pydantic import BaseModel

from fastapi import FastAPI
from app.ragHaystack import ProcessQuery

app = FastAPI()


class MessageUser(BaseModel):
    input: str


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


@app.post("/query")
def update_item(message: MessageUser):
    output = ProcessQuery(message.input)
    return output
