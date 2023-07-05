# escape-hub Escape Room Hub Coordinator

## Installation and Execution

Install the python requirements: ```pip install -r requirements.txt```

Start the hub: ```sanic escape-hub```

Note you may need to use ```pip3``` and ```python3``` commands dependent on your setup (python 3 is required).

By default sanic will serve on ```127.0.0.1``` so only respond to requests from the local machine, you can add the switch ```--host=0.0.0.0``` to the sanic command to listen and serve all interfaces. Also ```--debug``` is useful to see a lot of debug output.

## Docker

A Dockerfile is contained within the repository to allow building of a Docker container for the escape hub, configured to run on port 8000 by default.

Example to build the container:
```
docker build -t escapehub .
```

Example to run the container:
```
docker run -p 8000:8000 escapehub
```
(Note this will run in the foreground, add the ```-d``` switch to run in the background).

# Interfacing with Escape Hub Directly (API or WebSocket)

Most operations can be performed via an HTTP request (GET or POST) or a WebSocket transmission, all encoded in JSON. Some operations due to their nature are limited to WebSockets only and are indicated as such (WS Only).

To initiate an action the ```action``` field must contain a string of the relevant action at the top level of the JSON object.

## Action List

### Status
```status``` will return a full status set of the current setup with rooms in data and a status key containing the number of current websocket connections and the number of configured rooms. No required fields.

### Register
```register``` will register a device in a room, required fields are ```room``` containing a room ID key and ```name``` the friendly name for the room, ```status``` the current textual status of the device and a nested ```actions``` list. Each ```actions``` item will be an object containing an ```actionid``` (which will be passed to the device when the action is performed), a friendly ```name``` and a boolean ```enabled``` flag (if it can be provided at this moment to the device). Note if the device performs no actions then an empty list ```[]``` should be passed.

A device UUID will be returned to be used in future communication with the hub.

Example registration JSON body:
```json
{
    "action": "register",
    "room": "1",
    "name": "A Great Device",
    "status": "Ready to Start",
    "actions": [
        {
            "actionid": "FLASH",
            "name": "Flash Lights",
            "enabled": true
        },
        {
            "actionid": "OPENDRAWER",
            "name": "Open Drawer",
            "enabled": false
        }
    ]
}
```

Example response:
```json
{
    "error": false,
    "message": "",
    "data": {},
    "roomid": "e9c1842f-786c-43d7-afa1-8e0a4286e0eb"
}
```

Note this is *not* limited to WebSockets (if from a WebSocket the connection UID will be stored) but the API use is primarily for testing, the intention is that generally registration will be from interactive WebSocket device clients.

A call to ```register``` on success will trigger a publish event.

### Update
```update``` will update the device details in the same form as ```register``` (same JSON package) and will reflect any changes. On completion a publication event will be triggered.

Response will be an error-free response with a message showing that update was successful.

### Subscribe

```subscribe``` (WS only) will add that connection to the subscription list such that whenever a publish event is triggered (```register``` or ```update``` for example) the room data list will be transferred to the client once subscribed.

### Action

```action``` triggers a device action. The payload should contain IDs for the action, the device and the room. For example:
```json
{
    "action": "action",
    "actionid": "ACTIONONE",
    "deviceid": "cf29a-44194-abcdef",
    "roomid": "1"
}
```

A response will be sent with a message confirming the action. If any of the IDs are not found an error response is generated with the ```error``` flag set.

# Using the hubclient Package

A ```hubclient``` package is provided along with an example device client implementation (```demo-client.py```) in the ```client/``` directory. This provides a guide and package for the abstracted use of Escape Hub in any python code.

## Writing a Device Using hubclient

### Including the Package

Your python code must have the ```hubclient.py``` file in the same directory and can then import the package with ```from hubclient import hubclient```. Note there are some client dependencies contained within the ```requirements.txt``` file in the ```client/``` directory. These can be installed with ```pip install -r requirements.txt``` (note these requirements are different than those in the parent directory for the full EscapeHub server).

### Connecting and Registering

The client device must connect to the EscapeHub and then register itself along with relevant details such as the name and status of the device along with any actions (actions which can be triggered from the EscapeHub).

The connection URI will be a WebSocket URI and is to the web root of the EscapeHub ```/connect``` so for example if the EscapeHub is running on localhost port 8000 the URI would be ```ws://localhost:8000/connect```.

