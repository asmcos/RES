#
# 节点, 负责客户端的连接和服务对接
#

import trio
import socketio
import eventlet
from threading import Lock,Thread
import threading
import sys,time,os
import json5
import res_config as config
import res_key  as key

#节点列表 ，负责可以提供服务的节点列表
node_list   = {} 
server_list = {}
client_list = {}

# 2024.9.26
port = 9026
serverip = "http://localhost"

sio = socketio.Server( cors_allowed_origins='*' )
# wrap with a WSGI application
app = socketio.WSGIApp(sio)
# PeerID
peerid = key.get_peerid()

#
nio = socketio.Client()
class connect_mserver():
    @nio.event
    def connect( ):
        print("connect to server ")
        nio.emit("get_userid","")

    @nio.event
    def userid(message):
        userid = message.get("userid")
        data = {"peerid":key.get_peerid(),
            "public_key":key.get_public_key(),
            "signature":key.sign(userid),
            "userid":userid}
        nio.emit("register_client",
                data)
    @nio.event
    def register_client_callback(message):
        data = {"server":serverip + ":"  + str(port)}
        nio.emit("register_node",data)
        
nio.connect("http://localhost:9022/")


class node_server():
    @sio.event
    def connect(sid, environ, auth):
        print('a client connect ', sid)



    @sio.event
    def disconnect(sid):
        print('disconnect ', sid)

    @sio.event
    def get_userid(sid,message):

        data = {"userid":str(sid)}
        sio.emit("userid",data,to=sid)

    # message is PeerID
    # 告诉系统我是谁,我的公钥是什么?
    # 以便系统做安全验证

    @sio.event
    def register_client(sid,message):
        client_public_key_pem = message.get("public_key")
        signature             = message.get("signature")
        userid                = message.get("userid")
        client_public_key     = key.public_key_load(client_public_key_pem)
        ret = key.verify(client_public_key,signature,userid)
        if ret :
            client_list[sid] = {
                "peerid":message.get("peerid"),
                "public_key":message.get("public_key")
                }

        # 可以开始应用程序的工作了,链接工作已经完全就绪了
        sio.emit("register_client_callback","",to=sid)

    # client 将他能提供的服务 都告知管理系统
    # 以便提供给有需要的人

    @sio.event
    def register_server(sid,message):
        l = server_list.get(sid,[])
        l.append(message["type"])

        server_list[sid] = l

    @sio.event
    def apply(sid,message):
        t = message["type"]
        data = {"sid":"","type":t,"peerid":""}
        for sk in server_list.keys():
            sv = server_list[sk]
            if t in sv:
                data["sid"]  = sk
                data["type"] = t
                data["peerid"] = client_list[sk]["peerid"]
                break
            
        sio.emit("apply_callback",data,to=sid)

    @sio.event
    def exec_func(sid,message):
        for c in client_list.keys():
            p = client_list[c]
            if message["peerid"] == p["peerid"]:
                message["from_sid"]    = sid
                message["from_peerid"] = client_list[sid]["peerid"]
                sio.emit("exec_func",message,to=c)
    @sio.event
    def exec_ret(sid,message):
        for c in client_list.keys():
            ret = client_list[c]
            if message["peerid"] == ret["peerid"]:
                sio.emit("exec_ret",message,to=c)

def start ():
    print("Your PeerID is %s" % peerid)

    eventlet.wsgi.server(eventlet.listen(('', port)), app)


if __name__ == '__main__':

    start()
