#
# 管理中心，负责其他节点的链接和客户端的连接
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

# 节点列表 ，负责可以提供服务的节点列表
node_list   = {} 
client_list = {}

# 2024.9.22
port = 9022

sio = socketio.Server( cors_allowed_origins='*' )
# wrap with a WSGI application
app = socketio.WSGIApp(sio)
# PeerID
peerid = key.get_peerid()

#


@sio.event
def connect(sid, environ, auth):
    print('connect ', sid)



@sio.event
def disconnect(sid):
    print('disconnect ', sid)

@sio.event
def get_userid(sid,message):

    data = {"userid":str(sid)}
    sio.emit("userid",data,to=sid)

# message is PeerID
# 发起一个注册 
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
    sio.emit("register_client_callback","",to=sid)

# 注册一个节点
# 告诉系统我可以做中间节点,
# 中间节点可以帮助系统减轻消息转换的压力
# 
@sio.event
def register_node(sid,message):
    n = node_list.get(sid,{})
    n["server"] = message["server"]
    

    node_list[sid] = n

# client 获取一个节点让 用户链接
@sio.event
def get_anode(sid,message):
    #get a idle node
    for n in node_list.keys():
        v = node_list[n]
    data = {"node_server":v["server"]}

    sio.emit("get_node_callback",data,to=sid)    



def start ():
    print("Your PeerID is %s" % peerid)

    eventlet.wsgi.server(eventlet.listen(('', port)), app)


if __name__ == '__main__':

    start()