A dictionary should be created (and can be updated as needed) containing the salient information about the device, for example:
```python
device = { # a dictionary containing our device details
    "room": "1", # ID of the room we are to register to
    "name": "Some Device", # display name of the device
    "status": "Waiting", # textual status for management display
    "actions": [ # list of actions (of empty list!)
        {
            "actionid": "ACTONE", # the ID we will receive for this action
            "name": "Action One", # friendly name for display in the hub
            "enabled": True # is this action currently available
        },
        {
            "actionid": "ACTTWO", 
            "name": "Action Two", 
            "enabled": False 
        }
    ]
}
```

If you have actions at this point you should define an action handler function (covered in a later section).

At this point you are ready to (1) create an instance of the hub client, (2) connect the hub client to the remote EscapeHub server, and (3) register your device to the server.

To create an instance of the hub client:
```python
hub = hubclient()
```

And then to connect:
```python
huburi = "ws://localhost:8000/connect" # URI of the EscapeHub WS service
hub.Connect(huburi)
```

And finally, once we have defined our ```device``` dict containing the details, to register:
```python
myid = hub.Register(device)
```

The ID returned is your unique device connection ID (UUID). You do not need to save this as the hub client will remember it and use it automatically in future communications with the server.

You are now free to continue your program, the hub client will continue to run in the background as long as your code is executing (when your code exits the threads connecting to the Escape Hub will exit and the connections will close).

### Updating

If you need to update your device details you can simply construct a new device dict (or update the existing one) and then call ```hub.Update(device)``` (passing in your updated dict, in this case called ```device```).

### Actions

Actions can be registered with Escape Hub. These have an ID and a flag to show if they are enabled or not. If enabled, actions can be trigged from Escape Hub (for example through the web interface or an API call) and are for example intended for room operators to be able to manually trigger specific actions.

You may wish to have actions to solve certain puzzles or reset to game-ready condition etc.

To receive an action you must have registered actions (or updated them into existance) using ```Register``` and/or ```Update``` function calls as detailed above. You must also create a function which is the event handler and will be called when an action is received.

This function must take one parameter which is the action ID and must be set as the handler ```hub.actionHandler```.

For example to create an action handler function:
```python
def ActionHandler(actionid): # handler when we receive an action for us
    print("Action handler for ID "+actionid)
    # for the demo we will toggle i.e. ACTONE will disable ONE and enable TWO and vice-versa
    if actionid == "ACTONE":
        device['actions'][0]['enabled'] = False
        device['actions'][1]['enabled'] = True
    elif actionid == "ACTTWO":
        device['actions'][1]['enabled'] = False
        device['actions'][0]['enabled'] = True
    else:
        print("Unknown action") # useful for debug
    # and we update this state i.e. push it back to the hub
    hub.Update(device)
```

And then to register ```ActionHandler()``` as the event handler:
```python
hub.actionHandler = ActionHandler
```

### Misc

A debug flag can be set which will output low-level information from the client and the websocket library using the hubclient ```setDebug()``` method.

## An Example Client using hubclient

```python
"""
Escape-hub demo client
"""

import time

from hubclient import hubclient

huburi = "ws://localhost:8000/connect" # URI of the EscapeHub WS service
device = { # a dictionary containing our device details
    "room": "1", # ID of the room we are to register to
    "name": "Some Device", # display name of the device
    "status": "Waiting", # textual status for management display
    "actions": [ # list of actions (of empty list!)
        {
            "actionid": "ACTONE", # the ID we will receive for this action
            "name": "Action One", # friendly name for display in the hub
            "enabled": True # is this action currently available
        },
        {
            "actionid": "ACTTWO", 
            "name": "Action Two", 
            "enabled": False 
        }
    ]
}

def ActionHandler(actionid): # handler when we receive an action for us
    print("Action handler for ID "+actionid)
    # for the demo we will toggle i.e. ACTONE will disable ONE and enable TWO and vice-versa
    if actionid == "ACTONE":
        device['actions'][0]['enabled'] = False
        device['actions'][1]['enabled'] = True
    elif actionid == "ACTTWO":
        device['actions'][1]['enabled'] = False
        device['actions'][0]['enabled'] = True
    else:
        print("Unknown action") # useful for debug
    # and we update this state i.e. push it back to the hub
    hub.Update(device)

hub = hubclient() # the instance of the hubclient

hub.setDebug(True) # will output LOTS to the console

hub.actionHandler = ActionHandler # assign the function above to handle (receive) actions for us

print("Startup")

print("Connecting to EscapeHub via "+huburi)

hub.Connect(huburi)

print("Registering Device")
myid = hub.Register(device)


while True: # infinite loop for our device logic
    time.sleep(0.05)
```