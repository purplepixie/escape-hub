/*****
 * An example rudimentary Escape Hub client in CPP using easywsclient (https://github.com/dhbaird/easywsclient)
 * 
 * Note: this is a very simple client using basic principles and could well do with "proper" JSON handling and connsistent messaging
*/

//#include "easywsclient.hpp"
#include "easywsclient.cpp" // <-- include only if you don't want compile separately
#ifdef _WIN32
#pragma comment( lib, "ws2_32" )
#include <WinSock2.h>
#endif
#include <assert.h>
#include <stdio.h>
#include <string>
#include <iostream>
#include <random>
#include <sys/time.h>

using easywsclient::WebSocket;
using namespace std;
static WebSocket::pointer websocket = NULL;

// default connection arguments and global variables
string url = "ws://localhost:8000/connect";
string roomid = "1";
string name = "DemoDevice";
string deviceid = ""; // my device ID once registered
string status = "Waiting"; // status to be passed around
bool registered = false;

void handle_message(const std::string & message)
{
    printf(">>> %s\n", message.c_str());
    // room here for Json decoding of any choice but brute for the moment!
    if (!registered) // this should be a registration message
    {
        cout << "Checking for registration message" << endl;
        std::size_t did = message.find("deviceid");
        cout << did << endl;
        if (did != std::string::npos) // was found
        {
            deviceid = message.substr(did+13, 36); // this is horrible hard coded but will work (until proper JSON parsing!)
            cout << "Registered with deviceid " << deviceid << endl;
            registered = true;
        }
    }
    else
    {
        // put the logic to deal with actions etc here!
    }
}

void send_message(WebSocket::pointer websocket, std::string message)
{
    printf("<<< %s\n", message.c_str());
    websocket->send(message);
}

// This will create a "nice" JSON key-value pair with necessary escaping
std::string kvpq(std::string k, std::string v)
{
    string s = "\"" + k + "\":\"" + v + "\"";
    return s;
}

int main(int ac, char** av)
{
#ifdef _WIN32
    INT rc;
    WSADATA wsaData;

    rc = WSAStartup(MAKEWORD(2, 2), &wsaData);
    if (rc) {
        printf("WSAStartup Failed.\n");
        return 1;
    }
#endif

    bool running = true;

    cout << "Intialising - reading arguments" << endl;

    for(int i=1; i<ac; i++)
    {
        string arg = std::string(av[i]);
        cout << arg << endl;
        if (arg == "--roomid")
        {
            roomid=av[++i];
        }
        else if (arg == "--url")
            url=av[++i];
        else if (arg == "--name")
            name=av[++i];
    }

    cout << "Initialsing" << endl;

    cout << "URL: " << url << " ROOM: " << roomid << endl;

    websocket = WebSocket::from_url(url);
    assert(websocket);

    // first we register
    string regmsg = "{" + kvpq("action","register") + ", " + kvpq("room", roomid) + ", " + kvpq("name",name) + "," + kvpq("status",status) + ", \"actions\": []}";
    send_message(websocket, regmsg);


    while (running && websocket->getReadyState() != WebSocket::CLOSED)
    {
        //cout << "Polling" << endl;
        websocket->poll();
        websocket->dispatch(handle_message);
        
    }
    cout << "Exiting" << endl;
    if (websocket->getReadyState() == WebSocket::CLOSED)
        cout << "Web Socket was closed (disconnect)" << endl;
    delete websocket;
#ifdef _WIN32
    WSACleanup();
#endif
    return 0;
}
