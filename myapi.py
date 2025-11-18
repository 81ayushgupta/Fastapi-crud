from fastapi import FastAPI, HTTPException
from fastapi.security import OAuth2PasswordBearer, Oauth2PasswordRequestForm
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from fastapi import Depends
from pydantic import BaseModel
from typing import Optional, List
from passlib.context import CryptContext
import jwt

app = FastAPI(title = "Integration with SQL  - First App")


#Database Setup
engine  = create_engine("sqlite:///users.db",connect_args = {"check_same_thread" : False})
#prevent reloading 
SessionLocal = sessionmaker(autocommit = False, autoflush = False, bind = engine)
Base = declarative_base()

#Database Model
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key = True, index = True)
    name = Column(String, nullable = False)
    email = Column(String, nullable= False, unique = True)
    role = Column(String, nullable= False)
    
Base.metadata.create_all(engine)

#pydantic Models (Dataclass)
class UserCreate(BaseModel):
    name: str
    email: str
    role: str
    
class UserResponse(BaseModel):
    id:int
    name:str
    email:str
    role:str
    
    class Config:
        from_attributes = True
        
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
get_db()
    

# Endpoints (www.firstproject)
@app.get("/")

def root():
    return {"message" : "Into to FastAPI"}

@app.get("/users/{user_id}", response_model = UserResponse)
def get_user(user_id:int, db:Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code = 404, detail = "User not Found")
    return user

@app.post("/users", response_model = UserResponse)
def create_user(user : UserCreate, db:Session = Depends(get_db)):
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code = 404, detail = "User Already Exists!")

    #create a new user
    new_user = User(**user.dict())
    db.add(new_user)
    #commit the changes
    db.commit()
    db.refresh(new_user)
    return new_user
    
    
# update user
@app.put("/user/{user_id}",response_model = UserResponse)
def update_user(user_id : int, user: UserCreate, db:Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code = 404, detail = "User does not Exists!")
    
    for field, value in user.dict().items():
        setattr(db_user, field, value)
        
    db.commit()
    db.refresh(db_user)
    return db_user

# delete user
@app.delete("/users/{user_id}")
def delete_user(user_id : int, db:Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code = 404, detail = "User does not Exists!")
    
    db.delete(db_user)
    db.commit()
    return {"message" : "User Deleted!"}

@app.get("/users/", response_model = List[UserResponse])
def get_all_users(db:Session = Depends(get_db)):
    return db.query(User).all()