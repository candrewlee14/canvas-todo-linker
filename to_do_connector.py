import sys
import os, atexit
import json
import logging
import time
from typing import List
from msal import token_cache
import webbrowser
import pyperclip

import requests
import msal
from requests.sessions import Session
from models import TodoTask

# This will cache the token so we don't have to login through the website every time
cache = msal.SerializableTokenCache()
if os.path.exists("my_cache.bin"):
    cache.deserialize(open("my_cache.bin", "r").read())
atexit.register(lambda:
    open("my_cache.bin", "w").write(cache.serialize())
    # Hint: The following optional line persists only when state changed
    # if cache.has_state_changed else None
    )

with open('config.json') as config_file:
    config = json.load(config_file)

GRAPH_URL = config['RESOURCE'] + '/' + config['API_VERSION']


# Function based on https://github.com/AzureAD/microsoft-authentication-library-for-python/blob/dev/sample/device_flow_sample.py
def auth_for_session(auto = True) -> Session :
    """
    Get an authorization bearer token from Microsoft to access Microsoft Graph data and returns a requests Session.
    """

    # Optional logging
    # logging.basicConfig(level=logging.DEBUG)  # Enable DEBUG log for entire script
    # logging.getLogger("msal").setLevel(logging.INFO)  # Optionally disable MSAL DEBUG logs

    # Create a preferably long-lived app instance which maintains a token cache.
    app = msal.PublicClientApplication(
        config["CLIENT_ID"], authority='https://login.microsoftonline.com/common',
        token_cache = cache
        # token_cache=...  # Default cache is in memory only.
                        # You can learn how to use SerializableTokenCache from
                        # https://msal-python.rtfd.io/en/latest/#msal.SerializableTokenCache
        )

    # The pattern to acquire a token looks like this.
    result = None

    # Note: If your device-flow app does not have any interactive ability, you can
    #   completely skip the following cache part. But here we demonstrate it anyway.
    # We now check the cache to see if we have some end users signed in before.
    accounts = app.get_accounts()
    if accounts:
        logging.info("Account(s) exists in cache, probably with token too. Let's try.")
        print("Pick the account you want to use to proceed:")
        for i, a in enumerate(accounts):
            print(f'({str(i+1)}) ' + a["username"])
        print(f'({str(len(accounts) + 1)}) None')
        choice = input('Enter the number of an option: ')
        # Assuming the end user chose this one
        try:
            choice_num = int(choice)
            if choice_num > 0 and choice_num < len(accounts) + 1:
                chosen = accounts[choice_num-1]
                # Now let's try to find a token in cache for this account
                result = app.acquire_token_silent(config["SCOPE"], account=chosen)
            elif choice_num == len(accounts) + 1:
                print("Starting up web login for other account...")
            else: 
                print("Response was not one of the given options...")
        except:
            print("Invalid response...")

    if not result:
        logging.info("No suitable token exists in cache. Let's get a new one from AAD.")

        flow = app.initiate_device_flow(scopes=config["SCOPE"])
        if "user_code" not in flow:
            raise ValueError(
                "Fail to create device flow. Err: %s" % json.dumps(flow, indent=4))

        if auto:
            pyperclip.copy(flow['user_code']) # copy user code to clipboard
            webbrowser.open(flow['verification_uri']) # open browser
            print(f'The code {flow["user_code"]} has been copied to your clipboard, '
                f'and your web browser is opening {flow["verification_uri"]}. '
                'Paste the code to sign in.')
        else:
            print(flow["message"])
        sys.stdout.flush()  # Some terminal needs this to ensure the message is shown

        # Ideally you should wait here, in order to save some unnecessary polling
        # input("Press Enter after signing in from another device to proceed, CTRL+C to abort.")

        result = app.acquire_token_by_device_flow(flow)  # By default it will block
            # You can follow this instruction to shorten the block time
            #    https://msal-python.readthedocs.io/en/latest/#msal.PublicClientApplication.acquire_token_by_device_flow
            # or you may even turn off the blocking behavior,
            # and then keep calling acquire_token_by_device_flow(flow) in your own customized loop.

    if "access_token" in result:
        session = Session()
        session.headers.update({'Authorization': f'Bearer {result["access_token"]}', 'Content-Type':'application/json'})
        print("Authentication successful!")
        return session
    else:
        print(result.get("error"))
        print(result.get("error_description"))
        print(result.get("correlation_id"))  # You may need this when reporting a bug

def get_or_create_todolist(s: Session, name: str) -> str:
    """Looks for given task list name in To Do lists, and if it doesn't exist, it creates it.
    Returns the list id
    """
    lists = s.get(GRAPH_URL + '/me/todo/lists')
    if lists.status_code != 200:
        print("Response came back with error " + str(lists.status_code))
        quit()
    canvas_tasklist_ids = [lis['id'] for lis in lists.json()['value'] if lis['displayName'] == name]
    if not canvas_tasklist_ids:
        # canvas list does not exist, we need to make it:
        res = s.post(GRAPH_URL + '/me/todo/lists', json={'displayName':config['TASK_LIST_NAME']})
        if res.status_code != 201:
            print("Could not insert list. Error " + str(lists.status_code))
            quit()
        canvas_tasklist_ids.append(res.json()['id'])
    return canvas_tasklist_ids[0]

def create_task_from_task_obj(s: Session, todolist_id: str, task: TodoTask, is_update: bool = False) -> str:
    res = None
    if is_update:
        res = s.patch(GRAPH_URL + f'/me/todo/lists/{todolist_id}/tasks' , json=task.to_json())
    else:
        res = s.post(GRAPH_URL + f'/me/todo/lists/{todolist_id}/tasks' , json=task.to_json())
    return res.json()

def get_all_tasks_in_list(s: Session, todolist_id: str) -> List[TodoTask]:
    tasks = list()
    i = 0
    while True:
        next_endpoint = GRAPH_URL + f'/me/todo/lists/{todolist_id}/tasks?$skip={10*i}'
        tasks_data = s.get(next_endpoint).json()
        tasks.extend([TodoTask.from_dict(task) for task in tasks_data['value']])
        i+=1
        if len(tasks_data['value']) < 10: 
            return tasks;

"""
s = auth_for_session()
time.sleep(1)
list_id = get_or_create_canvas_list(s)
tasks_data = s.get(GRAPH_URL + f'/me/todo/lists/{list_id}/tasks').json()['value']
tasks = [TodoTask.from_dict(task) for task in tasks_data]
print(tasks)
"""
