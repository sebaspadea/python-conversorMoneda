from PyQt6.QtWidgets import QApplication, QDialog, QMessageBox
import sys

from presentation.screens.InitMenu_ui import Ui_InitMenu
from presentation.screens.Login_ui import Ui_LoginDialog
from presentation.screens.Register_ui import Ui_RegisterDialog

from business.authentication import Authenticator
from data.rates_repository import RatesRepository
from presentation.main_menu import MainMenu


class InitMenu(QDialog, Ui_InitMenu):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.choice = None
        self.btnLogin.clicked.connect(self.on_login)
        self.btnRegister.clicked.connect(self.on_register)
        self.btnExit.clicked.connect(self.on_exit)

    def on_login(self):
        self.choice = "login"
        self.accept()

    def on_register(self):
        self.choice = "register"
        self.accept()

    def on_exit(self):
        self.choice = "exit"
        self.reject()


class LoginDialog(QDialog, Ui_LoginDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.btnBox.accepted.connect(self.accept)
        self.btnBox.rejected.connect(self.reject)


class RegisterDialog(QDialog, Ui_RegisterDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.btnBox.accepted.connect(self.accept)
        self.btnBox.rejected.connect(self.reject)


class InitFlow:
    def __init__(self):
        self.app = None
        self.auth = Authenticator()
        self.rates_repo = RatesRepository()

    def start(self):
        self.app = QApplication(sys.argv)
        while True:
            menu = InitMenu()
            if menu.exec() != QDialog.DialogCode.Accepted or menu.choice == "exit":
                sys.exit(0)
            if menu.choice == "register":
                ok = self._handle_register()
                if not ok:
                    continue
                continue
            if menu.choice == "login":
                ok, user = self._handle_login()
                if not ok:
                    continue
                try:
                    self.rates_repo.load_rates()
                except Exception as e:
                    QMessageBox.information(None, "Aviso", f"No se pudieron cargar las cotizaciones.\n{e}")
                window = MainMenu(user)
                window.show()
                self.app.exec()

    def _handle_login(self):
        dlg = LoginDialog()
        while True:
            if dlg.exec() != QDialog.DialogCode.Accepted:
                return False, None
            username = dlg.txtUser.text().strip()
            password = dlg.txtPass.text().strip()
            if not username or not password:
                QMessageBox.warning(None, "Error", "Completá usuario y contraseña.")
                continue
            result, message, user = self.auth.login(username, password)
            if not result:
                QMessageBox.warning(None, "Login fallido", message)
                continue
            return True, user

    def _handle_register(self):
        dlg = RegisterDialog()
        while True:
            if dlg.exec() != QDialog.DialogCode.Accepted:
                return False
            user = dlg.txtUser.text().strip()
            p1 = dlg.txtPass.text()
            p2 = dlg.txtPass2.text()
            if not user or not p1 or not p2:
                dlg.lblError.setText("Completá todos los campos.")
                continue
            if p1 != p2:
                dlg.lblError.setText("Las contraseñas no coinciden.")
                continue
            valido, mensaje = self.auth.validar_password(p1)
            if not valido:
                dlg.lblError.setText(mensaje)
                continue
            msg = self.auth.register(user, p1)
            if msg.strip().startswith("❌") or "error" in msg.lower():
                dlg.lblError.setText(msg)
                continue
            QMessageBox.information(None, "Registro", msg)
            return True
