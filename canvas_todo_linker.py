from pprint import pprint
from typing import Dict
from datetime import datetime, timedelta
import dateutil.parser

from models import CanvasAssignment, CanvasCourse, TodoTask
from to_do_connector import auth_for_session, create_task_from_task_obj, get_all_tasks_in_list, get_or_create_todolist, GRAPH_URL, config, cache
from canvas_connector import get_month_assignments, get_all_courses

def assignment_task_namer(assignment: CanvasAssignment, course_id_dict: Dict[int, str], parse_at_dash: bool = False) -> str:
    course_name = course_id_dict[assignment.course_id]
    if parse_at_dash:
        course_name = course_name.split('-', 1)[0]
    #Remove hashtags, replace spaces with underscores, and put hashtag in front of the course name
    course_name = course_name.replace('#','')
    assignment.name = assignment.name.replace('#','')
    course_name = course_name.replace(' ','_')
    return ('#' + course_name + ' - ' + assignment.name).strip()

def create_task_obj_from_assignment(assignment: CanvasAssignment, course_id_dict: Dict[int, str]) -> TodoTask:
    #parse the due_at time, and set reminder back a specified number of hours
    reminder_time = (dateutil.parser.isoparse(assignment.due_at.replace('Z', '')) - timedelta(hours = config["REMINDER_HOURS_BEFORE_DUE"])).isoformat()

    return TodoTask(
        assignment_task_namer(assignment, course_id_dict, config["BREAK_COURSENAME_AT_DASH"]),
        assignment.html_url,
        config["SET_REMINDERS"],
        dueDateTime=assignment.due_at,
        reminderDateTime = reminder_time
        )

s = auth_for_session()
print('--------')
print("Getting Canvas courses and assignments for the next month")
courses = get_all_courses()
course_id_dict = {course.id:str(course.name) for course in courses}
assignments = get_month_assignments()
1
print(f"Checking for '{config['TASK_LIST_NAME']}' To Do list")
canvas_todolist_id = get_or_create_todolist(s, config['TASK_LIST_NAME'])
print('Getting previous assignment tasks from this list')
old_tasks = get_all_tasks_in_list(s, canvas_todolist_id)
updated_tasks = [create_task_obj_from_assignment(assignment, course_id_dict) for assignment in assignments]
#filter out any duplicates by putting same titles in dictionary
updated_tasks_by_title = {task.title:task for task in updated_tasks}

print('Uploading and updating Canvas assignment tasks into To Do')
res_list = list()
added = 0
updated = 0
old_task_titles = [task.title for task in old_tasks]
for task in updated_tasks_by_title.values():
    is_update = False
    if task.title in old_task_titles:
        is_update = True
        updated += 1
    else:
        added += 1
    res_list.append(create_task_from_task_obj(s, canvas_todolist_id, task, is_update))
print('--------')
print(f'{added} tasks were newly added to To Do')
print(f'{updated} tasks were updated on To Do')
