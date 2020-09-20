import sys  # For simplicity, we'll read config file from 1st CLI param sys.argv[1]
import json
import logging

import requests
import msal


with open('config.json') as config_file:
    config = json.load(config_file)

GRAPH_URL = config['RESOURCE'] + '/' + config['API_VERSION']


# Function based on https://github.com/AzureAD/microsoft-authentication-library-for-python/blob/dev/sample/device_flow_sample.py
def auth_for_session() -> requests.Session :
    """
    Get an authorization bearer token from Microsoft to access Microsoft Graph data and return a requests Session.
    """
    """
    The configuration file would look like this:
    {
        "authority": "https://login.microsoftonline.com/common",
        "client_id": "your_client_id",
        "SCOPE": ["User.ReadBasic.All"],
            // You can find the other permission names from this document
            // https://docs.microsoft.com/en-us/graph/permissions-reference
        "endpoint": "https://graph.microsoft.com/v1.0/users"
            // You can find more Microsoft Graph API endpoints from Graph Explorer
            // https://developer.microsoft.com/en-us/graph/graph-explorer
    }
    You can then run this sample with a JSON configuration file:
        python sample.py parameters.json
    """

    # Optional logging
    # logging.basicConfig(level=logging.DEBUG)  # Enable DEBUG log for entire script
    # logging.getLogger("msal").setLevel(logging.INFO)  # Optionally disable MSAL DEBUG logs

    # Create a preferably long-lived app instance which maintains a token cache.
    app = msal.PublicClientApplication(
        config["CLIENT_ID"], authority='https://login.microsoftonline.com/common',
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
        for a in accounts:
            print(a["username"])
        # Assuming the end user chose this one
        chosen = accounts[0]
        # Now let's try to find a token in cache for this account
        result = app.acquire_token_silent(config["SCOPE"], account=chosen)

    if not result:
        logging.info("No suitable token exists in cache. Let's get a new one from AAD.")

        flow = app.initiate_device_flow(scopes=config["SCOPE"])
        if "user_code" not in flow:
            raise ValueError(
                "Fail to create device flow. Err: %s" % json.dumps(flow, indent=4))

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
        session = requests.Session()
        session.headers.update({'Authorization': f'Bearer {result["access_token"]}'})
        return session
    else:
        print(result.get("error"))
        print(result.get("error_description"))
        print(result.get("correlation_id"))  # You may need this when reporting a bug

def get_or_create_canvas_list() -> str:
    """Looks for given task list name in To Do lists, and if it doesn't exist, it creates it.
    Returns the list id
    """
    lists = s.get(GRAPH_URL + '/me/todo/lists')
    if lists.status_code != 200:
        print("Response came back with error " + str(lists.status_code))
        quit()
    canvas_ids = [lis['id'] for lis in lists.json()['value'] if lis['displayName'] == config['TASK_LIST_NAME']]
    if not canvas_ids:
        # canvas list does not exit, we need to make it:
        res = s.post(GRAPH_URL + '/me/todo/lists', json={'displayName':config['TASK_LIST_NAME']})
        if res.status_code != 201:
            print("Could not insert list. Error " + str(lists.status_code))
            quit()
        canvas_ids.append(res.json()['id'])
    return canvas_ids[0]

def create_task_in_list(list_id: str):
    res = s.post(GRAPH_URL + f'/me/todo/lists/{list_id}/tasks' , json={'title':'Test Task 2', 'body':{'content':'link would go here', 'contentType':'text'}})
    return res.json()

s = auth_for_session()
lis_id = get_or_create_canvas_list()

print(json.dumps(create_task_in_list(lis_id), indent=2))
