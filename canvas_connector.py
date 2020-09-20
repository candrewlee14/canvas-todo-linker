import requests
import json
import datetime
from pprint import pprint
from utilities import chunks
from models import CanvasAssignment, CanvasCourse
from typing import List
# load config file
with open('config.json') as config_file:
    data = json.load(config_file)

# declare constant globals 
CHUNK_SIZE = 9
PER_PAGE = 50
SESSION = requests.Session()
SESSION.headers.update({'Authorization': f'Bearer {data["CANVAS_TOKEN"]}'})


def get_all_courses():
    """Get all user canvas course ids and return list of contexts"""
    course_params = {
            'enrollment_state':'active',
            'per_page': PER_PAGE,
        }
    courses_res = SESSION.get('https://' + data["CANVAS_URL"] + '/api/v1/courses', params=course_params)
    courses = [CanvasCourse.from_dict(course) for course in courses_res.json()]
    #Canvas expects contexts for courses to be course_:id
    return courses

def get_all_assignments():
    """Get all canvas assignments in all courses for the next month"""
    courses = get_all_courses()
    course_contexts = ['course_' + str(course.id) for course in courses]
    # set date range for getting assignments
    date_now = datetime.datetime.utcnow()
    month_delta = datetime.timedelta(days=365/12)
    next_month = date_now + month_delta
    
    # Canvas API only takes at max 10 contexts
    # break up contexts into chunks 
    course_chunks = list(chunks(course_contexts, CHUNK_SIZE))
    all_assignments : List[CanvasAssignment] = list()  
    # for each chunk, request the assignment calendar events
    for course_context_chunk in course_chunks:
        cal_params = {
                'type':'assignment',
                'context_codes[]': course_contexts, 
                'start_date': date_now.isoformat(),
                'end_date': next_month.isoformat(),
                'per_page': PER_PAGE,
            }
        assignment_events_res = SESSION.get('https://' + data["CANVAS_URL"] + '/api/v1/calendar_events', params=cal_params)
        #pull the assignment out of the assignment event and put them into the list
        all_assignments.extend([CanvasAssignment.from_dict(event['assignment']) for event in assignment_events_res.json()])
        
    return all_assignments
