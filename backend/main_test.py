from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
import os
from dotenv import load_dotenv
import uuid

load_dotenv()

app = FastAPI(title="Full-Stack Template API (Test)", version="1.0.0")

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
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "test-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# In-memory storage for testing
users_db = {}
posts_db = {}

# Pydantic models
class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class User(BaseModel):
    id: str
    username: str
    email: str
    created_at: datetime

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
    id: str
    title: str
    content: str
    category: str
    author_id: str
    author_username: str
    created_at: datetime
    updated_at: datetime

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
    
    user = users_db.get(username)
    if user is None:
        raise credentials_exception
    return user

# Initialize with demo user
demo_user_id = str(uuid.uuid4())
demo_password_hash = get_password_hash("demo123")
users_db["demo"] = {
    "_id": demo_user_id,
    "username": "demo",
    "email": "demo@example.com",
    "password": demo_password_hash,
    "created_at": datetime.utcnow()
}

# Initialize with demo posts
demo_posts = [
    {
        "title": "Welcome to FullStack Template",
        "content": "This is a demo post to showcase the CRUD functionality of our full-stack application. You can create, read, update, and delete posts through the admin dashboard.",
        "category": "general"
    },
    {
        "title": "Getting Started with React",
        "content": "React is a powerful JavaScript library for building user interfaces. This template includes React with modern hooks, context API, and routing.",
        "category": "technology"
    },
    {
        "title": "FastAPI Backend Features",
        "content": "Our backend is built with FastAPI, providing automatic API documentation, type validation, and high performance. It includes JWT authentication and CRUD operations.",
        "category": "technology"
    }
]

for i, post_data in enumerate(demo_posts):
    post_id = str(uuid.uuid4())
    posts_db[post_id] = {
        "_id": post_id,
        "title": post_data["title"],
        "content": post_data["content"],
        "category": post_data["category"],
        "author_id": demo_user_id,
        "author_username": "demo",
        "created_at": datetime.utcnow() - timedelta(days=i),
        "updated_at": datetime.utcnow() - timedelta(days=i)
    }

# Routes
@app.get("/")
async def root():
    return {"message": "Full-Stack Template API (Test Mode)", "version": "1.0.0"}

@app.post("/auth/signup", response_model=Token)
async def signup(user: UserCreate):
    # Check if user already exists
    if user.username in users_db or any(u["email"] == user.email for u in users_db.values()):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered"
        )
    
    # Create new user
    user_id = str(uuid.uuid4())
    hashed_password = get_password_hash(user.password)
    users_db[user.username] = {
        "_id": user_id,
        "username": user.username,
        "email": user.email,
        "password": hashed_password,
        "created_at": datetime.utcnow()
    }
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/auth/login", response_model=Token)
async def login(user: UserLogin):
    # Authenticate user
    db_user = users_db.get(user.username)
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
        id=str(current_user["_id"]),
        username=current_user["username"],
        email=current_user["email"],
        created_at=current_user["created_at"]
    )

@app.get("/posts", response_model=List[Post])
async def get_posts(skip: int = 0, limit: int = 10):
    posts_list = list(posts_db.values())
    posts_list.sort(key=lambda x: x["created_at"], reverse=True)
    posts_slice = posts_list[skip:skip + limit]
    
    return [Post(
        id=str(post["_id"]),
        title=post["title"],
        content=post["content"],
        category=post["category"],
        author_id=str(post["author_id"]),
        author_username=post["author_username"],
        created_at=post["created_at"],
        updated_at=post["updated_at"]
    ) for post in posts_slice]

@app.post("/posts", response_model=Post)
async def create_post(post: PostCreate, current_user: dict = Depends(get_current_user)):
    post_id = str(uuid.uuid4())
    post_doc = {
        "_id": post_id,
        "title": post.title,
        "content": post.content,
        "category": post.category,
        "author_id": current_user["_id"],
        "author_username": current_user["username"],
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    posts_db[post_id] = post_doc
    
    return Post(
        id=str(post_doc["_id"]),
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
    post = posts_db.get(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    return Post(
        id=str(post["_id"]),
        title=post["title"],
        content=post["content"],
        category=post["category"],
        author_id=str(post["author_id"]),
        author_username=post["author_username"],
        created_at=post["created_at"],
        updated_at=post["updated_at"]
    )

@app.put("/posts/{post_id}", response_model=Post)
async def update_post(post_id: str, post_update: PostUpdate, current_user: dict = Depends(get_current_user)):
    post = posts_db.get(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    if post["author_id"] != current_user["_id"]:
        raise HTTPException(status_code=403, detail="Not authorized to update this post")
    
    # Update post
    update_data = {k: v for k, v in post_update.dict().items() if v is not None}
    post.update(update_data)
    post["updated_at"] = datetime.utcnow()
    
    return Post(
        id=str(post["_id"]),
        title=post["title"],
        content=post["content"],
        category=post["category"],
        author_id=str(post["author_id"]),
        author_username=post["author_username"],
        created_at=post["created_at"],
        updated_at=post["updated_at"]
    )

@app.delete("/posts/{post_id}")
async def delete_post(post_id: str, current_user: dict = Depends(get_current_user)):
    post = posts_db.get(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    if post["author_id"] != current_user["_id"]:
        raise HTTPException(status_code=403, detail="Not authorized to delete this post")
    
    # Delete post
    del posts_db[post_id]
    
    return {"message": "Post deleted successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

