import React, { Component } from "react";
import { Text, Platform, Button, TextInput, View, Alert, Clipboard, Picker, ScrollView, TouchableWithoutFeedback } from "react-native";
import { CheckBox } from 'react-native-elements';
import helpers from "./helpers.js";

const alert = Alert.alert;
let MAIN_PSWD = "";
let SERVICES = [];
let logoutTimer;

class LoginLyt extends Component {
    constructor(props) {
        super(props);
        this.state = {
            username: "",
            mainPswd: ""
        };
    }

    render() {
        this.loadUname.bind(this)();
        return (
            <View style={{ flex: 1, justifyContent: "space-between", backgroundColor: "white" }}>
                <View style={{ flex: 1, backgroundColor: "white" }}>
                    <TextInput
                        style={{ height: 40 }}
                        value={this.state.username}
                        placeholder="Username"
                        autoCapitalize="none"
                        returnKeyType={"next"}
                        onChangeText={val => this.setState({ username: val })}
                        onSubmitEditing={() => this.mainPswd.focus()}
                    />
                    <TextInput
                        style={{ height: 40 }}
                        value={this.state.mainPswd}
                        ref={(input) => { this.mainPswd = input }}
                        placeholder="Main Password"
                        autoCapitalize="none"
                        onChangeText={val => this.setState({ mainPswd: val })}
                        onSubmitEditing={() => this.but.props.onPress()}
                        secureTextEntry={true}
                    />
                </View>
                <Button
                    title="Go!"
                    ref={(input) => { this.but = input }}
                    style={{ flex: 1 }}
                    onPress={this.go.bind(this)}
                />
            </View>
        )
    }

    async loadUname() {
        const uname = await helpers.getUname();
        if (uname != "file does not exist") {
            this.setState({ username: uname });
        }
    }

    async go() {
        const uname = this.state.username;
        const mainPswd = this.state.mainPswd;
        if (uname.length == 0) {
            alert("You must input your username!");
        } else if (await helpers.userExists(uname)) {
            if (mainPswd.length == 0) {
                alert("You must input your main password");
            } else {
                const resp = await helpers.checkMainPswd(uname, helpers.encMainPswd(mainPswd));
                if (resp == "failure") {
                    alert("That is not the correct main password");
                    this.setState({ mainPswd: "" });
                } else {
                    helpers.setUname(uname);
                    MAIN_PSWD = mainPswd;
                    if (logoutTimer) {
                        clearTimeout(logoutTimer);
                    }
                    logoutTimer = setTimeout(this.props.logout, 90000);
                    this.props.changePage("main");
                }
            }
        } else {
            alert(`The username ${uname} does not have an account associated with it`);
            this.setState({ username: "" });
        }
    }
}

class NewUserLyt extends Component {
    constructor(props) {
        super(props);
        this.state = {
            username: "",
            p1: "",
            p2: ""
        };
    }

    render() {
        return (
            <View style={{ flex: 1, justifyContent: "space-between", backgroundColor: "white" }}>
                <View style={{ flex: 1, backgroundColor: "white" }}>
                    <TextInput
                        style={{ height: 40 }}
                        value={this.state.username}
                        placeholder="Username"
                        autoCapitalize="none"
                        returnKeyType={"next"}
                        onChangeText={val => this.setState({ username: val })}
                        onSubmitEditing={() => this.p1.focus()}
                        blurOnSubmit={false}
                    />
                    <TextInput
                        style={{ height: 40 }}
                        value={this.state.p1}
                        ref={(input) => { this.p1 = input }}
                        placeholder="Main Password"
                        autoCapitalize="none"
                        returnKeyType={"next"}
                        onChangeText={val => this.setState({ p1: val })}
                        onSubmitEditing={() => this.p2.focus()}
                        secureTextEntry={true}
                        blurOnSubmit={false}
                    />
                    <TextInput
                        style={{ height: 40 }}
                        value={this.state.p2}
                        ref={(input) => { this.p2 = input }}
                        placeholder="Confirm Password"
                        autoCapitalize="none"
                        onChangeText={val => this.setState({ p2: val })}
                        onSubmitEditing={() => this.but.props.onPress()}
                        secureTextEntry={true}
                    />
                </View>
                <Button
                    title="Go!"
                    ref={(input) => { this.but = input }}
                    style={{ flex: 1 }}
                    onPress={this.go.bind(this)}
                />
            </View>
        )
    }

