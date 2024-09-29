#
#
#

import sys
import os

src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../src'))
if src_path not in sys.path:
    sys.path.append(src_path)

import requests
from requests.models import Response

import res_register as reg
import threading
condition = threading.Condition()

class server:
    params = {"proto":["https","http"]}
    server_sid = ""
    server_peerid = ""
    sio = ""
    # 返回值队列
    responequeue = {}
    count = 0
    def __init__(self):
        pass

    @staticmethod
    def apply():
        data = {
                "type":reg.REQUESTS,
                "params":server.params
                }
        server.sio.emit("apply",data)
        with condition:
            condition.wait()

    @staticmethod
    def apply_callback(message):
        if message["sid"] != "":
            server.server_sid    = message["sid"]
            server.server_peerid = message["peerid"] 
        with condition:
            condition.notify()

    @staticmethod
    def get(*args,**kwargs):
        data = {}
        data["type"]     = reg.REQUESTS
        data["sid"]      = server.server_sid
        data["peerid"]   = server.server_peerid
        data["funcname"] = "get"
        data["args"]     = args
        data["kwargs"]   = kwargs
        data["order"]    = server.count
        server.count += 1
        server.sio.emit("exec_func",data)
        with condition:
            condition.wait()
        ret = server.responequeue[data["order"]]
        server.responequeue[data["order"]] = None
        return ret

    @staticmethod
    def post(*args,**kwargs):
        data = {}
        data["type"]     = reg.REQUESTS
        data["sid"]      = server.server_sid
        data["peerid"]   = server.server_peerid
        data["args"]     = args
        data["kwargs"]   = kwargs
        data["funcname"] = "post"
        data["order"]    = server.count
        server.count += 1
        server.sio.emit("exec_func",data)

    @staticmethod
    def exec_get(*args,**kwargs):
        ret = requests.get(*args,**kwargs)
        return ret

    @staticmethod
    def exec_post():
        pass

    @staticmethod
    def exec_func(message):
        if message["funcname"] == "get":
            ret = server.exec_get(*message["args"],**message["kwargs"])
            data = {"content":ret.content,
                    "status_code":ret.status_code,
                    "headers":dict(ret.headers)}

            data["type"]      = reg.REQUESTS
            data["sid"]       = message['from_sid']
            data["peerid"]    = message['from_peerid']
            data["funcname"]  = message["funcname"]
            data["order"]  = message["order"]

            server.sio.emit("exec_ret",data)

    @staticmethod
    def ret_func(message):
        if message["funcname"] == "get":
            ret = Response()
            ret.status_code = message["status_code"]
            ret._content = message["content"]
            ret.headers = message["headers"]
            
            server.responequeue[message["order"]] = ret
            with condition:
                condition.notify()


reg.server(reg.REQUESTS,server)


