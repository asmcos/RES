import trio
import socketio
import eventlet
from threading import Lock,Thread
import threading
import sys,time,os
import json5
import res_config as config
import res_key as key
from   res_common import *
import sys
import os

modules_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../modules'))
sys.path.append(modules_path)
import load_modules 


mio = socketio.Client()
hostserver = 'http://localhost:9022' 
nserver = ''

nio = socketio.Client()

res_main = None

class manager_server():
    @mio.event
    def connect( ):
        print("connect to manager server.")
        mio.emit("get_userid","")

    @mio.event
    def disconnect( ):
        print('disconnect manager server')

    @mio.event
    def userid(message):
        userid = message.get("userid")
        data = {"peerid":key.get_peerid(),
            "public_key":key.get_public_key(),
            "signature":key.sign(userid),
            "userid":userid}
        mio.emit("register_client",
                data)
    @mio.event
    def register_client_callback(message):
        mio.emit("get_anode","")

    @mio.event
    def get_node_callback(message):

        #端开管理服务器链接
        mio.disconnect()

        nserver = message["node_server"]
        # 建立node 节点链接
        nio.connect(nserver)
        nio.wait()

class node_server():
    @nio.event
    def connect( ):
        print("connect to node server")
        load_modules.init()
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
        for s in server_list:
            nio.emit("register_server",{"type":s["type"]})
        if res_main:
            threading.Thread(target=res_main,args=(nio,)).start()

    @nio.event
    def apply_callback(message):
        t = message["type"]
        for s in server_list:
            if t == s["type"]:
                s["func"].apply_callback(message)
    @nio.event
    def exec_func(message):
        t = message["type"]
        for s in server_list:
            if t == s["type"]:
                s["func"].exec_func(message)
    @nio.event
    def exec_ret(message):
        t = message["type"]
        for s in server_list:
            if t == s["type"]:
                s["func"].ret_func(message)
        
        
def start(m = None):
    global res_main
    res_main = m

    mio.connect(hostserver)
    mio.wait()

if __name__ == "__main__":
    start()




