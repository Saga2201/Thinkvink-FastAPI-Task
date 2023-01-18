from fastapi import FastAPI, Depends, HTTPException, status
import models 
from schemas import User, UserProfile, ChangePassword
from database import Base, engine, SessionLocal
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from authentications import authenticate_user, create_access_token, get_current_user, get_password_hash
from datetime import timedelta 

Base.metadata.create_all(engine)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ACCESS_TOKEN_EXPIRE_MINUTES = 30

def get_session():
    session = SessionLocal()
    try:
        yield session

    finally:
        session.close()

app = FastAPI()

@app.get("/userProfile/{id}")
def getUsersProfile(id: int, session: Session = Depends(get_session)):
    """
    Function will return user details from given id.
    """
    user = session.query(models.User).get(id)
    return {"Userlist": user}    

def get_username(session):
    """
    Function will return uniq username.
    data will get all user records and will pick last record id and by increment by 1 will add to new username.
    """
    data = session.query(models.User).all()
    counter = data[-1].id + 1
    return f"User{counter}"

@app.post("/register")
def userRegistration(user: User, session: Session = Depends(get_session)):
    """
    User registration function.

    Note: username will be automatically generate by get_username() 
    """
    email_exist = session.query(models.User).filter(models.User.email==user.email).first()
    if not email_exist:
        user_details = models.User(username = get_username(session), 
            email = user.email,
            user_type = user.user_type,
            password = get_password_hash(user.password)                    
        )
        session.add(user_details)
        session.commit()
        session.refresh(user_details)

        return {"Status": user_details}
    else:
        return {"Status": "Email is already exist."}    

@app.put("/profileUpdate/{id}")
def userProfileUpdate(id: int, user_details:UserProfile, session: Session = Depends(get_session)):
    """
    Function will update user profile.
    """
    user_exist = session.query(models.User).filter(models.User.username==user_details.username).first()
    email_exist = session.query(models.User).filter(models.User.email==user_details.email).first()
    if not user_exist and not email_exist:
        user = session.query(models.User).get(id)
        user.username = user_details.username
        user.email = user_details.email
        user.user_type = user_details.user_type
        user.password = user_details.password
        session.commit()
        
        return {"Status": f"{user.username} is updated."}
    else:
        return {"Status": "Username or mail is already exist."}    

@app.delete("/userRemove/{id}")
def userDelete(id: int, session: Session = Depends(get_session)):
    """
    Function will delete user from given id.
    """
    user = session.query(models.User).get(id)
    username = user.username
    session.delete(user)
    session.commit()
    session.close()

    return {"Status": f"{username} removed!"}

@app.patch("/changePassword/{id}")
def ChangeUserPassword(token: str, user_data: ChangePassword ,session: Session = Depends(get_session)):
    """
    User password change functionality by user token.
    """
    user = get_current_user(session, token)
 
    if user_data.new_password == user_data.confirm_new_password:
        user.password = get_password_hash(user_data.new_password)
        session.commit()
        return {"Status": f"{user.username} password has been changed!"}
    return{"Status": "new password and confirm password must be same."}

@app.post("/login/")
def user_login(email: str, password: str, session: Session = Depends(get_session)): 
    """
    Function will return token after successful authentication of user credential.
    """
    user_email = session.query(models.User).filter(models.User.email==email).first()
    user = authenticate_user(session, user_email.username, password)
    if not user_email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/logout/")
def userLogout(token: str, session: Session = Depends(get_session)):
    """
    Function will logout the current user.

    set expired time to -1, so, token will expire.
    """
    user = get_current_user(session, token)
    access_token_expires = timedelta(minutes=-1)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "status": "Logout"}