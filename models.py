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

class TodoTask(JsonSerializableBase):
    """Microsoft To Do Task class that helps in JSON serialization/deserialization"""
    def __init__(self, title: str, dueDateTime: str, reminderDateTime: str, id = None):
        super().__init__()
        self.title = title
        self.isReminderOn = True
        self.dueDateTime = dueDateTime
        self.reminderDateTime =  reminderDateTime

    @classmethod
    def from_dict(cls, data: dict):
        try:
            return cls(
                data['title'],
                data['isReminderOn'],
                data['dueDateTime'],
                data['reminderDateTime'],
                id = data['id']
            ) 
        except:
            print("TodoTask dictionary came in unnexpected format")
            quit()

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
    def __init__(self, name: str, dueDateTime: str, html_url: str, id = None):
        super().__init__()
        self.name = name
        self.due_at = dueDateTime
        self.html_url = html_url

    @classmethod
    def from_dict(cls, data: dict):
        try:
            return cls(
                data['name'],
                data['due_at'],
                data['html_url'],
                id = data['id']
            ) 
        except:
            print("CanvasAssignment dictionary came in unnexpected format")
            quit()
