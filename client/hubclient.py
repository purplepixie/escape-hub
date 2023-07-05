
import websocket
import _thread
import time
import rel
import json
import threading

class hubclient:

    def __init__(self):
        self.ws = False # websocket object
        self.dev = False # development mode (debug output)
        self.registered = False # once registered we pass everything to the callback
        self.myid = False # for remote ID of device
        self.wst = False # WS Thread 
        self.sct = False # Our SystemConnect Thread
        self.quit = False # Indication to quit and close down

        self.actionHandler = False # the function to handle actions for us

    def Debug(self,str):
        if self.dev is True:
            print("HubClient: "+str)

    def Connect(self, uri): # wrapper to connect starting thread
        self.sct = threading.Thread(target=self.SystemConnect, args=(uri,))
        self.sct.daemon = True
        self.sct.start()
        time.sleep(0.5)
    
    def setDebug(self, d):
        if d:
            websocket.enableTrace(True)
        else:
            websocket.enableTrace(False)
        self.dev = d

    def SystemConnect(self, uri):
        self.Debug("Connecting to "+uri)
        #websocket.enableTrace(True)
        self.ws = websocket.WebSocketApp(
            uri,
            on_open=self.on_open,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close
        )
        #self.ws.run_forever(dispatcher=rel, reconnect=5)  
        #rel.signal(2, rel.abort)  # Keyboard Interrupt
        #rel.dispatch()
        self.wst = threading.Thread(target=self.ws.run_forever)
        self.wst.daemon = True
        self.wst.start()
        self.Debug("Connected")
        while not self.quit:
            message = ws.recv()
            print("RX: "+message)
    
    def on_open(self,ws):
        self.Debug("WS reports connected")
    
    def on_error(self, ws, error):
        print("WS Error: "+error)
        self.Debug("WS Error: "+error)
    
    def on_close(self, ws, close_status_code, close_msg):
        self.Debug("WS Close, code: "+str(close_status_code)+", msg: "+close_msg)
    
    def on_message(self, ws, message):
        self.Debug("WS Message RX: "+message)
        try:
            m = json.loads(message)
            if self.registered is False:
                if "deviceid" in m: # registration message
                    self.myid = m["deviceid"]
                    self.registered = True
                    self.Debug("Device registered with ID "+self.myid)
            else: # we are registered
                self.Debug("Received "+message)
                # Processing options for RX
                # Action
                if "action" in m and m['action'] == 'action' and "deviceid" in m and m['deviceid'] == self.myid and "actionid" in m:
                    self.Debug("Valid action received actionid: "+m['actionid'])
                    # call action handler
                    if callable(self.actionHandler):
                        self.actionHandler(m['actionid'])
                    else:
                        self.Debug("Action received but no valid handler registered")
                elif "error" in m and m['error'] is False and "deviceid" in m and m['deviceid'] == self.myid and "message" in m: # generic message to me (i.e. ACK)
                    self.Debug("Message: "+m['message'])
                else: # unknown data
                    self.Debug("Unknown or invalid data received")
        except Exception as e:
            print("** EXCEPTION **")
            print(e)

    def Register(self, data):
        data.update({"action":"register"})
        self.Debug("Registering Device")
        self.ws.send(json.dumps(data))
    
    def Update(self, data):
        data.update({"action":"update"})
        data.update({"deviceid": self.myid})
        self.ws.send(json.dumps(data))