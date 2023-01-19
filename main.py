from datetime import datetime, timedelta

from dateutil.parser import *
from fastapi import FastAPI, Depends, HTTPException, status, Request, UploadFile, File
from passlib.context import CryptContext
from sqlalchemy.orm import Session

import shutil
import models
from authentications import authenticate_user, create_access_token, get_current_user, get_password_hash
from database import Base, engine, SessionLocal
from pagination import get_data
from schemas import User, UserProfile, ChangePassword, Assessment, UserAnswer
from utils import get_assessment_details, is_teacher_type_user

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

@app.post("/profileImage/")
def uploadProfileImage(token:str, file: UploadFile = File(...), session: Session = Depends(get_session)):
    """
    Function to upload profile image of user.
    """
    user = get_current_user(session, token)
    with open(f"media/{user.username}.jpg", "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"Status": "f{user.username} image uploaded."}             

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

# Assessment
@app.post("/createAssessment/")
def CreateAssessment(token: str, assessment: Assessment, session: Session = Depends(get_session)):
    """
    Function will create assessment questions
    """
    user = get_current_user(session, token)
    if user.user_type == "teacher":
        assessment_details = models.Assessment(
            subject_name = assessment.subject_name,
            date = parse(assessment.date),
            time = datetime.strptime(assessment.time, '%H:%M').time(),    
            questions = assessment.questions,
            creator_id = user.id         
        )
        session.add(assessment_details)
        session.commit()
        session.refresh(assessment_details)

        return {"Status": assessment_details}
    else:
        return {"Status": f"{user.username} you're not authorized to perform this operation."}

@app.post("/searchAssessment")
def searchAssessment(search_param: str, page: int, limit: int, request: Request, session: Session = Depends(get_session)):
    """
    This function will search assessment filter is working on assessment subject with pagination.
    """
    filtered_data = session.query(models.Assessment).filter(models.Assessment.subject_name.contains(search_param))
    # pagination will work with page number and limit.
    # limit represent how many records page should contain.
    data = get_data(filtered_data, page, limit)
    if not data:
        return {"Status": "No result found with given keyword."}
    
    return {"Status": [assessment.subject_name for assessment in data]}

@app.post("/detailAssessment/{id:int}")
def getDetailAssessment(id: int, token: str, session: Session = Depends(get_session)):
    """
    Function will fetch details of assessment.
    with type teacher user can view answer also.
    with student type user can view questions only.
    """
    user = get_current_user(session, token)
    assessment_obj = session.query(models.Assessment).get(id)    
    data = get_assessment_details(user, assessment_obj)
    return {"Status": data}

@app.post("/submitAssessment/{id:int}")
def userAssessment(id: int, token: str, answer: UserAnswer, session: Session = Depends(get_session)):
    """
    Function will used to submit assessment for student type user.
    """
    user = get_current_user(session, token)
    assessment_obj = session.query(models.Assessment).get(id)
    if not is_teacher_type_user(user):
        answer_details = models.AnswerAssessment(
            answers = answer.answer,
            student_id = user.id,
            user_assessment_id = assessment_obj.id,                     
        )
        session.add(answer_details)
        session.commit()
        session.refresh(answer_details)

        return {"Status": answer_details}
    else:
        return {"Status": f"{user.username} you're not authorized to perform this operation."}

@app.delete("/deleteAssessment/{id:int}")
def assessmentDelete(id: int, token:str, session: Session = Depends(get_session)):
    """
    This function will remove assessment.
    only teacher type user can remove assessment.
    """
    user = get_current_user(session, token)
    if is_teacher_type_user(user):
        assessment = session.query(models.Assessment).get(id)
        assessment_name = f"{assessment.subject_name} - {assessment.id}"
        session.delete(assessment)
        session.commit()
        session.close()
        return {"Status": f"{assessment_name} is removed"}
    return {"Status": f"you don't have permission to remove assessment!"}

@app.put("/updateAssessment/{id:int}")
def assessmentUpdate(id: int, assessment:Assessment, token:str, session: Session = Depends(get_session)):
    """
    Function will updaye the assessment detail.
    only teacher type of user allowed to perform this action.
    """
    user = get_current_user(session, token)
    if is_teacher_type_user(user):
        assessment_obj = session.query(models.Assessment).get(id)
        if assessment_obj:
            assessment_obj.subject_name = assessment.subject_name
            assessment_obj.date = parse(assessment.date)
            assessment_obj.time = datetime.strptime(assessment.time, '%H:%M').time()
            assessment_obj.questions = assessment.questions
            session.commit()
            return {"Status": f"{assessment_obj.subject_name} is updated"}
        return {"Status": "No data found!"}    
    return {"Status": f"you don't have permission to remove assessment!"}