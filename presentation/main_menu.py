# presentation/main_menu.py
from PyQt6.QtWidgets import QMainWindow, QTableWidgetItem, QInputDialog, QMessageBox, QDialog, QApplication
from decimal import Decimal
from business.account_service import AccountService
from business.models import Usuario, Cuenta
from data.rates_repository import RatesRepository
from presentation.screens.Main_ui import Ui_MainWindow
from presentation.screens.DialogAccounts import Ui_Dialog

class DialogoCuenta(QDialog, Ui_Dialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

class MainMenu(QMainWindow, Ui_MainWindow):
    def __init__(self, user: Usuario):
        super().__init__()
        self.user = user
        self.svc = AccountService()
        self.setupUi(self)
        try:
            self.AccountTable.horizontalHeader().setStretchLastSection(True)
        except Exception:
            pass
        self.btnAddAccount.clicked.connect(self._crear_cuenta)
        self.btnDeposit.clicked.connect(self._depositar_ars)
        self.btnBuy.clicked.connect(lambda: self.statusBar().showMessage("Pendiente: Comprar Moneda", 3000))
        self.btnSell.clicked.connect(lambda: self.statusBar().showMessage("Pendiente: Vender Moneda", 3000))
        self.btnLogout.clicked.connect(self._logout)
        self._refresh_table()
        self.statusBar().showMessage(f"Sesión: {self.user.username}", 3000)

    def _refresh_table(self):
        self.AccountTable.setRowCount(0)
        for moneda, cuenta in sorted(self.user.cuentas.items()):
            row = self.AccountTable.rowCount()
            self.AccountTable.insertRow(row)
            self.AccountTable.setItem(row, 0, QTableWidgetItem(moneda))
            self.AccountTable.setItem(row, 1, QTableWidgetItem(str(cuenta.saldo)))

    def _depositar_ars(self):
        monto_str, ok = QInputDialog.getText(self, "Depósito de ARS", "Monto en ARS:")
        if not ok:
            return
        mensaje = self.svc.depositar_ars(self.user, (monto_str or "").strip())
        QMessageBox.information(self, "Depósito", mensaje)
        self._refresh_table()

    def _crear_cuenta(self):
        dlg = DialogoCuenta(self)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        moneda = dlg.accountList.currentText().strip().upper()
        rates = RatesRepository.load_rates()
        if moneda in self.user.cuentas:
            QMessageBox.warning(self, "Crear cuenta", f"Ya tenés una cuenta en {moneda}.")
            return
        if moneda not in rates.keys():
            QMessageBox.warning(self, "Crear cuenta", f"La moneda '{moneda}' no está disponible.")
            return
        self.user.cuentas[moneda] = Cuenta(moneda, Decimal("0.00"))
        self.svc.repo.save_user(self.user)
        QMessageBox.information(self, "Crear cuenta", f"Cuenta en {moneda} creada.")
        self._refresh_table()

    def _logout(self):
        self.close()
        app = QApplication.instance()
        if app is not None:
            app.quit()
