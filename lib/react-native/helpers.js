import base64 from "react-native-base64";
import CryptoJS from "crypto-js";
import bigInt from "big-integer";
import RNFS from 'react-native-fs';
import fernet from "fernet";
const HOST = "https://sampw-password-manager.herokuapp.com";
const UNAME_PATH = RNFS.DocumentDirectoryPath + "/.uname"

async function post(url, data) {
    return await fetch(url, { method: "POST", body: JSON.stringify(data) })
}

async function userExists(uname) {
    const r = await fetch(`${HOST}/userExists/${sha256(uname)}`);
    return (await r.text()) == "yes"
}

async function createUser(uname, pswd) {
    const data = { pswd };
    const r = await post(`${HOST}/createUser/${sha256(uname)}`, data);
    return await r.text();
}

async function checkMainPswd(uname, pswd) {
    const data = { pswd };
    const r = await post(`${HOST}/checkMainPswd/${sha256(uname)}`, data);
    return await r.text();
}

async function getPswdsDoc(uname, pswd) {
    const data = { pswd };
    const r = await post(`${HOST}/getPswdsDoc/${sha256(uname)}`, data);
    const t = await r.text();
    try {
        return JSON.parse(t);
    } catch {
        return t;
    }
}

async function setPswdsDoc(uname, pswd, toSet) {
    const data = { pswd, toSet };
    const r = await post(`${HOST}/setPswdsDoc/${sha256(uname)}`, data);
    return await r.text();
}

async function setServiceList(uname, pswd, toSet) {
    const data = { pswd, toSet };
    const r = await post(`${HOST}/setServiceList/${sha256(uname)}`, data);
    return await r.text();

}

async function getPswd(uname, pswd, service) {
    const data = { pswd, service };
    const r = await post(`${HOST}/getPswd/${sha256(uname)}`, data);
    const t = await r.text();
    try {
        return JSON.parse(t);
    } catch {
        return t;
    }
}

async function setPswd(uname, pswd, service, toSet, encService) {
    const data = { pswd, service, toSet, encService };
    const r = await post(`${HOST}/setPswd/${sha256(uname)}`, data);
    return await r.text();
}

async function delPswd(uname, pswd, service) {
    const data = { pswd, service };
    const r = await post(`${HOST}/delPswd/${sha256(uname)}`, data);
    return await r.text();
}

async function getServices(uname, pswd) {
    data = { pswd };
    const r = await post(`${HOST}/getServiceList/${sha256(uname)}`, data);
    const t = await r.text();
    try {
        return JSON.parse(t);
    } catch {
        return t;
    }
}

async function resetMainPswd(uname, pswd, toSet) {
    const data = { pswd, toSet };
    const r = await post(`${HOST}/resetMainPswd/${sha256(uname)}`, data);
    return await r.text()
}

async function dropUser(uname, pswd) {
    const data = { pswd };
    const r = await post(`${HOST}/dropUser/${sha256(uname)}`, data);
    return await r.text();
}

async function getUname() {
    if (await RNFS.exists(UNAME_PATH)) {
        return await RNFS.readFile(UNAME_PATH);
    } else {
        return "file does not exist"
    }
}

function setUname(uname) {
    RNFS.writeFile(UNAME_PATH, uname);
}

function delUname() {
    RNFS.unlink(UNAME_PATH);
}

function sha256(text) {
    return CryptoJS.SHA256(text).toString();
}

function titleCase(text) {
    return text
        .split(' ')
        .map(s => s.charAt(0).toUpperCase() + s.substring(1))
        .join(' ');
}

function get_hexdigest(salt, plaintext) {
    return sha256(salt + plaintext)
}


const SECRET_KEY = "something like SUPER DUPER secret";


function make_password(plaintext, service) {
    salt = get_hexdigest(SECRET_KEY, service)
    hsh = get_hexdigest(salt, plaintext)
    return salt + hsh
}

ALPHABET = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()-_".split("");

function password(plaintext, service) {
    const raw_hexdigest = make_password(plaintext, service);
    let num = bigInt(raw_hexdigest, 16);
    const num_chars = ALPHABET.length;
    const chars = [];
    while (chars.length < 30) {
        const idx = num.mod(num_chars);
        num = num.divide(num_chars);
        chars.push(ALPHABET[idx.toJSNumber()])
    }
    return chars.join("");
}

function encPswd(service, toSet, mainPswd) {
    let bEncer = password(mainPswd, service);
    bEncer = new fernet.Secret(base64.encode(bEncer.padEnd(32, String.fromCharCode(0))));
    let encrypted = {}
    for (let key in toSet) {
        const encer = new fernet.Token({
            secret: bEncer
        });
        encrypted[key] = encer.encode(toSet[key]);
    }
    return encrypted
}

function dencPswd(service, encrypted, mainPswd) {
    let bEncer = password(mainPswd, service);
    bEncer = new fernet.Secret(base64.encode(bEncer.padEnd(32, String.fromCharCode(0))));
    let decrypted = {}
    for (let key in encrypted) {
        const encer = new fernet.Token({
            secret: bEncer,
            token: encrypted[key],
            ttl: 0
        });
        decrypted[key] = encer.decode();
    }
    return decrypted;
}

function encService(service, mainPswd) {
    let bEncer = password(mainPswd, SECRET_KEY);
    bEncer = new fernet.Secret(base64.encode(bEncer.padEnd(32, String.fromCharCode(0))));
    const encer = new fernet.Token({
        secret: bEncer,
    });
    return encer.encode(service)
}

function dencService(service, mainPswd) {
    let bEncer = password(mainPswd, SECRET_KEY);
    bEncer = new fernet.Secret(base64.encode(bEncer.padEnd(32, String.fromCharCode(0))));
    const encer = new fernet.Token({
        secret: bEncer,
        token: service,
        ttl: 0
    });

    return encer.decode();
}

function encMainPswd(mainPswd) {
    return sha256(password(mainPswd, SECRET_KEY));
}

module.exports = {
    userExists,
    createUser,
    checkMainPswd,
    getPswdsDoc,
    setPswdsDoc,
    setServiceList,
    getPswd,
    setPswd,
    delPswd,
    getServices,
    resetMainPswd,
    dropUser,
    getUname,
    setUname,
    delUname,
    sha256,
    titleCase,
    encPswd,
    dencPswd,
    encService,
    dencService,
    encMainPswd
};