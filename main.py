from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
from pydantic import BaseModel
from bson.objectid import ObjectId
from datetime import datetime
import bcrypt

# เชื่อมต่อกับ MongoDB
client = MongoClient("mongodb://localhost:27017")
db = client["ChatBot"]
register_collection = db["register"]
history_collection = db["history"]
section_collection = db["section"]

# สร้างคลาส
class Regis(BaseModel):
    username: str
    password: str
    email: str
    theme: str  = 'default'


class Login(BaseModel):
    username: str
    password: str


    
class History(BaseModel):
    question: str
    answer: str

class Upname(BaseModel):
    name : str


app = FastAPI()




############ Register #####################################
@app.post("/register")
async def register(re: Regis):
   
    if register_collection.find_one({"username": re.username, "email": re.email}):
        raise HTTPException(status_code=400, detail="ข้อมูลนี้มีอยู่แล้ว")

    hash_pw = bcrypt.hashpw(re.password.encode("utf-8"), bcrypt.gensalt())
    user_data = {
        "username": re.username,
        "password": hash_pw.decode("utf-8"),
        "email": re.email,
        "theme": re.theme
    }
  
    result = register_collection.insert_one(user_data)
    return {
        "id": str(result.inserted_id),
        "username": re.username,
        "email": re.email,
        "theme": re.theme
    }


### LOGIN #####


@app.post("/login")
async def user_login(login: Login):
    user = register_collection.find_one({"username": login.username})
    if not user:
        raise HTTPException(status_code=400, detail="ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง")

    if not bcrypt.checkpw(
        login.password.encode("utf-8"), user["password"].encode("utf-8")
    ):
        raise HTTPException(status_code=400, detail="ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง")

    return {
        "message": "เข้าสู่ระบบสำเร็จ",
        "id": str(user.get("_id")),
        "username": login.username,
        "email": user["email"],
    }


####### section ###################   
@app.post('/section/{user_id}')
async def cr_section(user_id:str):
    dt = datetime.now()
    

    section_data = {
        "user_id": user_id,
        "name": dt
        
    }
    result = section_collection.insert_one(section_data)
    return {
        "id": str(result.inserted_id), 
        "user_id": user_id,
        "name": dt
        
    }


######## History #####

@app.post('/history/{section_id}')
async def cr_history(section_id: str, hs: History):
    
    history_data = {
        "section_id": section_id,  
        "question": hs.question,
        "answer": hs.answer
    }

    result = history_collection.insert_one(history_data)
    return {
        "id": str(result.inserted_id),  
        "section_id": section_id,
        "question": hs.question,
        "answer": hs.answer
    }





########################
@app.get('/section/{user_id}')
async def view_section(user_id: str):
    users = section_collection.find({"user_id": user_id})  # Find all documents with the specified user_id
    user_list = []
    
    for user in users:
        user_list.append({
            "id": str(user["_id"]),
            "user_id": user["user_id"],
            "name": user["name"]
        })
    
    return user_list

###############################
@app.get('/history/{section_id}')
async def read_history(section_id: str):
    readme = history_collection.find({"section_id":section_id})
    read_all = []
    for read in readme:
        read_all.append({
            "id": str(read["_id"]),  
            "section_id": read["section_id"],
            "question": read["question"],
            "answer": read["answer"]
        })
    return read_all

######### update name ใช้id ของ section ######
@app.put('/section/{section_id}')
async def up_section(section_id:str,upname:Upname):
    result = section_collection.update_one(
        {"_id": ObjectId(section_id)},
        {"$set":{"name":upname.name}}
    )
    return{
        "name":upname.name
    }

######### delete ใช้id ของ section ######
@app.delete('/section/{section_id}')
async def delete_all(section_id:str):
    del_hs = history_collection.delete_many({"section_id":section_id})
    del_sec = section_collection.delete_one({"_id":ObjectId(section_id)})
    return{
        "msg":"ลบสำเร็จ"
    }