    async go() {
        const uname = this.state.username;
        const p1 = this.state.p1;
        const p2 = this.state.p2;
        if (p1 != p2) {
            alert("The two passwords don't match");
            this.setState({ p1: "", p2: "" });
        } else if (p1.length == 0) {
            alert("You must input a main password");
        } else if (await helpers.userExists(uname)) {
            alert(`The username ${uname} is already in use`);
            this.setState({ username: "" });
        } else {
            helpers.createUser(uname, helpers.encMainPswd(p2));
            helpers.setUname(uname);
            MAIN_PSWD = p1;
            if (logoutTimer) {
                clearTimeout(logoutTimer);
            }
            logoutTimer = setTimeout(this.props.logout, 90000);
            alert("Your account has been created");
            this.props.changePage("main");
        }
    }
}

class ManagePswdsLyt extends Component {
    constructor(props) {
        super(props);
        this.state = {
            services: false,
            service: ""
        };
        setTimeout(() => {
            this.textChanged.bind(this)("");
        }, 10);
    }

    render() {
        return (
            <View style={{ flex: 1, justifyContent: "space-between", backgroundColor: "white" }}>
                <View style={{ flex: 1, backgroundColor: "white" }}>
                    <TextInput
                        style={{ height: 40 }}
                        value={this.state.service}
                        ref={(input) => { this.service = input }}
                        placeholder="Service Name"
                        onChangeText={this.textChanged.bind(this)}
                        autoCapitalize="words"
                        onSubmitEditing={() => this.but.props.onPress()}
                    />
                    <ScrollView
                        style={{ flex: 1 }}
                        ref={(input) => { this.scroller = input }}>
                        {this.state.services}
                    </ScrollView>
                </View>
                <Button
                    title="Go!"
                    ref={(input) => { this.but = input }}
                    style={{ flex: 1 }}
                    onPress={this.go.bind(this)}
                />
            </View>
        )
    }

    async textChanged(text) {
        this.setState({ service: text });
        let s1 = SERVICES.slice(0);
        s1.sort();
        s1 = [...new Set(s1
            .filter(service => service.toLowerCase().startsWith(text.toLowerCase()))
            .map(service => helpers.titleCase(service)))];
        let textServices = [];
        for (let i = 0; i < s1.length; i++) {
            let service = s1[i];
            async function onClick() {
                let pswd = await getPswd(service.toLowerCase(), MAIN_PSWD);
                this.props.options(service, pswd);
            }
            textServices.push(
                <Text key={i} onPress={onClick.bind(this)} style={{ fontSize: 20 }}>
                    {"• " + service}
                </Text>
            )
        }
        this.setState({ services: textServices });
        return textServices;
    }

    async go() {
        let service = this.state.service
        let pswd = await getPswd(service.toLowerCase(), MAIN_PSWD);
        if (pswd == "password doesn't exist") {
            if (this.state.services.length > 0) {
                service = this.state.services[0].substring(2);
                let pswd = await getPswd(service.toLowerCase(), MAIN_PSWD);
                this.props.options(service, pswd);
            } else {
                alert(`Would you like to set a username for ${service}`, "", [
                    { text: "No", onPress: () => this.props.setPswd1(service) },
                    { text: "Yes", onPress: () => this.props.setPswd2(service) }
                ], { cancelable: false });

            }
        } else {
            this.props.options(service, pswd);
        }
    }

}

class OptionsLyt extends Component {
    constructor(props) {
        super(props);
        this.state = {
            newPswd: ""
        };
    }

    render() {
        return (
            <View style={{ flex: 1, justifyContent: "space-between", backgroundColor: "white" }}>
                <Text style={{ fontSize: 20, marginTop: 30 }}>
                    {'uname' in this.props.pswd ? `Your username for ${this.props.service} is ${this.props.pswd.uname}\nYour password for ${this.props.service} is ${this.props.pswd.pswd}` : `Your password for ${this.props.service} is ${this.props.pswd.pswd}. (You don't have a username set)`}
                </Text>
                <Button
                    title="Copy password to clipboard"
                    style={{ flex: 1 }}
                    onPress={this.copy.bind(this)}
                />
                <Button
                    title="Change password"
                    style={{ flex: 1 }}
                    ref={(input) => { this.but = input }}
                    onPress={this.change.bind(this)}
                />
                <Button
                    title="Delete password"
                    style={{ flex: 1 }}
                    onPress={this.delete.bind(this)}
                />
                <Button
                    title="Exit"
                    style={{ flex: 1 }}
                    onPress={this.exit.bind(this)}
                />
            </View>)
    }

