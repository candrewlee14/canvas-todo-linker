import requests
import json
import datetime
from pprint import pprint
from utilities import chunks

# load config file
with open('config.json') as config_file:
    data = json.load(config_file)

# declare constant globals 
CHUNK_SIZE = 9
PER_PAGE = 50
CANVAS_HEADERS = {
        'Authorization': 'Bearer ' + data['canvas_token'],
    }

def get_course_contexts():
    """Get all user canvas course ids and return list of contexts"""
    course_params = {
            'enrollment_state':'active',
            'per_page': PER_PAGE,
        }
    courses_res = requests.get(
        'https://' + data["canvas_url"] + '/api/v1/courses', 
        headers=CANVAS_HEADERS, params=course_params)
    #Canvas expects contexts for courses to be course_:id
    course_contexts = ['course_' + str(course['id']) for course in courses_res.json() if 'name' in course];
    return course_contexts

def get_all_assignments():
    """Get all canvas assignments in all courses for the next month"""
    course_contexts = get_course_contexts()
    # set date range for getting assignments
    date_now = datetime.datetime.today()
    month_delta = datetime.timedelta(days=365/12)
    next_month = date_now + month_delta
    
    # Canvas API only takes at max 10 contexts
    # break up contexts into chunks 
    course_chunks = list(chunks(course_contexts, CHUNK_SIZE))
    all_assignments = list()
    # for each chunk, request the assignment calendar events
    for course_context_chunk in course_chunks:
        cal_params = {
                'type':'assignment',
                'context_codes[]': course_contexts, 
                'start_date': date_now.isoformat(),
                'end_date': next_month.isoformat(),
                'per_page': PER_PAGE,
            }
        assignments_res = requests.get(
            'https://' + data["canvas_url"] + '/api/v1/calendar_events', 
            headers=CANVAS_HEADERS, params=cal_params)
        all_assignments.extend(assignments_res.json())
        
    return all_assignments
