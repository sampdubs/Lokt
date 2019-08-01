from fbs_runtime.application_context.PyQt5 import ApplicationContext
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import *
import sip
import sys
from functools import partial
from pyperclip import copy
import helpers

MAIN_PSWD = ""
SERVICES = []
timer = None


def make_login_lyt(new_user=False):
    message = QLabel()
    layout = QVBoxLayout()
    message.setText("Please login with your username")
    new_checkbox = QCheckBox("I am creating a new account")
    new_checkbox.setFixedHeight(45)
    uname_input = QLineEdit()
    uname_input.setPlaceholderText("Username")
    main_pswd_input = QLineEdit()
    main_pswd_input.setEchoMode(QLineEdit.Password)
    main_pswd_input.setPlaceholderText("Main password")
    if new_user:
        message.setText(
            "Please enter your username and password to create an account")
        new_checkbox.setChecked(True)
        main_pswd_confirm_input = QLineEdit()
        main_pswd_confirm_input.setEchoMode(QLineEdit.Password)
        main_pswd_confirm_input.setPlaceholderText("Confirm password")
        layout.addWidget(new_checkbox)
        layout.addWidget(message)
        layout.addWidget(uname_input)
        layout.addWidget(main_pswd_input)
        layout.addWidget(main_pswd_confirm_input)
    else:
        layout.addWidget(new_checkbox)
        layout.addWidget(uname_input)
        layout.addWidget(main_pswd_input)
    layout.addStretch(1)
    frame = QFrame()
    frame.setLayout(layout)
    return frame


def make_main_lyt():
    service_input = QLineEdit()
    layout = QVBoxLayout()
    service_input.setPlaceholderText("Service name")
    layout.addWidget(service_input)
    scroll_layout = QVBoxLayout()
    scroll_layout.addStretch(1)
    scroll_widget = QWidget()
    scroll_widget.setLayout(scroll_layout)
    scroller = QScrollArea()
    scroller.setWidget(scroll_widget)
    scroller.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    scroller.setWidgetResizable(True)
    layout.addWidget(scroller, stretch=20)
    layout.addStretch(1)
    frame = QFrame()
    frame.setLayout(layout)
    return frame


def make_account_lyt():
    layout = QVBoxLayout()
    log_out_btn = QPushButton("Log out")
    log_out_btn.setAutoDefault(True)
    label1 = QLabel("Reset your main password")
    old_input = QLineEdit()
    old_input.setEchoMode(QLineEdit.Password)
    old_input.setPlaceholderText("Current main password")
    p1_input = QLineEdit()
    p1_input.setEchoMode(QLineEdit.Password)
    p1_input.setPlaceholderText("New main password")
    p2_input = QLineEdit()
    p2_input.setEchoMode(QLineEdit.Password)
    p2_input.setPlaceholderText("Confirm new main password")
    reset_btn = QPushButton("Reset main password")
    spacer1 = QSpacerItem(20, 5000, QSizePolicy.Minimum, QSizePolicy.Expanding)
    spacer2 = QSpacerItem(20, 5000, QSizePolicy.Minimum, QSizePolicy.Expanding)
    label2 = QLabel("Delete your account")
    main_pswd_input = QLineEdit()
    main_pswd_input.setEchoMode(QLineEdit.Password)
    main_pswd_input.setPlaceholderText("Main password")
    del_acct_btn = QPushButton("Delete account")
    del_acct_btn.setAutoDefault(True)
    layout.addWidget(log_out_btn)
    layout.addItem(spacer1)
    layout.addWidget(label1)
    layout.addWidget(old_input)
    layout.addWidget(p1_input)
    layout.addWidget(p2_input)
    layout.addWidget(reset_btn)
    layout.addItem(spacer2)
    layout.addWidget(label2)
    layout.addWidget(main_pswd_input)
    layout.addWidget(del_acct_btn)
    layout.addStretch(1)
    frame = QFrame()
    frame.setLayout(layout)
    return frame