    copy() {
        Clipboard.setString(this.props.pswd.pswd);
        this.props.changePage("main");
    }

    change() {
        alert(`Would you like to set a username for ${service}`, "", [
            { text: "No", onPress: () => this.props.setPswd1(service) },
            { text: "Yes", onPress: () => this.props.setPswd2(service) }
        ], { cancelable: false });
    }

    delete() {
        alert("Are you sure you want to delete this password?", "", [
            { text: "No", onPress: () => { } },
            {
                text: "Yes", onPress: async () => {
                    resp = await delPswd(this.props.service.toLowerCase(), MAIN_PSWD)
                    if (resp == "success") {
                        alert(`Password deleted`);
                        this.props.changePage("main");
                    } else {
                        alert("There was a problem deleting your password:" + resp);
                        this.props.changePage("main");
                    }
                }
            }
        ], { cancelable: false });
    }

    exit() {
        this.props.changePage("main");
    }
}

class SetPswdLyt1 extends Component {
    constructor(props) {
        super(props);
        this.state = {
            pswd: ""
        };
    }

    render() {
        return (
            <View style={{ flex: 1, justifyContent: "space-between", backgroundColor: "white" }}>
                <View style={{ flex: 1, backgroundColor: "white" }}>
                    <Text style={{ fontSize: 20, marginTop: 30 }}>
                        Set password for {this.props.service}
                    </Text>
                    <TextInput
                        style={{ height: 40 }}
                        value={this.state.pswd}
                        ref={(input) => { this.pswd = input }}
                        onChangeText={val => this.setState({ pswd: val })}
                        placeholder="Password for service"
                        autoCapitalize="none"
                        secureTextEntry={true}
                        returnKeyType={"next"}
                        onSubmitEditing={() => this.but.props.onPress()}
                        blurOnSubmit={false}
                    />
                </View>
                <View style={{
                    flex: 1,
                    flexDirection: 'row',
                    justifyContent: 'space-between'
                }}>
                    <Button
                        title="Cancel"
                        style={{ flex: 1 }}
                        onPress={() => this.props.changePage("main")}
                    />
                    <Button
                        title="Go!"
                        ref={(input) => { this.but = input }}
                        style={{ flex: 1 }}
                        onPress={this.go.bind(this)}
                    />
                </View>
            </View>
        )
    }

    async go() {
        const service = this.props.service;
        const toSet = this.state.pswd;
        if (toSet.length == 0) {
            alert("You must input a password")
        } else {
            if (await setPswd(service.toLowerCase(), MAIN_PSWD, { pswd: toSet }) == "success") {
                alert(`Password for ${service} successfully set to ${toSet}`)
                this.props.changePage("main");
            } else {
                alert("There was a problem setting your password")
            }
        }
    }
}

class SetPswdLyt2 extends Component {
    constructor(props) {
        super(props);
        this.state = {
            uname: "",
            pswd: ""
        };
    }

    render() {
        return (
            <View style={{ flex: 1, justifyContent: "space-between", backgroundColor: "white" }}>
                <View style={{ flex: 1, backgroundColor: "white" }}>
                    <Text style={{ fontSize: 20, marginTop: 30 }}>
                        Set username and password for {this.props.service}
                    </Text>
                    <TextInput
                        style={{ height: 40 }}
                        value={this.state.uname}
                        ref={(input) => { this.uname = input }}
                        onChangeText={val => this.setState({ uname: val })}
                        placeholder="Username for service"
                        autoCapitalize="none"
                        secureTextEntry={true}
                        returnKeyType={"next"}
                        onSubmitEditing={() => this.pswd.focus()}
                        blurOnSubmit={false}
                    />
                    <TextInput
                        style={{ height: 40 }}
                        value={this.state.pswd}
                        ref={(input) => { this.pswd = input }}
                        onChangeText={val => this.setState({ pswd: val })}
                        placeholder="Password for service"
                        autoCapitalize="none"
                        secureTextEntry={true}
                        returnKeyType={"next"}
                        onSubmitEditing={() => this.but.props.onPress()}
                        blurOnSubmit={false}
                    />
                </View>
                <View style={{
                    flex: 1,
                    flexDirection: 'row',
                    justifyContent: 'space-between'
                }}>
                    <Button
                        title="Cancel"
                        style={{ flex: 1 }}
                        onPress={() => this.props.changePage("main")}
                    />
                    <Button
                        title="Go!"
                        ref={(input) => { this.but = input }}
                        style={{ flex: 1 }}
                        onPress={this.go.bind(this)}
                    />
                </View>
            </View>
        )
    }

