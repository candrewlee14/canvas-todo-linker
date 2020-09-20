import json
import datetime

class JsonObject():
    def __init__(self):
        self.id = None

    def get_fields_dict(self, includeId: bool):
        res = dict(self.__dict__)
        for key in res.keys:
            res[key] = str(res[key])
        if not includeId:
            res.pop('id')
        return res

    def to_json(self, includeId: bool = False):
        return json.dumps(self, default=lambda o: o.get_fields_dict(includeId), 
            sort_keys=True, indent=4)

class TodoTask(JsonObject):
    def __init__(self, title:str, dueDateTime:str, reminderDateTime:str, id = None):
        super().__init__()
        self.title = title
        self.isReminderOn = True
        self.dueDateTime = dueDateTime
        self.reminderDateTime =  reminderDateTime
            
class CanvasAssignment(JsonObject):
    def __init__(self, name:str, dueDateTime:str, html_url:str, id = None):
        super().__init__()
        self.name = name
        self.due_at = dueDateTime
        self.html_url = html_url
