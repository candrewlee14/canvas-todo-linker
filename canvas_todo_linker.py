from requests.sessions import Session
from typing import Dict, List, Any
from datetime import datetime, timedelta

from models import CanvasAssignment, CanvasCourse, TodoTask
from to_do_connector import auth_for_session, create_task_from_task_obj, get_or_create_canvas_todolist, GRAPH_URL, config, cache
from canvas_connector import get_all_assignments, get_all_courses


def create_task_obj_from_assignment(assignment: CanvasAssignment, course_id_dict: Dict[int, str], parse_at_dash: bool = False) -> TodoTask:
    course_name = course_id_dict[assignment.course_id]
    #parse the due_at time, and set reminder back a specified number of hours
    reminder_time = (datetime.fromisoformat(assignment.due_at.replace('Z', '')) - timedelta(hours = config["REMINDER_HOURS_BEFORE_DUE"])).isoformat()
    if parse_at_dash:
        course_name = course_name.split('-', 1)[0]
    return TodoTask(
        course_name + ' - ' + assignment.name, 
        assignment.html_url,
        config["SET_REMINDERS"],
        dueDateTime=assignment.due_at,
        reminderDateTime = reminder_time
        )

s = auth_for_session()
courses = get_all_courses()
course_id_dict = {course.id:str(course.name) for course in courses}
assignments = get_all_assignments()
task = create_task_obj_from_assignment(assignments[0], course_id_dict, parse_at_dash=True)
print(task)
canvas_todolist_id = get_or_create_canvas_todolist(s)
res_data = create_task_from_task_obj(s, canvas_todolist_id, task)
print(res_data)