    async go() {
        const service = this.props.service;
        const pswd = this.state.pswd;
        const uname = this.state.uname;
        if (uname.length == 0) {
            alert("You must input a username")
        } else if (pswd.length == 0) {
            alert("You must input a password")
        } else {
            resp = await setPswd(service.toLowerCase(), MAIN_PSWD, { pswd: pswd, uname: uname })
            if (resp == "success") {
                alert(`Username for ${service} successfully set to ${uname} and password for ${service} successfully set to ${pswd}`);
                this.props.changePage("main");
            } else {
                alert("There was a problem setting your password: " + resp);
            }
        }
    }
}

class AccountLyt extends Component {
    constructor(props) {
        super(props);
        this.state = {
            mainPswd: "",
            old: "",
            p1: "",
            p2: ""
        };
    }

    render() {
        return (
            <View style={{ flex: 1, justifyContent: "space-between", backgroundColor: "white" }}>
                <View style={{ flex: 1, backgroundColor: "white", justifyContent: "space-between" }}>
                    <View style={{ flex: 1, backgroundColor: "white", justifyContent: "flex-start" }}>
                        <Button
                            title="Log Out"
                            ref={(input) => { this.logoutbut = input }}
                            onPress={this.props.logout}
                        />
                    </View>
                    <View style={{ flex: 1, backgroundColor: "white" }}>
                        <TextInput
                            style={{ height: 40 }}
                            value={this.state.old}
                            onChangeText={val => this.setState({ old: val })}
                            placeholder="Old Password"
                            ref={(input) => { this.old = input }}
                            autoCapitalize="none"
                            secureTextEntry={true}
                            returnKeyType={"next"}
                            onSubmitEditing={() => this.p1.focus()}
                            blurOnSubmit={false}
                        />
                        <TextInput
                            style={{ height: 40 }}
                            value={this.state.p1}
                            onChangeText={val => this.setState({ p1: val })}
                            placeholder="New Password"
                            ref={(input) => { this.p1 = input }}
                            autoCapitalize="none"
                            secureTextEntry={true}
                            returnKeyType={"next"}
                            onSubmitEditing={() => this.p2.focus()}
                            blurOnSubmit={false}
                        />
                        <TextInput
                            style={{ height: 40 }}
                            value={this.state.p2}
                            onChangeText={val => this.setState({ p2: val })}
                            placeholder="Confirm Password"
                            ref={(input) => { this.p2 = input }}
                            autoCapitalize="none"
                            secureTextEntry={true}
                            onSubmitEditing={() => this.resetbut.props.onPress()}
                        />
                        <Button
                            title="Reset Main Password"
                            ref={(input) => { this.resetbut = input }}
                            style={{ flex: 1 }}
                            onPress={this.resetPswd.bind(this)}
                        />
                    </View>
                    <View style={{ flex: 1, marginBottom: 50, justifyContent: "flex-end" }}>
                        <TextInput
                            style={{ height: 40 }}
                            value={this.state.mainPswd}
                            onChangeText={val => this.setState({ mainPswd: val })}
                            placeholder="Main Password"
                            ref={(input) => { this.mainPswd = input }}
                            autoCapitalize="none"
                            secureTextEntry={true}
                            onSubmitEditing={() => this.delbut.props.onPress()}
                        />
                        <Button
                            title="Delete Account"
                            ref={(input) => { this.delbut = input }}
                            style={{ flex: 1 }}
                            onPress={this.delAcct.bind(this)}
                        />
                    </View>
                </View>
            </View>
        )
    }