def alert(msg):
    alert = QMessageBox()
    alert.setText(msg)
    alert.exec_()


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setMouseTracking(True)
        self.mouseMoveEvent = self.reset_time
        self.layoutOptions = {}
        self.screen = "Login"
        self.screenChoice = QComboBox()
        self.screenChoice.addItems(
            ["Manage passwords", "My account"])
        self.screenChoice.currentTextChanged.connect(self.on_changed)
        self.go_button = QPushButton("Go!")
        self.go_button.clicked.connect(self.on_button_clicked)
        self.go_button.setAutoDefault(True)
        self.layoutOptions["Login"] = make_login_lyt()
        self.layoutOptions["Manage passwords"] = make_main_lyt()
        self.layoutOptions["My account"] = make_account_lyt()
        self.layoutOptions["Login"].children(
        )[3].returnPressed.connect(self.on_button_clicked)
        self.layoutOptions["Login"].children(
        )[1].stateChanged.connect(self.checkbox_clicked)
        self.layoutOptions["Manage passwords"].children(
        )[1].textChanged.connect(self.on_text_changed)
        self.layoutOptions["Manage passwords"].children(
        )[1].returnPressed.connect(self.on_button_clicked)
        self.layoutOptions["My account"].children(
        )[1].clicked.connect(self.logout)
        self.layoutOptions["My account"].children(
        )[5].returnPressed.connect(self.change_main)
        self.layoutOptions["My account"].children(
        )[6].clicked.connect(self.change_main)
        self.layoutOptions["My account"].children(
        )[8].returnPressed.connect(self.del_account)
        self.layoutOptions["My account"].children(
        )[9].clicked.connect(self.del_account)
        self.mainLayout = QVBoxLayout()
        self.mainLayout.addWidget(self.screenChoice)
        self.mainLayout.setAlignment(self.screenChoice, Qt.AlignTop)
        self.mainLayout.addWidget(self.layoutOptions["Login"])
        self.mainLayout.addWidget(
            self.layoutOptions["Manage passwords"])
        self.mainLayout.addWidget(self.layoutOptions["My account"])
        self.mainLayout.addWidget(self.go_button)
        self.on_changed("Login")
        self.setLayout(self.mainLayout)
        self.checkbox_clicked(Qt.Checked)
        self.checkbox_clicked(Qt.Unchecked)

    def reset_time(self, _):
        global timer
        if timer:
            timer.stop()
        timer = QTimer()
        timer.timeout.connect(self.logout)
        timer.start(90000)

    def checkbox_clicked(self, state):
        self.mainLayout.removeWidget(self.layoutOptions["Login"])
        sip.delete(self.layoutOptions["Login"])
        self.mainLayout.removeWidget(self.go_button)
        if state == Qt.Checked:
            self.layoutOptions["Login"] = make_login_lyt(True)
            self.layoutOptions["Login"].children(
            )[5].returnPressed.connect(self.on_button_clicked)
        else:
            self.layoutOptions["Login"] = make_login_lyt()
            self.layoutOptions["Login"].children(
            )[3].returnPressed.connect(self.on_button_clicked)
        self.layoutOptions["Login"].children(
        )[1].stateChanged.connect(self.checkbox_clicked)
        self.mainLayout.addWidget(self.layoutOptions["Login"])
        self.mainLayout.addWidget(self.go_button)
        self.on_changed("Login")

    def logout(self):
        global timer
        if timer:
            timer.stop()
            timer = None
        self.screenChoice.setCurrentIndex(0)
        global MAIN_PSWD
        MAIN_PSWD = ""
        self.on_changed("Login")

    def change_main(self):
        chils = self.layoutOptions[self.screen].children()
        mainPswd = chils[3].text()
        p1 = chils[4].text()
        p2 = chils[5].text()
        if len(mainPswd) == 0:
            alert("You must enter your current password")
        elif p1 != p2:
            alert("The two passwords don't match!")
        elif len(p1) == 0:
            alert("You must enter a new password")
        else:
            resp = checkMainPswd(mainPswd)
            if resp == "failure":
                alert("That's not your old password")
                chils[3].setText("")
            elif resp == "user not in database":
                alert(
                    f"The username {helpers.getUname()} does not have an account associated with it")
            elif self.ask("Are you absolutely sure that you want to reset your main password?"):
                resp = setMainPswd(p1, mainPswd)
                if resp == "success":
                    alert(f"Password set to {p1}")
                    global MAIN_PSWD
                    MAIN_PSWD = p1
                    for item in chils:
                        if isinstance(item, QLineEdit):
                            item.setText("")
                else:
                    alert("There was a problem resetting your main password")
            else:
                alert("Your password was not reset")

    def del_account(self):
        mainPswd = self.layoutOptions[self.screen].children()[8].text()
        if len(mainPswd) == 0:
            alert("You must input your main password")
        else:
            uname = helpers.getUname()
            resp = helpers.checkMainPswd(uname, helpers.encMainPswd(mainPswd))
            if resp == "failure":
                alert("That is not the correct main password")
            elif resp == "user not in database":
                alert(
                    f"The username {uname} does not have an account associated with it")
            else:
                if self.ask("""Are you absolutely sure that you want to delete this account?

Any passwords that you have stored will no longer be accesable.

Only click yes if you are absolutely sure that you understand the consequences of doing so"""):
                    helpers.dropUser(uname, helpers.encMainPswd(mainPswd))
                    helpers.delUname()
                    alert("Your account has been deleted")
                    self.on_changed("Login")
                else:
                    alert("Your account has not been deleted")

    def on_changed(self, value):
        if value == "Manage passwords":
            global SERVICES
            s1 = getAllServices(MAIN_PSWD)
            s1 = list({service.title() for service in s1})
            s1.sort()
            lyt = self.layoutOptions[value].children()[2].widget().layout()
            if s1 != SERVICES:
                SERVICES = s1
                SERVICES = list({service.title() for service in SERVICES})
                SERVICES.sort()
                for i in reversed(range(lyt.count())):
                    widget = lyt.takeAt(i).widget()
                    if widget is not None:
                        widget.setParent(None)
                for service in SERVICES:
                    label = QLabel("• " + service)

                    def on_click(s, e):
                        pswd = getPswd(s.lower(), MAIN_PSWD)
                        self.options(s, pswd)
                    label.mouseReleaseEvent = partial(on_click, service)
                    lyt.addWidget(label)
        if self.screen == "Login" and self.screen != value:
            self.screenChoice.show()
        elif value == "Login":
            self.screenChoice.hide()
            if self.screen != value:
                self.mainLayout.removeWidget(self.layoutOptions["Login"])
                sip.delete(self.layoutOptions["Login"])
                if self.screen != "My account":
                    self.mainLayout.removeWidget(self.go_button)
                self.layoutOptions["Login"] = make_login_lyt()
                self.layoutOptions["Login"].children(
                )[3].returnPressed.connect(self.on_button_clicked)
                self.layoutOptions["Login"].children(
                )[1].stateChanged.connect(self.checkbox_clicked)
                self.mainLayout.addWidget(self.layoutOptions["Login"])
                if self.screen != "My account":
                    self.mainLayout.addWidget(self.go_button)
        if self.screen == "My account":
            self.go_button = QPushButton("Go!")
            self.go_button.clicked.connect(self.on_button_clicked)
            self.go_button.setAutoDefault(True)
            self.mainLayout.addWidget(self.go_button)
        elif value == "My account":
            self.mainLayout.removeWidget(self.go_button)
            sip.delete(self.go_button)
        for key in self.layoutOptions:
            if key != value:
                self.layoutOptions[key].hide()
        self.layoutOptions[value].show()
        self.screen = value
        if value == "Login" and self.screen != value:
            self.checkbox_clicked(Qt.Checked)
            self.checkbox_clicked(Qt.Unchecked)
        chils = self.layoutOptions[value].children()
        for item in chils:
            if isinstance(item, QLineEdit):
                item.setText("")
        uname = helpers.getUname()
        if uname != "file does not exist" and value == "Login" and chils[1].isChecked() == False:
            self.layoutOptions[value].children()[2].setText(uname)

    def ask(self, msg):
        buttonReply = QMessageBox.question(
            self, "", msg, QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        return buttonReply == QMessageBox.Yes

    def options(self, service, pswd):
        question = QMessageBox()
        if "uname" in pswd:
            question.setText(
                f"Your username for {service} is {pswd['uname']}\nYour password for {service} is {pswd['pswd']}")
        else:
            question.setText(
                f"Your password for {service} is {pswd['pswd']}\nYou have no username set")
        b1 = QPushButton("Ok")
        b2 = QPushButton("Copy password to clipboard")
        b2.clicked.connect(lambda: copy(pswd["pswd"]))
        b3 = QPushButton("Change password")

        def on_change():
            global SERVICES
            if self.ask(f"Would you like to set a username for {service}?"):
                uname, okPressed = QInputDialog.getText(
                    self, "Set username", f"Username to set for {service}:", QLineEdit.Normal, "")
                if okPressed:
                    if len(uname) > 0:
                        pswd, okPressed = QInputDialog.getText(
                            self, "Set password", f"Password to set for {service}:", QLineEdit.Normal, "")
                        if okPressed:
                            if len(pswd) > 0:
                                if self.ask(f"Are you sure that you want to reset this password to {pswd} (and the username to {uname}?"):
                                    resp = setPswd(
                                        service.lower(), MAIN_PSWD, pswd=pswd, uname=uname)
                                    if resp == "success":
                                        alert(
                                            f"Username for {service} successfully set to {uname} and password set to {pswd}")
                                    else:
                                        alert(
                                            "There was a problem setting your password")
                                    SERVICES = getAllServices(MAIN_PSWD)
                                    self.layoutOptions[self.screen].children()[
                                        1].setText("")
                                else:
                                    alert(
                                        f"The password for {service} has not been changed")
                            else:
                                alert("You must enter a password")
                    else:
                        alert("You must enter a username")
            else:
                pswd, okPressed = QInputDialog.getText(
                    self, "Set password", f"Password to set for {service}:", QLineEdit.Normal, "")
                if okPressed:
                    if len(pswd) > 0:
                        if self.ask(f"Are you sure that you want to reset this password to {pswd}?"):
                            resp = setPswd(service.lower(),
                                           MAIN_PSWD, pswd=pswd)
                            if resp == "success":
                                alert(
                                    f"Password for {service} successfully set to {pswd}")
                            else:
                                alert("There was a problem setting your password")
                            SERVICES = getAllServices(MAIN_PSWD)
                            self.layoutOptions[self.screen].children()[
                                1].setText("")
                        else:
                            alert(
                                f"The password for {service} has not been changed")
                    else:
                        alert("You must enter a password")
        b3.clicked.connect(on_change)
        b4 = QPushButton("Delete password")

        def on_del():
            if self.ask(f"Are you sure that you want to delete your password for {service}?"):
                resp = delPswd(service.lower(), MAIN_PSWD)
                if resp == "success":
                    alert(
                        f"Password successfully deleted for {service}")
                    global SERVICES
                    SERVICES = getAllServices(MAIN_PSWD)
                    self.layoutOptions[self.screen].children()[1].setText("")
                    self.on_text_changed("")
                else:
                    alert("There was a problem deleting your password")
        b4.clicked.connect(on_del)
        question.addButton(b1, QMessageBox.NoRole)
        question.addButton(b2, QMessageBox.AcceptRole)
        question.addButton(b3, QMessageBox.ResetRole)
        question.addButton(b4, QMessageBox.DestructiveRole)
        question.exec()

    def on_text_changed(self, text):
        chils = self.layoutOptions[self.screen].children()
        global SERVICES
        s1 = SERVICES.copy()
        s1 = list({service.title()
                   for service in s1 if service.lower().startswith(text.lower())})
        s1.sort()
        lyt = chils[2].widget().layout()
        for i in reversed(range(lyt.count())):
            widget = lyt.takeAt(i).widget()
            if widget is not None:
                widget.setParent(None)
        for service in s1:
            label = QLabel("• " + service)

            def on_click(s, e):
                pswd = getPswd(s.lower(), MAIN_PSWD)
                self.options(s, pswd)
            label.mouseReleaseEvent = partial(on_click, service)
            lyt.addWidget(label)

    def on_button_clicked(self):
        chils = self.layoutOptions[self.screen].children()
        if self.screen == "Login":
            global MAIN_PSWD, timer
            if len(chils) == 4:
                uname = chils[2].text()
                if len(uname) == 0:
                    alert("You must input your username!")
                else:
                    mainPswd = chils[3].text()
                    if helpers.userExists(uname):
                        if len(mainPswd) == 0:
                            alert("You must input your main password!")
                        else:
                            resp = helpers.checkMainPswd(
                                uname, helpers.encMainPswd(mainPswd))
                            if resp == "failure":
                                alert("That is not the correct main password")
                                chils[3].setText("")
                            else:
                                helpers.setUname(uname)
                                MAIN_PSWD = mainPswd
                                if timer:
                                    timer.stop()
                                timer = QTimer()
                                timer.timeout.connect(self.logout)
                                timer.start(90000)
                                self.on_changed("Manage passwords")
                    else:
                        alert(
                            f"The username {uname} does not have an account associated with it")
                        chils[2].setText("")
            else:
                uname = chils[3].text()
                p1 = chils[4].text()
                p2 = chils[5].text()
                if p1 != p2:
                    alert("The two passwords don't match")
                    chils[4].setText("")
                    chils[5].setText("")
                elif len(p1) == 0:
                    alert("You must input a main password")
                elif helpers.userExists(uname):
                    alert(f"The username {uname} is already in use")
                else:
                    helpers.createUser(uname, helpers.encMainPswd(p1))
                    helpers.setUname(uname)
                    MAIN_PSWD = p1
                    if timer:
                        timer.stop()
                    timer = QTimer()
                    timer.timeout.connect(self.logout)
                    timer.start(90000)
                    alert("Your account has been created")
                    self.on_changed("Manage passwords")
        elif self.screen == "Manage passwords":
            global SERVICES
            service = chils[1].text()
            pswd = getPswd(service.lower(), MAIN_PSWD)
            if pswd == "password doesn't exist":
                lyt = chils[2].widget().layout()
                for i in range(lyt.count()):
                    widget = lyt.takeAt(i).widget()
                    if isinstance(widget, QLabel):
                        service = widget.text()[2:]
                        pswd = getPswd(service.lower(), MAIN_PSWD)
                        self.options(service, pswd)
                        return
                if self.ask(f"Would you like to set a username for {service}?"):
                    uname, okPressed = QInputDialog.getText(
                        self, "Set username", f"Username to set for {service}:", QLineEdit.Normal, "")
                    if okPressed:
                        if len(uname) > 0:
                            pswd, okPressed = QInputDialog.getText(
                                self, "Set password", f"Password to set for {service}:", QLineEdit.Normal, "")
                            if okPressed:
                                if len(pswd) > 0:
                                    resp = setPswd(
                                        service.lower(), MAIN_PSWD, pswd=pswd, uname=uname)
                                    if resp == "success":
                                        alert(
                                            f"Username for {service} successfully set to {uname} and password set to {pswd}")
                                    else:
                                        alert(
                                            "There was a problem setting your password")
                                    SERVICES = getAllServices(MAIN_PSWD)
                                    self.layoutOptions[self.screen].children()[
                                        1].setText("")
                                else:
                                    alert("You must enter a password")
                        else:
                            alert("You must enter a username")
                else:
                    pswd, okPressed = QInputDialog.getText(
                        self, "Set password", f"Password to set for {service}:", QLineEdit.Normal, "")
                    if okPressed:
                        if len(pswd) > 0:
                            resp = setPswd(service.lower(),
                                           MAIN_PSWD, pswd=pswd)
                            if resp == "success":
                                alert(
                                    f"Password for {service} successfully set to {pswd}")
                            else:
                                alert("There was a problem setting your password")
                            SERVICES = getAllServices(MAIN_PSWD)
                            self.layoutOptions[self.screen].children()[
                                1].setText("")
                        else:
                            alert("You must enter a password")
            else:
                self.options(service, pswd)
        elif self.screen == "Reset main password":
            mainPswd = chils[2].text()
            p1 = chils[4].text()
            p2 = chils[6].text()
            if len(mainPswd) == 0:
                alert("You must enter your current password")
            elif p1 != p2:
                alert("The two passwords don't match!")
            elif len(p1) == 0:
                alert("You must enter a new password")
            else:
                resp = checkMainPswd(mainPswd)
                if resp == "failure":
                    alert("That's not your old password")
                    chils[2].setText("")
                elif resp == "user not in database":
                    alert(
                        f"The username {mainPswd} does not have an account associated with it")
                elif self.ask("Are you absolutely sure that you want to reset your main password?"):
                    resp = setMainPswd(p1, mainPswd)
                    if resp == "success":
                        alert(f"Password set to {p1}")
                        for item in chils:
                            if isinstance(item, QLineEdit):
                                item.setText("")
                    else:
                        alert("There was a problem resetting your main password")
                else:
                    alert("Your password was not reset")


def checkMainPswd(mainPswd):
    return helpers.checkMainPswd(helpers.getUname(), helpers.encMainPswd(mainPswd))


def setPswd(service, mainPswd, pswd=None, uname=None):
    encService = helpers.encService(service, mainPswd)
    encMainPswd = helpers.encMainPswd(mainPswd)
    encPswd = helpers.encPswd(service, pswd, mainPswd)
    if uname:
        encUname = helpers.encPswd(service, uname, mainPswd)
        return helpers.setPswd(helpers.getUname(), encMainPswd, helpers.sha256(service), {"pswd": encPswd, "uname": encUname}, encService)
    return helpers.setPswd(helpers.getUname(), encMainPswd, helpers.sha256(service), {"pswd": encPswd}, encService)


def getPswd(service, mainPswd):
    encMainPswd = helpers.encMainPswd(mainPswd)
    resp = helpers.getPswd(helpers.getUname(), encMainPswd, helpers.sha256(
        service))
    try:
        return {key: helpers.dencPswd(service, value, mainPswd) for key, value in resp.items()}
    except:
        return resp


def delPswd(service, mainPswd):
    encMainPswd = helpers.encMainPswd(mainPswd)
    encService = helpers.encService(service, mainPswd)
    encServiceList = helpers.getServices(helpers.getUname(), encMainPswd)
    if type(encServiceList) != list:
        return encServiceList
    serviceList = set()
    toSet = []
    for encService in encServiceList:
        dencService = helpers.dencService(encService, mainPswd)
        if dencService != service:
            serviceList.add(dencService)
    for dencService in serviceList:
        toSet.append(helpers.encService(dencService, mainPswd))
    resp = helpers.setServiceList(helpers.getUname(), encMainPswd, toSet)
    if resp != "success":
        return resp
    return helpers.delPswd(helpers.getUname(), encMainPswd, helpers.sha256(service))


def getAllServices(mainPswd):
    encMainPswd = helpers.encMainPswd(mainPswd)
    encServiceList = helpers.getServices(helpers.getUname(), encMainPswd)
    if type(encServiceList) != list:
        return encServiceList
    serviceList = set()
    for encService in encServiceList:
        decrypted = helpers.dencService(encService, mainPswd)
        serviceList.add(decrypted)
    return list(serviceList)


def getAllServicesFromDoc(mainPswd, passwords):
    serviceList = set()
    encList = passwords[helpers.sha256("service list")]
    for encrypted in encList:
        serviceList.add(helpers.dencService(encrypted, mainPswd))
    return list(serviceList)


def setMainPswd(new, old):
    encOldPswd = helpers.encMainPswd(old)
    encNewPswd = helpers.encMainPswd(new)
    resp = helpers.resetMainPswd(helpers.getUname(), encOldPswd, encNewPswd)
    if resp != "success":
        return resp
    passwords = helpers.getPswdsDoc(helpers.getUname(), encNewPswd)
    if type(passwords) != dict:
        return passwords
    serviceList = getAllServicesFromDoc(old, passwords)
    serviceToPass = {}
    for service in serviceList:
        key = helpers.sha256(service)
        encrypted = passwords[key]
        decrypted = {key: helpers.dencPswd(
            service, value, old) for key, value in encrypted.items()}
        serviceToPass[service] = decrypted
    encServiceList = []
    for service in serviceList:
        encPswd = {key: helpers.encPswd(service, value, new)
                   for key, value in serviceToPass[service].items()}
        passwords[helpers.sha256(service)] = encPswd
        encService = helpers.encService(service, new)
        encServiceList.append(encService)
    passwords[helpers.sha256("service list")] = encServiceList
    return helpers.setPswdsDoc(helpers.getUname(), encNewPswd, passwords)


if __name__ == "__main__":
    appctxt = ApplicationContext()
    window = MainWindow()
    window.resize(700, 600)
    window.show()
    exit_code = appctxt.app.exec_()
    sys.exit(exit_code)
