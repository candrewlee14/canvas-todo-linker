import json

class JsonSerializableBase():
    """JSON-Serializable base class"""
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



        

class CanvasCourse():
    """Canvas Course class that helps in JSON deserialization"""
    def __init__(self, id, name):
        self.id = id
        self.name = name

    @classmethod
    def from_dict(cls, data: dict):
        try:
            return cls(
                data['id'],
                data['name']
            ) 
        except:
            print("CanvasCourse dictionary came in unnexpected format")
            quit()


class CanvasAssignment():
    """Canvas Assignment class that helps in JSON deserialization"""
    def __init__(self, name: str, dueDateTime: str, html_url: str, course_id: int, id = None):
        super().__init__()
        self.name = name
        self.due_at = dueDateTime
        self.html_url = html_url
        self.course_id = course_id
        self.id = id
    @classmethod
    def from_dict(cls, data: dict):
        try:
            return cls(
                data['name'],
                data['due_at'],
                data['html_url'],
                int(data['course_id']),
                id = data['id']
            ) 
        except:
            print("CanvasAssignment dictionary came in unnexpected format")
            quit()

class TodoTask(JsonSerializableBase):
    """Microsoft To Do Task class that helps in JSON serialization/deserialization"""
    def __init__(self, title: str, body: str, isReminderOn: bool, dueDateTime: str = None, reminderDateTime: str = None, id = None):
        super().__init__()
        self.title = title
        self.body = body
        self.isReminderOn = isReminderOn
        self.dueDateTime = dueDateTime
        self.reminderDateTime =  reminderDateTime
        self.id = id

    @classmethod
    def from_dict(cls, data: dict):
        try:
            return cls(
                data['title'],
                data['body']['content'],
                data['isReminderOn'],
                # assumes UTC timezone. This may need a fix in the future
                dueDateTime = data.get('dueDateTime', {}).get('dateTime', None),
                reminderDateTime = data.get('reminderDateTime', {}).get('dateTime', None),
                id = data['id']
            ) 
        except:
            print("TodoTask dictionary came in unnexpected format")
            quit()

    def to_json(self):
        json_dict = dict()
        json_dict['title'] = self.title
        json_dict['isReminderOn'] = self.isReminderOn
        json_dict['dueDateTime'] = {'dateTime': self.dueDateTime, 'timeZone' : 'UTC'}
        json_dict['body'] = {'content' : self.body, 'contentType': 'text'}
        json_dict['reminderDateTime'] = {'dateTime': self.reminderDateTime, 'timeZone' : 'UTC'}
        return json_dict
