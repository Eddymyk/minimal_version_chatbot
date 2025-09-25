from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
import google.generativeai as genai
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
# ---------------- CONFIG ----------------


SECRET_KEY = "supersecretkey"   # move to .env later
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

app = FastAPI()

# Dummy DB (replace with MongoDB later)
fake_users_db = {}

# ---------------- AUTH ----------------
def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta=None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

@app.post("/register")
def register(username: str, password: str):
    if username in fake_users_db:
        raise HTTPException(status_code=400, detail="User already exists")
    fake_users_db[username] = {"username": username, "password": get_password_hash(password)}
    return {"msg": "User registered successfully"}

@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = fake_users_db.get(form_data.username)
    if not user or not verify_password(form_data.password, user["password"]):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    access_token = create_access_token(data={"sub": user["username"]})
    return {"access_token": access_token, "token_type": "bearer"}

# ---------------- GEMINI CHAT ----------------
@app.post("/chat")
def chat(prompt: str, token: str = Depends(oauth2_scheme)):
    try:
        username = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])["sub"]
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)
    return {"user": username, "prompt": prompt, "response": response.text}

