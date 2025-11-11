from AI_functions import chatgpt, dalle
from sqlalchemy_db import SessionLocal, engine, User
from schema import UserSchema, UserResponseSchema
from fastapi import FastAPI, Depends, HTTPException
from typing import List
import requests
from sqlalchemy.orm import Session
import uvicorn

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
async def home():
    return {"Message": "Welcome to my API"}

@app.post("/generate_image")
async def generate_images(data: UserSchema, db: Session = Depends(get_db)):

    image_url = dalle(data.description)
    user = User(description = data.description, image_url = image_url)

    db.add(user)
    db.commit()
    db.refresh(user)

    return user

@app.get("/images", response_model = List[UserResponseSchema])
async def get_images(db: Session = Depends(get_db)):
    images = db.query(User).all()
    return images

@app.delete("/delete_image")
async def delete_images(data: UserSchema, db: Session = Depends(get_db)):

    user = db.query(User).filter(User.description == data.description).first()

    if not user:
        raise HTTPException(status_code = 404, detail = "Image not found")

    db.delete(user)
    db.commit()

    return user

@app.delete("/truncate")
async def truncate_table(db: Session = Depends(get_db)):

    images = db.query(User).delete()
    
    db.commit()

    return {"message":"Images deleted succeessfully!"}

@app.put("/update_image")
async def update_images(data: UserSchema, db: Session = Depends(get_db)):

    image = db.query(User).filter(User.id == data.id).first()

    if not image:
        raise HTTPException(status_code = "404", detail = "Image not found")

    image_url = dalle(data.description)
    new_image = User(description = data.description, image_url = image_url)

    image.description = new_image.description
    image.image_url = image_url

    db.commit()
    db.refresh(image)

    return image

@app.post("/smart_choice")
async def smart_choice(data: UserSchema, db: Session = Depends(get_db)):
    
    refined_prompt = chatgpt(data.description)
    if refined_prompt:
        url = dalle(refined_prompt)

    image = User(description = refined_prompt, image_url = url)

    db.add(image)
    db.commit()
    db.refresh(image)

    return image



if __name__ == "__main__":

    uvicorn.run(app, host = "127.0.0.1", port = 8001)
