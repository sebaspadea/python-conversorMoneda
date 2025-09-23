from PyQt6.QtWidgets import QApplication, QDialog, QMainWindow, QTableWidgetItem, QMessageBox
import sys

from presentation.screens.InitMenu_ui import Ui_InitMenu
from presentation.screens.Login_ui import Ui_LoginDialog
from presentation.screens.Register_ui import Ui_RegisterDialog
from presentation.screens.Main_ui import Ui_MainWindow
from presentation.screens.DialogAccounts import Ui_Dialog

from business.authentication import Authenticator
from data.rates_repository import RatesRepository


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


class DialogoCuenta(QDialog, Ui_Dialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)


class VentanaPrincipal(QMainWindow, Ui_MainWindow):
    def __init__(self, username: str):
        super().__init__()
        self.username = username
        self.setupUi(self)
        try:
            self.AccountTable.horizontalHeader().setStretchLastSection(True)
        except Exception:
            pass
        try:
            self.btnAddAccount.clicked.connect(self.on_add_account)
            self.btnBuy.clicked.connect(lambda: self.statusBar().showMessage("Comprar Moneda (pendiente de business)", 3000))
            self.btnSell.clicked.connect(lambda: self.statusBar().showMessage("Vender Moneda (pendiente de business)", 3000))
        except Exception:
            pass
        self.statusBar().showMessage(f"Sesión iniciada: {self.username}", 3000)
        self.show()

    def on_add_account(self):
        dlg = DialogoCuenta(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            moneda = getattr(dlg, "accountList").currentText()
            row = self.AccountTable.rowCount()
            self.AccountTable.insertRow(row)
            self.AccountTable.setItem(row, 0, QTableWidgetItem(moneda))
            self.AccountTable.setItem(row, 1, QTableWidgetItem("0.00"))


class InitFlow:
    def __init__(self):
        self.app = None
        self.window = None
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
                ok = self._handle_login()
                if ok:
                    break
                continue
        sys.exit(self.app.exec())

    def _handle_login(self) -> bool:
        login = LoginDialog()
        while True:
            if login.exec() != QDialog.DialogCode.Accepted:
                return False
            username = login.txtUser.text().strip()
            password = login.txtPass.text().strip()
            if not username or not password:
                QMessageBox.warning(None, "Error", "Completá usuario y contraseña.")
                continue
            result, message, user = self.auth.login(username, password)
            if not result:
                QMessageBox.warning(None, "Login fallido", message)
                continue
            try:
                self.rates_repo.load_rates()
            except Exception as e:
                QMessageBox.information(None, "Aviso", f"No se pudieron cargar las cotizaciones.\n{e}")
            self.window = VentanaPrincipal(username=username)
            return True

    def _handle_register(self) -> bool:
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
