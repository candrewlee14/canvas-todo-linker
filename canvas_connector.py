from requests.sessions import Session
import datetime
from pprint import pprint
from typing import List

from utilities import chunks
from models import CanvasAssignment, CanvasCourse
from start_config import config

# declare constant globals 
CHUNK_SIZE = 9
PER_PAGE = 50
SESSION = Session()
SESSION.headers.update({'Authorization': f'Bearer {config["CANVAS_TOKEN"]}'})


def get_all_courses():
    """Get all user canvas course ids and return list of contexts"""
    course_params = {
            'enrollment_state':'active',
            'per_page': PER_PAGE,
        }
    courses_res = SESSION.get(config["CANVAS_URL"] + '/api/v1/courses', params=course_params)
    courses = [CanvasCourse.from_dict(course) for course in courses_res.json()]
    #Canvas expects contexts for courses to be course_:id
    return courses

def get_month_assignments():
    """Get all canvas assignments in all courses for the next month"""
    courses = get_all_courses()
    course_contexts = ['course_' + str(course.id) for course in courses]
    # set date range for getting assignments
    date_now = datetime.datetime.utcnow()
    month_delta = datetime.timedelta(days=365/12)
    day_delta = datetime.timedelta(days=1)
    next_month = date_now + month_delta
    yesterday = date_now - day_delta
    
    # Canvas API only takes at max 10 contexts
    # break up contexts into chunks 
    course_chunks = list(chunks(course_contexts, CHUNK_SIZE))
    all_assignments : List[CanvasAssignment] = list()  
    # for each chunk, request the assignment calendar events
    for course_context_chunk in course_chunks:
        cal_params = {
                'type':'assignment',
                'context_codes[]': course_context_chunk, 
                'start_date': yesterday.isoformat(),
                'end_date': next_month.isoformat(),
                'per_page': PER_PAGE,
            }
        assignment_events_res = SESSION.get(config["CANVAS_URL"] + '/api/v1/calendar_events', params=cal_params)
        #pull the assignment out of the assignment event and put them into the list
        all_assignments.extend([CanvasAssignment.from_dict(event['assignment']) for event in assignment_events_res.json()])
        
    return all_assignments

#print(get_all_assignments())
