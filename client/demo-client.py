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

hub = hubclient() # the instance of the hubclient

print("Startup")

print("Connecting to EscapeHub via "+huburi)

hubclient.Connect(hub,huburi)

print("Registering Device")
myid = hubclient.Register(hub,device)


while True: # infinite loop for our device logic
    time.sleep(0.05)