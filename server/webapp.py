import pymongo
from flask import Flask, request
from json import loads, dumps
from hashlib import sha256 as _sha256
app = Flask(__name__)


def sha256(s):
    return _sha256(s.encode("utf-8")).hexdigest()

with open('config.json', 'r') as f:
    config = loads(f.read())
    print(config)

client = pymongo.MongoClient("mongodb://{username}:{password}@{client}/{database}".format(**config))
db = client[config['database']]
col = db['passwords']
print(col)
serviceHash = sha256("service list")
mainHash = sha256("mainPswd")


@app.route("/userExists/<uname>")
def userExists(uname):
    if col.find_one({"_id": uname}):
        return "yes"
    return "no"


@app.route("/createUser/<uname>", methods=["POST"])
def createUser(uname):
    data = loads(request.data)
    newDoc = {}
    newDoc["_id"] = uname
    newDoc[serviceHash] = []
    newDoc[mainHash] = data["pswd"]
    col.insert(newDoc)
    return "success"


def checkMainPswdHelper(uname, pswd):
    doc = col.find_one({"_id": uname})
    if doc:
        realPswd = doc[mainHash]
        if realPswd == pswd:
            return "success"
        else:
            return "failure"
    else:
        return "user not in database"


@app.route("/checkMainPswd/<uname>", methods=["POST"])
def checkMainPswd(uname):
    data = loads(request.data)
    return checkMainPswdHelper(uname, data['pswd'])


@app.route("/getPswdsDoc/<uname>", methods=["POST"])
def getPswdsDoc(uname):
    data = loads(request.data)
    result = checkMainPswdHelper(uname, data["pswd"])
    if result == "success":
        pswdsDoc = col.find_one({"_id": uname})
        del pswdsDoc["_id"]
        del pswdsDoc[mainHash]
        return dumps(pswdsDoc)
    return result


@app.route("/setPswdsDoc/<uname>", methods=["POST"])
def setPswdsDoc(uname):
    data = loads(request.data)
    result = checkMainPswdHelper(uname, data["pswd"])
    if result == "success":
        newDoc = data["toSet"]
        newDoc["_id"] = uname
        newDoc[mainHash] = data["pswd"]
        col.replace_one({"_id": uname}, newDoc)
    return result


@app.route("/getServiceList/<uname>", methods=["POST"])
def getServiceList(uname):
    data = loads(request.data)
    result = checkMainPswdHelper(uname, data["pswd"])
    if result == "success":
        pswdsDoc = col.find_one({"_id": uname})
        return dumps(pswdsDoc[serviceHash])
    return result


@app.route("/setServiceList/<uname>", methods=["POST"])
def setServiceList(uname):
    data = loads(request.data)
    result = checkMainPswdHelper(uname, data["pswd"])
    if result == "success":
        col.update_one({"_id": uname}, {
            "$set": {serviceHash: data["toSet"]}})
    return result


@app.route("/getPswd/<uname>", methods=["POST"])
def getPswd(uname):
    data = loads(request.data)
    result = checkMainPswdHelper(uname, data["pswd"])
    if result == "success":
        pswdsDoc = col.find_one({"_id": uname})
        if data["service"] in pswdsDoc:
            return dumps(pswdsDoc[data["service"]])
        else:
            return "password doesn't exist"
    return result


@app.route("/setPswd/<uname>", methods=["POST"])
def setPswd(uname):
    data = loads(request.data)
    result = checkMainPswdHelper(uname, data["pswd"])
    if result == "success":
        col.update_one({"_id": uname}, {"$set": {
            data["service"]: data["toSet"]}, "$push": {serviceHash: data['encService']}})
    return result


@app.route("/delPswd/<uname>", methods=["POST"])
def delPswd(uname):
    data = loads(request.data)
    result = checkMainPswdHelper(uname, data["pswd"])
    if result == "success":
        pswdsDoc = col.find_one({"_id": uname})
        if data["service"] not in pswdsDoc:
            return "password doesn't exist"
        col.update_one({"_id": uname}, {
            "$unset": {data["service"]: ""}})
    return result


@app.route("/getServices/<uname>", methods=["POST"])
def getServices(uname):
    data = loads(request.data)
    result = checkMainPswdHelper(uname, data["pswd"])
    if result == "success":
        pswdsDoc = col.find_one({"_id": uname})
        return dumps(pswdsDoc[serviceHash])
    return result


@app.route("/resetMainPswd/<uname>", methods=["POST"])
def resetMainPswd(uname):
    data = loads(request.data)
    result = checkMainPswdHelper(uname, data["pswd"])
    if result == "success":
        col.update_one({"_id": uname}, {
            "$set": {mainHash: data["toSet"]}})
    return result


@app.route("/dropUser/<uname>", methods=["POST"])
def dropUser(uname):
    data = loads(request.data)
    result = checkMainPswdHelper(uname, data["pswd"])
    if result == "success":
        col.remove({"_id": uname})
    return result
