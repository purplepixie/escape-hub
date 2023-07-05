"""
This file is part of escape-hub.

Escape-hub is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

Escape-hub is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with escape-hub. If not, see <https://www.gnu.org/licenses/>.

Escape-hub is Copyright (C) 2023 David Cutting (dcutting@purplepixie.org; http://purplepixie.org/dave; http://davecutting.uk), all rights reserved.
"""

"""
Echo test with WS and Sanic.

"""

from sanic import Sanic, Request, Websocket
from sanic.response import text
from sanic.response import json as sjson
import uuid
import copy
import json

# Global Set of Connections (WebSockets)
connections = {}

# Main Connection Reference Dictionary - to deepcopy()
connectiondictionary = {
            "socket": False,
            "room": False,
            "subscribed": False
        }

# Connection Handling
async def AddConnection(cuuid, cdict):
    connections.update({cuuid: cdict})
    print("Connecting "+cuuid+" making total of "+str(len(connections.keys())))

async def RemoveConnection(cuuid):
    connections.pop(cuuid)
    print("Removing "+cuuid+" making total of "+str(len(connections.keys())))

async def Receive(cuuid, data):
    print("RX "+cuuid+": "+data)
    await Broadcast(data)

async def Broadcast(data):
    uuids = list(connections.keys())
    for u in uuids:
        await Send(u, data)

async def Send(cuuid, data):
    try:
        print("TX '"+data+"' to WS "+cuuid)
        await connections[cuuid]["socket"].send(data)
    except Exception as e:
        print("TX Error Exception for WS "+cuuid)
        print(str(e))
        await RemoveConnection(cuuid)



# Sanic app
app = Sanic("EscapeHub")

@app.get("/")
async def main_page(request):
    return text("Hello from Echo Server")

@app.websocket("/connect")
async def connect(request: Request, ws: Websocket):
    myuuid = str(uuid.uuid4())
    try:
        connectiondict = copy.deepcopy(connectiondictionary)
        connectiondict["socket"]=ws
        await AddConnection(myuuid, connectiondict)
        while True:
            data = await ws.recv()
            await Receive(myuuid, data)
    except Exception as e:
        print("WS "+myuuid+" exception, removing")
        print(e)
        await RemoveConnection(myuuid)
