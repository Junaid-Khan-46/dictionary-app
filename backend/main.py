from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
import os
from dotenv import load_dotenv
from bson import ObjectId
import asyncio

load_dotenv()

app = FastAPI(title="Full-Stack Template API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-this")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "fullstack_template")

# MongoDB client
client = AsyncIOMotorClient(MONGODB_URL)
database = client[DATABASE_NAME]
users_collection = database.users
posts_collection = database.posts

# Pydantic models
class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class User(BaseModel):
    id: str = Field(alias="_id")
    username: str
    email: str
    created_at: datetime

    class Config:
        populate_by_name = True

class Token(BaseModel):
    access_token: str
    token_type: str

class PostCreate(BaseModel):
    title: str
    content: str
    category: Optional[str] = "general"

class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    category: Optional[str] = None

class Post(BaseModel):
    id: str = Field(alias="_id")
    title: str
    content: str
    category: str
    author_id: str
    author_username: str
    created_at: datetime
    updated_at: datetime

    class Config:
        populate_by_name = True

# Helper functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = await users_collection.find_one({"username": username})
    if user is None:
        raise credentials_exception
    return user

# Routes
@app.get("/")
async def root():
    return {"message": "Full-Stack Template API", "version": "1.0.0"}

@app.post("/auth/signup", response_model=Token)
async def signup(user: UserCreate):
    # Check if user already exists
    existing_user = await users_collection.find_one({"$or": [{"username": user.username}, {"email": user.email}]})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user.password)
    user_doc = {
        "username": user.username,
        "email": user.email,
        "password": hashed_password,
        "created_at": datetime.utcnow()
    }
    
    result = await users_collection.insert_one(user_doc)
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/auth/login", response_model=Token)
async def login(user: UserLogin):
    # Authenticate user
    db_user = await users_collection.find_one({"username": user.username})
    if not db_user or not verify_password(user.password, db_user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/auth/me", response_model=User)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    return User(
        _id=str(current_user["_id"]),
        username=current_user["username"],
        email=current_user["email"],
        created_at=current_user["created_at"]
    )

@app.get("/posts", response_model=List[Post])
async def get_posts(skip: int = 0, limit: int = 10):
    cursor = posts_collection.find().sort("created_at", -1).skip(skip).limit(limit)
    posts = []
    async for post in cursor:
        posts.append(Post(
            _id=str(post["_id"]),
            title=post["title"],
            content=post["content"],
            category=post["category"],
            author_id=str(post["author_id"]),
            author_username=post["author_username"],
            created_at=post["created_at"],
            updated_at=post["updated_at"]
        ))
    return posts

@app.post("/posts", response_model=Post)
async def create_post(post: PostCreate, current_user: dict = Depends(get_current_user)):
    post_doc = {
        "title": post.title,
        "content": post.content,
        "category": post.category,
        "author_id": current_user["_id"],
        "author_username": current_user["username"],
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    result = await posts_collection.insert_one(post_doc)
    post_doc["_id"] = result.inserted_id
    
    return Post(
        _id=str(post_doc["_id"]),
        title=post_doc["title"],
        content=post_doc["content"],
        category=post_doc["category"],
        author_id=str(post_doc["author_id"]),
        author_username=post_doc["author_username"],
        created_at=post_doc["created_at"],
        updated_at=post_doc["updated_at"]
    )

@app.get("/posts/{post_id}", response_model=Post)
async def get_post(post_id: str):
    try:
        post = await posts_collection.find_one({"_id": ObjectId(post_id)})
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        
        return Post(
            _id=str(post["_id"]),
            title=post["title"],
            content=post["content"],
            category=post["category"],
            author_id=str(post["author_id"]),
            author_username=post["author_username"],
            created_at=post["created_at"],
            updated_at=post["updated_at"]
        )
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid post ID")

@app.put("/posts/{post_id}", response_model=Post)
async def update_post(post_id: str, post_update: PostUpdate, current_user: dict = Depends(get_current_user)):
    try:
        # Check if post exists and user is the author
        post = await posts_collection.find_one({"_id": ObjectId(post_id)})
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        
        if post["author_id"] != current_user["_id"]:
            raise HTTPException(status_code=403, detail="Not authorized to update this post")
        
        # Update post
        update_data = {k: v for k, v in post_update.dict().items() if v is not None}
        update_data["updated_at"] = datetime.utcnow()
        
        await posts_collection.update_one(
            {"_id": ObjectId(post_id)},
            {"$set": update_data}
        )
        
        # Get updated post
        updated_post = await posts_collection.find_one({"_id": ObjectId(post_id)})
        
        return Post(
            _id=str(updated_post["_id"]),
            title=updated_post["title"],
            content=updated_post["content"],
            category=updated_post["category"],
            author_id=str(updated_post["author_id"]),
            author_username=updated_post["author_username"],
            created_at=updated_post["created_at"],
            updated_at=updated_post["updated_at"]
        )
    except Exception as e:
        if "Invalid post ID" in str(e):
            raise HTTPException(status_code=400, detail="Invalid post ID")
        raise e

@app.delete("/posts/{post_id}")
async def delete_post(post_id: str, current_user: dict = Depends(get_current_user)):
    try:
        # Check if post exists and user is the author
        post = await posts_collection.find_one({"_id": ObjectId(post_id)})
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        
        if post["author_id"] != current_user["_id"]:
            raise HTTPException(status_code=403, detail="Not authorized to delete this post")
        
        # Delete post
        await posts_collection.delete_one({"_id": ObjectId(post_id)})
        
        return {"message": "Post deleted successfully"}
    except Exception as e:
        if "Invalid post ID" in str(e):
            raise HTTPException(status_code=400, detail="Invalid post ID")
        raise e

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

