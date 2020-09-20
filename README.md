# canvas-todo-linker
Links Canvas LMS Assignments to Microsoft To-Do.

## Setup
Create a `config.json` file and replace these contents with your information:

```
{
    "CANVAS_TOKEN": "TOKEN_HERE",
    "CANVAS_URL": "SCHOOL_HERE.instructure.com",
    "CLIENT_ID": "CID_HERE",
    "AUTHORITY_URL": "https://login.microsoftonline.com/common/",
    "RESOURCE": "https://graph.microsoft.com",
    "API_VERSION": "beta",
    "SCOPE": ["Tasks.ReadWrite"],
    "TASK_LIST_NAME": "Canvas",
    "SET_REMINDERS": true,
    "REMINDER_HOURS_BEFORE_DUE": 12'
    "BREAK_COURSENAME_AT_DASH": true
}
```
Set up a new resource in Azure Portal. Change the **API Permissions** to allow `Tasks.ReadWrite`.
Go to the **Authentication** page.
- Add a platform
    - Check the box next to https://login.microsoftonline.com/common/oauth2/nativeclient.
- Find the setting labeled Default client type and set it to Yes.
- Select Save at the top of the page.
