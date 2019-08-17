from hashlib import sha256 as _sha256
from cryptography.fernet import Fernet
import base64
from requests import post, get
from json import dumps, loads, JSONDecodeError
import os

##Change this if you are creating your own server and mongodb
HOST = "https://sampw-password-manager.herokuapp.com"


def sha256(s):
    return _sha256(s.encode('utf-8')).hexdigest()


def userExists(uname):
    r = get(f"{HOST}/userExists/{sha256(uname)}")
    return r.text == "yes"


def createUser(uname, pswd):
    data = {
        "pswd": pswd
    }
    r = post(f"{HOST}/createUser/{sha256(uname)}", data=dumps(data))
    return r.text


def checkMainPswd(uname, pswd):
    data = {
        "pswd": pswd
    }
    r = post(f"{HOST}/checkMainPswd/{sha256(uname)}", data=dumps(data))
    return r.text


def getPswdsDoc(uname, pswd):
    data = {
        "pswd": pswd
    }
    r = post(f"{HOST}/getPswdsDoc/{sha256(uname)}", data=dumps(data))
    try:
        return loads(r.text)
    except JSONDecodeError:
        return r.text


def setPswdsDoc(uname, pswd, toSet):
    data = {
        "pswd": pswd,
        "toSet": toSet
    }
    r = post(f"{HOST}/setPswdsDoc/{sha256(uname)}", data=dumps(data))
    return r.text


def setServiceList(uname, pswd, toSet):
    data = {
        "pswd": pswd,
        "toSet": toSet
    }
    r = post(f"{HOST}/setServiceList/{sha256(uname)}", data=dumps(data))
    return r.text


def getPswd(uname, pswd, service):
    data = {
        "pswd": pswd,
        "service": service
    }
    r = post(f"{HOST}/getPswd/{sha256(uname)}", data=dumps(data))
    try:
        return loads(r.text)
    except JSONDecodeError:
        return r.text

def setPswd(uname, pswd, service, toSet, encService):
    data = {
        "pswd": pswd,
        "service": service,
        "toSet": toSet,
        "encService": encService
    }
    r = post(f"{HOST}/setPswd/{sha256(uname)}", data=dumps(data))
    return r.text


def delPswd(uname, pswd, service):
    data = {
        "pswd": pswd,
        "service": service,
    }
    r = post(f"{HOST}/delPswd/{sha256(uname)}", data=dumps(data))
    return r.text


def getServices(uname, pswd):
    data = {
        "pswd": pswd
    }
    r = post(f"{HOST}/getServices/{sha256(uname)}", data=dumps(data))
    try:
        return loads(r.text)
    except JSONDecodeError:
        return r.text


def resetMainPswd(uname, pswd, toSet):
    data = {
        "pswd": pswd,
        "toSet": toSet
    }
    r = post(f"{HOST}/resetMainPswd/{sha256(uname)}", data=dumps(data))
    return r.text


def dropUser(uname, pswd):
    data = {
        "pswd": pswd
    }
    r = post(f"{HOST}/dropUser/{sha256(uname)}", data=dumps(data))
    return r.text


def getUname():
    try:
        with open(os.path.expanduser('~/.uname'), "r") as f:
            return f.read()
    except FileNotFoundError:
        return "file does not exist"


def setUname(uname):
    with open(os.path.expanduser('~/.uname'), "w+") as f:
        f.write(uname)


def delUname():
    os.remove(os.path.expanduser('~/.uname'))


def get_hexdigest(salt, plaintext):
    return sha256(salt + plaintext)


SECRET_KEY = "something like SUPER DUPER secret"


def make_password(plaintext, service):
    salt = get_hexdigest(SECRET_KEY, service)
    hsh = get_hexdigest(salt, plaintext)
    return "".join((salt, hsh))


ALPHABET = ("abcdefghijklmnopqrstuvwxyz"
            "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
            "0123456789!@#$%^&*()-_")


def password(plaintext, service, length=30):
    raw_hexdigest = make_password(plaintext, service)
    # Convert the hexdigest into decimal
    num = int(raw_hexdigest, 16)
    # What base will we convert `num` into?
    num_chars = len(ALPHABET)
    # Build up the new password one "digit" at a time,
    # up to a certain length
    chars = []
    while len(chars) < length:
        num, idx = divmod(num, num_chars)
        chars.append(ALPHABET[idx])
    return "".join(chars)


def encPswd(service, toSet, mainPswd):
    bToSet = toSet.encode("utf-8")
    bEncer = password(mainPswd, service).encode("utf-8")
    encer = Fernet(base64.urlsafe_b64encode(
        bEncer + bytes(32-len(bEncer))))
    return encer.encrypt(bToSet).decode("utf-8")


def dencPswd(service, encrypted, mainPswd):
    bEncer = password(mainPswd, service).encode("utf-8")
    encer = Fernet(base64.urlsafe_b64encode(
        bEncer + bytes(32-len(bEncer))))
    return encer.decrypt(encrypted.encode("utf-8")).decode("utf-8")


def encService(service, mainPswd):
    bEncer = password(mainPswd, SECRET_KEY).encode("utf-8")
    encer = Fernet(base64.urlsafe_b64encode(
        bEncer + bytes(32-len(bEncer))))
    return encer.encrypt(service.encode("utf-8")).decode("utf-8")


def dencService(service, mainPswd):
    bEncer = password(mainPswd, SECRET_KEY).encode("utf-8")
    encer = Fernet(base64.urlsafe_b64encode(
        bEncer + bytes(32-len(bEncer))))
    return encer.decrypt(service.encode('utf-8')).decode('utf-8')


def encMainPswd(mainPswd):
    return sha256(password(mainPswd, SECRET_KEY))
