#
# 安全通信和验证 管理
#


import os
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
import base64
import hashlib
import res_config


pri_file = res_config.user_path("~/.res/private_key.pem")

private_key    = None
public_key     = None
public_key_pem = None
peerid         = None

def create_key():
    # 生成私钥
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )



    # 序列化私钥
    private_key_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )

    with open(pri_file,"wb") as key_file:    
        key_file.write(private_key_pem)

    print("The system has created a private key file at %s.\nPlease do not delete it.\n" % pri_file)

def init_key():
    global private_key,public_key,peerid,public_key_pem

    if not os.path.isfile(pri_file):
         create_key ()

    with open(pri_file, "rb") as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=None,
            backend=default_backend()
        )



    # 生成公钥
    public_key = private_key.public_key()


    # 序列化私钥
    private_key_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )

    # 序列化公钥
    public_key_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    peerid= hashlib.sha256(public_key_pem).hexdigest() 

def public_key_load(pem):
    try:
        client_public = serialization.load_pem_public_key(
            pem.encode(),
            backend=default_backend()
        )
        return client_public
    except:
        return None

def get_peerid():
    return peerid

def get_public_key():
    return public_key_pem.decode("utf-8")


def sign(data):
    if isinstance(data,str):
        data = data.encode('utf-8')

    signature = private_key.sign(
        data,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    signature = base64.b64encode(signature).decode('utf-8')
    return signature 

def verify(pubkey,signature,data):
    signature  = base64.b64decode(signature)

    if isinstance(data,str):
        data = data.encode('utf-8')

    try:
        pubkey.verify(
            signature,
            data,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        
        return True
    except:
        return False

init_key()