    async resetPswd() {
        const mainPswd = this.state.old;
        const p1 = this.state.p1;
        const p2 = this.state.p2;
        if (mainPswd.length == 0) {
            alert("You must enter your current password");
        } else if (p1 != p2) {
            alert("The two passwords don't match!");
            this.setState({ p1: "", p2: "" });
        } else if (p1.length == 0) {
            alert("You must enter a new password");
        } else {
            const resp = await checkMainPswd(this.state.old);
            if (resp == "failure") {
                alert("That's not your old password");
                this.setState({ old: "" });
            } else if (resp == "user not in database") {
                alert(`"You must login with a valid username (${await helpers.getUname()} does not have an account)`);
            } else {
                alert("Are you absolutely sure that you want to reset your main password?", `From ${mainPswd} to ${p1}`, [
                    {
                        text: "No", onPress: () => {
                            alert("Your password was not reset");
                            this.setState({ old: "", p1: "", p2: "" });
                        }
                    },
                    {
                        text: "Yes", onPress: async () => {
                            const resp = await setMainPswd(p1, mainPswd);
                            if (resp == "success") {
                                alert(`Password set to ${p1}`);
                                MAIN_PSWD = p1;
                                this.setState({ old: "", p1: "", p2: "" });
                            } else {
                                alert("There was a problem resetting your main password");
                            }
                        }
                    }
                ], { cancelable: false });
            }
        }
    }

    async delAcct() {
        const mainPswd = this.state.mainPswd;
        if (mainPswd.length == 0) {
            alert("You must input your main password");
        } else {
            const uname = await helpers.getUname();
            if (mainPswd != MAIN_PSWD) {
                alert("That is not the correct main password");
            } else {
                alert(`Are you absolutely sure that you want to delete this account?
                
Any passwords that you have stored will no longer be accesable.
                
Only click yes if you are absolutely sure that you understand the consequences of doing so`, "", [
                        { text: "No", onPress: () => alert("Your account has not been deleted") },
                        {
                            text: "Yes", onPress: async () => {
                                await helpers.dropUser(uname, helpers.encMainPswd(mainPswd));
                                await helpers.delUname();
                                alert("Your account has been deleted");
                                this.props.changePage("login");
                            }
                        }
                    ], { cancelable: false });
            }
        }
    }
}

export default class App extends Component {
    constructor(props) {
        super(props);
        console.disableYellowBox = true;
        this.layoutOptions = {
            "login": LoginLyt,
            "newuser": NewUserLyt,
            "main": ManagePswdsLyt,
            "opts": OptionsLyt,
            "set1": SetPswdLyt1,
            "set2": SetPswdLyt2,
            "acct": AccountLyt
        };
        this.state = {
            page: this.layoutOptions["login"],
            pageName: "login",
            checked: false
        };
    }

    render() {
        let top = (
            <View style={{ height: Platform.OS == "ios" ? 200 : 50, backgroundColor: "white" }}>
                <Picker
                    selectedValue={this.state.pageName}
                    style={{ height: 50 }}
                    onValueChange={this.changePage.bind(this)}>
                    <Picker.Item label="Manage passwords" value="main" />
                    <Picker.Item label="My account" value="acct" />
                </Picker>
            </View>
        );
        if (this.state.pageName == "login" || this.state.pageName == "newuser") {
            top = (
                <View style={{ paddingTop: 40, height: 125, backgroundColor: "white" }}>
                    <CheckBox
                        title="I am creating a new account"
                        checked={this.state.checked}
                        onPress={this.checkboxClicked.bind(this)}
                    />
                </View>
            );
        } else if (this.state.pageName == "opts" || this.state.pageName == "set1" || this.state.pageName == "set2") {
            top = null;
        }
        this.state.page = this.layoutOptions[this.state.pageName];
        return (
            <TouchableWithoutFeedback
                onPressIn={() => {
                    if (logoutTimer) {
                        clearTimeout(logoutTimer);
                    }
                    logoutTimer = setTimeout(this.logout.bind(this), 90000);
                }}
            >
                <View style={{ flex: 1, padding: 10, alignItems: "stretch", justifyContent: "space-between", backgroundColor: "white" }}>
                    {top}
                    <this.state.page
                        changePage={this.changePage.bind(this)}
                        service={this.state.service}
                        pswd={this.state.pswd}
                        options={this.options.bind(this)}
                        setPswd1={this.setPswd1.bind(this)}
                        setPswd2={this.setPswd2.bind(this)}
                        logout={this.logout.bind(this)}
                    />
                </View>
            </TouchableWithoutFeedback>
        );
    }

    checkboxClicked() {
        this.state.checked = !this.state.checked;
        if (this.state.checked) {
            this.setState({ page: this.layoutOptions["newuser"], pageName: "newuser" });
        } else {
            this.setState({ page: this.layoutOptions["login"], pageName: "login" });
        }
    }

    async changePage(val) {
        if (val == "main") {
            SERVICES = await getAllServices(MAIN_PSWD);
        }
        this.setState({ page: this.layoutOptions[val], pageName: val });
    }

