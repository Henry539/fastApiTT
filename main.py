import database

import uvicorn
from database import engine, get_db
from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session
from typing import Optional
import uuid

database.Base.metadata.create_all(bind=engine)

app = FastAPI()


def get_all_folder(db: Session):
    return db.query(database.Folder).all()

def get_all_token(db: Session):
    return db.query(database.Token).all()


def create_Folder(db: Session, folder_id: str, user_id: str):
    db_Data = database.Folder(folder_id=folder_id, user_id=user_id)
    db.add(db_Data)
    db.commit()
    db.refresh(db_Data)
    return db_Data

def create_Token(db: Session, r_clone_token: str,client_id: str,client_secret: str):
    db_Data = database.Token(r_clone_token=r_clone_token,client_id=client_id,client_secret=client_secret)
    db.add(db_Data)
    db.commit()
    db.refresh(db_Data)
    return db_Data

def check_data_exist_folder(db: Session , folder_id: str):
    data1 = db.query(database.Folder).filter(database.Folder.folder_id == folder_id).first()
    return data1

def check_data_exist_token(db: Session , r_clone_token: str):
    data1 = db.query(database.Token).filter(database.Token.r_clone_token == r_clone_token).first()
    return data1

def check_data_unused_folder(db: Session):
    data = db.query(database.Folder).filter(database.Folder.token_id == None).all()
    return data

def check_data_unused_token(db: Session):
    data = db.query(database.Token).filter(database.Token.folder_id == None).all()
    return data

def add_folder_token(db: Session,folder_id: str,r_clone_token: str):
    folder = db.query(database.Folder).filter(database.Folder.folder_id == folder_id).first()
    token = db.query(database.Token).filter(database.Token.r_clone_token == r_clone_token).first()
    folder.token_id = r_clone_token
    token.folder_id = folder_id
    db.add(folder)
    db.add(token)
    db.commit()
    db.refresh(token)
    db.refresh(folder)
    return {folder}




@app.get("/folders")
def read_folders(db: Session = Depends(get_db)):
    db_Data = get_all_folder(db=db)
    return db_Data

@app.get("/tokens")
def read_tokens(db: Session = Depends(get_db)):
    db_Data = get_all_token(db=db)
    return db_Data

@app.post("/create-folder")
def create_folder(folder_id: str, user_id: str, db: Session = Depends(get_db)):
    check_exist_folder = check_data_exist_folder(db=db, folder_id=folder_id)
    if check_exist_folder != None:
        return {f"Error: string_data {folder_id} is exist!"}
    data_Data = create_Folder(db=db, folder_id=folder_id,user_id=user_id)
    return data_Data

@app.post("/create-token")
def create_token(r_clone_token: str,client_id: Optional[str]=None,client_secret: Optional[str]=None, db: Session = Depends(get_db)):
    check_exist_folder = check_data_exist_token(db=db, r_clone_token=r_clone_token)
    if check_exist_folder != None:
        return {f"Error: string_data {r_clone_token} is exist!"}
    data_Data = create_Token(db=db, r_clone_token=r_clone_token,client_id=client_id,client_secret=client_secret)
    return data_Data

@app.get("/unused-folder")
def read_unused_folder(db: Session = Depends(get_db)):
    db_Data = check_data_unused_folder(db=db)
    return db_Data

@app.get("/unused-token")
def read_unused_token(db: Session = Depends(get_db)):
    db_Data = check_data_unused_token(db=db)
    return db_Data

@app.get("/get-unused-folder-token")
def read_unused_token(db: Session = Depends(get_db)):
    list_unused_folder_token = {}
    list_token = []
    list_folder = []
    db_token = check_data_unused_token(db=db)
    db_folder = check_data_unused_folder(db=db)
    for token in db_token:
        list_token.append(token.r_clone_token)
    for folder in db_folder:
        list_folder.append(folder.folder_id)
    list_unused_folder_token['folder'] = list_folder
    list_unused_folder_token['token'] = list_token
    return list_unused_folder_token

@app.put("/add-folder-token")
def map_folder_token(r_clone_token: str, folder_id: str,db: Session = Depends(get_db)):
    add_f_t = add_folder_token(db=db,folder_id=folder_id,r_clone_token=r_clone_token)
    return add_f_t

@app.get("/register")
def get_user_id():
    return {"user_id": str(uuid.uuid4())}

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.0", port=8002, reload=True)
