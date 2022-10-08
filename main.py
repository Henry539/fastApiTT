import database

import uvicorn
from database import engine, get_db
from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session
from typing import Optional
import uuid

database.Base.metadata.create_all(bind=engine)

app = FastAPI()


# <------------- Function mapping Object-Database ------------->

# <----- Get all folders Function ----->
def get_all_folder(db: Session):
    return db.query(database.Folder).all()


# <----- Get all tokens Function ----->
def get_all_token(db: Session):
    return db.query(database.Token).all()


# <----- Create new folder Function ----->
def create_new_folder(db: Session, folder_id: str, user_id: str):
    data_result = database.Folder(folder_id=folder_id, user_id=user_id)
    db.add(data_result)
    db.commit()
    db.refresh(data_result)
    return data_result


# <----- Create new token Function ----->
def create_new_token(db: Session, r_clone_token: str, client_id: str, client_secret: str):
    data_result = database.Token(r_clone_token=r_clone_token, client_id=client_id, client_secret=client_secret)
    db.add(data_result)
    db.commit()
    db.refresh(data_result)
    return data_result


# <----- Get exist folder Function ----->
def check_data_folder_exist(db: Session, folder_id: str):
    data1 = db.query(database.Folder).filter(database.Folder.folder_id == folder_id).first()
    return data1


# <----- Get exist token  Function ----->
def check_data_token_exist(db: Session, r_clone_token: str):
    data1 = db.query(database.Token).filter(database.Token.r_clone_token == r_clone_token).first()
    return data1


# <----- Get all unused folder Function ----->
def check_data_unused_folder(db: Session):
    data = db.query(database.Folder).filter(database.Folder.token_id == None).all()
    return data


# <----- Get all unused token Function ----->
def check_data_unused_token(db: Session):
    data = db.query(database.Token).filter(database.Token.folder_id == None).all()
    return data


# <----- Mapping 1 folder - 1 token Function ----->
def add_folder_token(db: Session, folder_id: str, r_clone_token: str):
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


# <----- Check mapping folder Function ----->
def check_mapping_folder_exist(db: Session, folder_id: str):
    data1 = db.query(database.Folder).filter(database.Folder.folder_id == folder_id).first()
    return data1.token_id


# <----- Check mapping folder Function ----->
def check_mapping_token_exist(db: Session, r_clone_token: str):
    data1 = db.query(database.Token).filter(database.Token.r_clone_token == r_clone_token).first()
    return data1.folder_id


# <----- Get all used folder-token Function ----->
def get_all_mapping_token_folder(db: Session):
    list_all_mapping = []
    data_folder_result = db.query(database.Folder).filter(database.Folder.token_id != None).all()
    for folder in data_folder_result:
        list_once_mapping = []
        data_token_result = db.query(database.Token).filter(database.Token.r_clone_token == folder.token_id).first()
        list_once_mapping.append(folder)
        list_once_mapping.append(data_token_result)
        list_all_mapping.append(list_once_mapping)
    return list_all_mapping


# <------------- API service ------------->

# <----- List all folders ----->
@app.get("/folders")
def read_folders(db: Session = Depends(get_db)):
    data_result = get_all_folder(db=db)
    return data_result


# <----- List all tokens ----->
@app.get("/tokens")
def read_tokens(db: Session = Depends(get_db)):
    data_result = get_all_token(db=db)
    return data_result


# <----- Create new folder ----->
@app.post("/create-folder")
def create_folder(folder_id: str, user_id: str, db: Session = Depends(get_db)):
    check_exist_folder = check_data_folder_exist(db=db, folder_id=folder_id)
    if check_exist_folder is not None:
        return {f"Error: string_data {folder_id} is exist!"}
    data_result = create_new_folder(db=db, folder_id=folder_id, user_id=user_id)
    return data_result


# <----- Create new token ----->
@app.post("/create-token")
def create_token(r_clone_token: str, client_id: Optional[str] = None, client_secret: Optional[str] = None,
                 db: Session = Depends(get_db)):
    check_exist_folder = check_data_token_exist(db=db, r_clone_token=r_clone_token)
    if check_exist_folder is not None:
        return {f"Error: string_data {r_clone_token} is exist!"}
    data_result = create_new_token(db=db, r_clone_token=r_clone_token, client_id=client_id, client_secret=client_secret)
    return data_result


# <----- List all unused folders ----->
@app.get("/unused-folder")
def read_unused_folder(db: Session = Depends(get_db)):
    data_result = check_data_unused_folder(db=db)
    return data_result


# <----- List all unused tokens ----->
@app.get("/unused-token")
def read_unused_token(db: Session = Depends(get_db)):
    data_result = check_data_unused_token(db=db)
    return data_result


# <----- Check unused folder-tokens ----->
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


# <----- Add unused folders-tokens ----->
@app.put("/add-folder-token")
def map_folder_token(folder_id: str, r_clone_token: str, db: Session = Depends(get_db)):
    if check_mapping_folder_exist(db=db, folder_id=folder_id) is not None:
        return {f'Error: Folder {folder_id} is mapping!'}
    if check_mapping_token_exist(db=db, r_clone_token=r_clone_token) is not None:
        return {f'Error: Token {r_clone_token} is mapping!'}
    add_f_t = add_folder_token(db=db, folder_id=folder_id, r_clone_token=r_clone_token)
    return add_f_t


# <----- Get new Register/user_id ----->
@app.get("/register")
def get_user_id():
    return {"user_id": str(uuid.uuid4())}


# <----- Get all Mapping folder-token ----->
@app.get("/all-mapping")
def get_all_mapping_folder_token(db: Session = Depends(get_db)):
    return get_all_mapping_token_folder(db=db)


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.0", port=8002, reload=True)