    options(service, pswd) {
        this.setState({
            service,
            pswd,
            pageName: "opts",
            page: this.layoutOptions["opts"]
        });
    }

    setPswd1(service) {
        this.setState({
            service,
            pageName: "set1",
            page: this.layoutOptions["set1"]
        });
    }

    setPswd2(service) {
        this.setState({
            service,
            pageName: "set2",
            page: this.layoutOptions["set2"]
        });
    }

    logout() {
        MAIN_PSWD = "";
        this.changePage.bind(this)("login");
    }
}

async function checkMainPswd(mainPswd) {
    return await helpers.checkMainPswd(await helpers.getUname(), helpers.encMainPswd(mainPswd));
}

async function setPswd(service, mainPswd, toSet) {
    const encService = helpers.encService(service, mainPswd);
    const encMainPswd = helpers.encMainPswd(mainPswd);
    const encPswd = helpers.encPswd(service, toSet, mainPswd);
    return await helpers.setPswd(await helpers.getUname(), encMainPswd, helpers.sha256(service), encPswd, encService);
}

async function getPswd(service, mainPswd) {
    const encMainPswd = helpers.encMainPswd(mainPswd);
    const resp = await helpers.getPswd(await helpers.getUname(), encMainPswd, helpers.sha256(service));
    if (!['failure', 'user not in database', "password doesn't exist"].includes(resp)) {
        return helpers.dencPswd(service, resp, mainPswd);
    }
    return resp;
}


async function delPswd(service, mainPswd) {
    const encMainPswd = helpers.encMainPswd(mainPswd);
    const encService = helpers.encService(service, mainPswd);
    const encServiceList = await helpers.getServices(await helpers.getUname(), encMainPswd);
    if (!Array.isArray(encServiceList)) {
        return encServiceList;
    }
    let serviceList = new Set();
    let toSet = [];
    for (let encService of encServiceList) {
        const dencService = helpers.dencService(encService, mainPswd);
        if (dencService !== service) {
            serviceList.add(dencService);
        }
    }
    for (let dencService of serviceList) {
        toSet.push(helpers.encService(dencService, mainPswd));
    }
    const resp = await helpers.setServiceList(await helpers.getUname(), encMainPswd, toSet)
    if (resp !== "success") {
        return resp;
    }
    return await helpers.delPswd(await helpers.getUname(), encMainPswd, helpers.sha256(service));
}

async function getAllServices(mainPswd) {
    const encMainPswd = helpers.encMainPswd(mainPswd);
    const encServiceList = await helpers.getServices(await helpers.getUname(), encMainPswd);
    if (!Array.isArray(encServiceList)) {
        return encServiceList;
    }
    let serviceList = new Set();
    for (let encService of encServiceList) {
        const decrypted = helpers.dencService(encService, mainPswd);
        serviceList.add(decrypted);
    }
    return [...serviceList];
}

function getAllServicesFromDoc(mainPswd, passwords) {
    let serviceList = new Set();
    const encList = passwords[helpers.sha256("service list")];
    for (let encrypted of encList) {
        serviceList.add(helpers.dencService(encrypted, mainPswd));
    }
    return [...serviceList];
}

async function setMainPswd(next, old) {
    const encOldPswd = helpers.encMainPswd(old);
    const encNewPswd = helpers.encMainPswd(next);
    const resp = await helpers.resetMainPswd(await helpers.getUname(), encOldPswd, encNewPswd);
    if (resp !== "success") {
        return resp;
    }
    let passwords = await helpers.getPswdsDoc(await helpers.getUname(), encNewPswd);
    if (typeof passwords !== "object") {
        return passwords;
    }
    const serviceList = getAllServicesFromDoc(old, passwords);
    let serviceToPass = {};
    for (let service of serviceList) {
        const key = helpers.sha256(service);
        const encrypted = passwords[key];
        const decrypted = helpers.dencPswd(service, encrypted, old);
        serviceToPass[service] = decrypted;
    }
    let encServiceList = [];
    for (let service of serviceList) {
        const encPswd = helpers.encPswd(service, serviceToPass[service], next);
        passwords[helpers.sha256(service)] = encPswd;
        const encService = helpers.encService(service, next);
        encServiceList.push(encService);
    }
    passwords[helpers.sha256("service list")] = encServiceList;
    return await helpers.setPswdsDoc(await helpers.getUname(), encNewPswd, passwords);
}