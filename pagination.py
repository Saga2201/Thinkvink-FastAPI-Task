from models import Assessment
from fastapi import HTTPException

def get_data(filtered_data, page: int = 0, limit: int = 1):
    # Note not the best option for large data sets.
    try:
        data = filtered_data.offset(page).limit(limit).all()
        # breakpoint()
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail='There was an error while processing your request.')