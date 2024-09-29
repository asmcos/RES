import os
import json5
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
import hashlib

def user_path(name):
    t = os.path.expanduser(name)
    return os.path.normpath(t)

config_path = user_path("~/.res")
os.makedirs(config_path, exist_ok=True)

config_file = user_path("~/.res/config.json5")

config = None

def get_config():
    global config
    # 第N次获取
    if config != None:
        return config

    # 第一次获取
    if os.path.isfile(config_file):
        with open(config_file, 'r', encoding='utf-8') as f:
            try:
                config = json5.load(f)
            except:
                config = {}
            return config

    config = {}
    return config

def save_config(k,v):
    global config
    config = get_config()
    config[k] = v

    with open(config_file, 'w', encoding='utf-8') as f:
        json5.dump(config, f, indent=4)






