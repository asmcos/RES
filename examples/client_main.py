
import sys
import os

src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../src'))
modules_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../modules'))
sys.path.append(src_path)
sys.path.append(modules_path)

import res_client
import res_requests as requests

def main(sio):
    
    print("start client main")
    requests.server.sio = sio

    requests.server.apply()
    
    ret = requests.server.get("https://bing.com")
    print(ret.status_code)

res_client.start ( main )
