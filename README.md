# Thinkvink-FastAPI-Task

**Project's title:**
**Examer**

**About:**

Technology used: FastAPI

An examer API's with CRUD (create, read, update, and delete) operations would allow users to register themselve and user type with teacher can add assessment, as well as. Teacher would be able to create new asssessment by entering questions and answers, date, time, and subject then save or publish the exam for others to take. They would also be able to edit or delete existing assessment.

When taking an assessment, users would see the questions and be able to select their answers. 

In summary, the app would provide the functionality to create, read, update and delete users and assessments, and also allows the user to take the asssessment.

**How to run:**
- create virtual environment.
- activate virtual environment.
- install requirments.txt file inside requirements folder.
- go inside examer the run `uvicorn main:app --reload`
- open in browser: http://127.0.0.1:8000/docs#
- test API

references:
Choces: https://stackoverflow.com/questions/6262943/sqlalchemy-how-to-make-django-choices-using-sqlalchemy,
        https://stackoverflow.com/questions/2317081/sqlalchemy-maximum-column-length
Passwod Char length: https://stackoverflow.com/questions/50174325/define-minimum-length-for-postgresql-string-column-with-sqlalchemy
hash password: https://www.fastapitutorial.com/blog/password-hashing-fastapi/
paginations: https://stackoverflow.com/questions/60152442/does-fastapi-contrib-has-paginator-for-postgresql
