def is_teacher_type_user(user):
    """
    if user type is teacher then it will return True else False.
    """
    if user.user_type == "teacher":
        return True
    return False
    
def get_assessment_details(user, assessment_data):
    """
    return assessment details according to user type.
    """
    if is_teacher_type_user(user):
        return {
            "subject": assessment_data.subject_name,
            "date": assessment_data.date,
            "time": assessment_data.time,
            "questions" : assessment_data.questions
        }
    else:
        return {
            "subject": assessment_data.subject_name,
            "date": assessment_data.date,
            "time": assessment_data.time,
            "questions" : dict.fromkeys(assessment_data.questions.keys(), "hide")
        }
