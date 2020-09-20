import json

config_template_text = '''
{
    "API_VERSION": "beta",
    "AUTHORITY_URL": "https://login.microsoftonline.com/common/",
    "BREAK_COURSENAME_AT_DASH": true,
    "CANVAS_TOKEN": "",
    "CANVAS_URL": "",
    "CLIENT_ID": "00876b71-2f31-4715-8243-c51238091e50",
    "REMINDER_HOURS_BEFORE_DUE": 1,
    "RESOURCE": "https://graph.microsoft.com",
    "SCOPE": [
        "Tasks.ReadWrite"
    ],
    "SET_REMINDERS": true,
    "TASK_LIST_NAME": "Canvas"
}
'''

def start_config() -> dict:
    """Set up config file and insert CANVAS_TOKEN and CANVAS_URL if blank"""
    #Check if file exists
    try:
        config_file=open('config.json')
        config_file.close()
    except FileNotFoundError:
        print("Config file couldn't be found. Creating one...")
        with open('config.json', 'w') as config_file:
            config_file.write(config_template_text)
    # Try reading json of config file and adding missing Canvas fields
    try:
        with open('config.json', 'r+') as config_file:
            config_data = json.load(config_file)
            if config_data.get("CANVAS_TOKEN", "") == "":
                config_data["CANVAS_TOKEN"] = input('Please paste your Canvas Access Token here: ').strip()
            if config_data.get("CANVAS_URL", "") == "":
                config_data["CANVAS_URL"] = input('Please paste your Canvas domain (https://DOMAIN_NAME.instructure.com) here: ').strip()
            config_file.seek(0)
            config_file.write(json.dumps(config_data, indent = 4, sort_keys = True))
            config_file.truncate()
            return config_data
    except:
        print("File was in incorrect format. Please refer to README.")
        input('Press ENTER to exit.')
        quit()

config = start_config()
