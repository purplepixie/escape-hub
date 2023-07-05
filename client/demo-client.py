"""
This file is part of escape-hub.

Escape-hub is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

Escape-hub is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with escape-hub. If not, see <https://www.gnu.org/licenses/>.

Escape-hub is Copyright (C) 2023 David Cutting (dcutting@purplepixie.org; http://purplepixie.org/dave; http://davecutting.uk), all rights reserved.
"""

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