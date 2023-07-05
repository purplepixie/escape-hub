# escape-hub Escape Room Hub Coordinator

## Installation and Execution

Install the python requirements: ```pip install -r requirements.txt```

Start the hub: ```sanic escape-hub```

Note you may need to use ```pip3``` and ```python3``` commands dependent on your setup (python 3 is required).

By default sanic will serve on ```127.0.0.1``` so only respond to requests from the local machine, you can add the switch ```--host=0.0.0.0``` to the sanic command to listen and serve all interfaces. Also ```--debug``` is useful to see a lot of debug output.

# Interfacing with Escape Hub Directly (API or WebSocket)

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

# Using the hubclient Package
