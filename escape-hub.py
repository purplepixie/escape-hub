"""
This file is part of escape-hub.

Escape-hub is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

Escape-hub is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with escape-hub. If not, see <https://www.gnu.org/licenses/>.

Escape-hub is Copyright (C) 2023 David Cutting (dcutting@purplepixie.org; http://purplepixie.org/dave; http://davecutting.uk), all rights reserved.
"""

"""
Escape-hub primary program.

Version 0.0.01
"""

from sanic import Sanic, Request, Websocket
from sanic.response import text
from sanic.response import json as sjson
import uuid
import copy
import json

# Global Set of Connections (WebSockets)
connections = {}

# Global Set of Data for Rooms (and Devices)
rooms = {}

# Main Connection Reference Dictionary - to deepcopy()
connectiondictionary = {
            "socket": False,
            "room": False,
            "subscribed": False
        }

# Default Room Dictionary - to deepcopy()
roomdictionary = {
    "name": "",
    "devices": {}
}

# Default Return Object - to deepcopy()
returnobject = {
    "error": False,
    "message": "",
    "data": {}
}

# Connection Handling
async def AddConnection(cuuid, cdict):
    connections.update({cuuid: cdict})
    print("Connecting "+cuuid+" making total of "+str(len(connections.keys())))

async def RemoveConnection(cuuid):
    connections.pop(cuuid)
    print("Removing "+cuuid+" making total of "+str(len(connections.keys())))

async def Receive(cuuid, data):
    try:
        print("RX "+cuuid+": "+data)
        sendbackj = Process(json.loads(data)) # returns a Sanic JSONResponse
        sendback = json.dumps(sendbackj.raw_body)
        print("Back from Process")
        print(sendback)
        await Send(cuuid, sendback)
    except Exception as ex:
        print("Exception in receive")
        template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        message = template.format(type(ex).__name__, ex.args)
        print(message)

async def Broadcast(data):
    uuids = list(connections.keys())
    for u in uuids:
        await Send(u, data)

async def Publish():
    uuids = list(connections.keys())
    for u in uuids:
        if connections[u]["subscribed"] is True:
            await Send(u, json.dumps(rooms))

async def Send(cuuid, data):
    try:
        print("TX '"+data+"' to WS "+cuuid)
        await connections[cuuid]["socket"].send(data)
    except Exception as e:
        print("TX Error Exception for WS "+cuuid)
        print(str(e))
        await RemoveConnection(cuuid)

# Room and Data Management
def AddRoom(ruuid, name):
    newroom = copy.deepcopy(roomdictionary)
    newroom['name']=name
    rooms.update({ruuid: newroom})
    return ruuid

def Process(reqjson):
    print("Process called for RX data packet")
    ret = copy.deepcopy(returnobject)

    if reqjson['action'] == 'status':
        ret['status'] = {
            "connections": str(len(connections.keys())),
            "rooms": str(len(rooms.keys()))
        }
        ret['data'] = rooms
        ret['message'] = "Status from Escape Hub"
    elif reqjson['action'] == 'register':
        if reqjson['room'] in rooms: # does the room exist for registration
            devid = str(uuid.uuid4())
            print("Registering new device for room "+reqjson['room']+" ID "+devid)
            rd = {}
            rd.update({"name": reqjson['name']})
            rd.update({"status": reqjson['status']})
            rd.update({"actions": reqjson['actions']})
              
            print("Updating room device list")
            rooms[reqjson['room']]['devices'].update({devid: rd})
            print(rooms)
            ret['deviceid'] = devid
            print(ret)
        else:
            print("Device attempted to register for non-existant room "+reqjson['room'])
            ret['error'] = True
            ret['message'] = "Room Does Not Exist"

    print("Process routine complete")
    return sjson(ret)

# Load Config
rf = open('config/rooms.json')
roomconfig = json.load(rf)
rf.close()
for r in roomconfig.keys():
    AddRoom(r, roomconfig[r])

# Sanic app
app = Sanic("EscapeHub")

@app.get("/")
async def main_page(request):
    return text("Hello from EscapeHub")

@app.get("/status")
async def status_page(request):
    t = "EscapeHub Status\n\nConnections: "+str(len(connections.keys()))+"\nRooms: "+str(len(rooms.keys()))
    return text(t)

@app.route("/api", methods=["POST","GET"])
async def api_handler(request):
    return Process(request.json)

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
