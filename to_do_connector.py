from adal import AuthenticationContext
import webbrowser
import pyperclip
import requests
import json
import datetime
from pprint import pprint

# load config file
with open('config.json') as config_file:
    data = json.load(config_file)
    
# From https://github.com/microsoftgraph/python-sample-console-app/blob/master/helpers.py
def device_flow_session(auto=False):
    """Obtain an access token from Azure AD (via device flow) and create
    a Requests session instance ready to make authenticated calls to
    Microsoft Graph.
    client_id = Application ID for registered "Azure AD only" V1-endpoint app
    auto      = whether to copy device code to clipboard and auto-launch browser
    Returns Requests session object if user signed in successfully. The session
    includes the access token in an Authorization header.
    User identity must be an organizational account (ADAL does not support MSAs).
    """
    ctx = AuthenticationContext(data['AUTHORITY_URL'] + data['TENANT_ID'], api_version=None)
    device_code = ctx.acquire_user_code(data['RESOURCE'],
                                        data['CLIENT_ID'])

    # display user instructions
    if auto:
        pyperclip.copy(device_code['user_code']) # copy user code to clipboard
        webbrowser.open(device_code['verification_url']) # open browser
        print(f'The code {device_code["user_code"]} has been copied to your clipboard, '
              f'and your web browser is opening {device_code["verification_url"]}. '
              'Paste the code to sign in.')
    else:
        print(device_code['message'])

    token_response = ctx.acquire_token_with_device_code(data['RESOURCE'],
                                                        device_code,
                                                        data['CLIENT_ID'])
    if not token_response.get('accessToken', None):
        return None

    session = requests.Session()
    session.headers.update({'Authorization': f'Bearer {token_response["accessToken"]}',
                            'SdkVersion': 'canvas-todo-linker',
                            'x-client-SKU': 'canvas-todo-linker'})
    return session

s = device_flow_session()
GRAPH_URL = data['RESOURCE'] + '/' + data['API_VERSION']
lists = s.get(GRAPH_URL + '/me/todo/lists')
if lists.status_code != 200:
    print("Response came back with error " + str(lists.status_code))
    quit()
list_ids = [lis['id'] for lis in lists.json()]
tasks = s.get(GRAPH_URL + '/me/todo/lists/'+ list_ids[0] + '/tasks')

pprint(tasks.json())
