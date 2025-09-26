from PyQt6.QtWidgets import QMainWindow, QTableWidgetItem, QInputDialog, QMessageBox, QDialog, QApplication
from decimal import Decimal
from business.account_service import AccountService
from business.models import Usuario, Cuenta
from data.rates_repository import RatesRepository
from presentation.screens.Main_ui import Ui_MainWindow
from presentation.screens.ChangeCurrencyDialog_ui import Ui_ChangeCurrencyDialog


class ChangeCurrencyDialog(QDialog, Ui_ChangeCurrencyDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        if hasattr(self, "btnBox"):
            self.btnBox.accepted.connect(self.accept)
            self.btnBox.rejected.connect(self.reject)


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
        self.btnAddAccount.clicked.connect(self.create_account)
        self.btnDeposit.clicked.connect(self.deposit_ars)
        self.btnBuy.clicked.connect(self.buy_currency)
        self.btnSell.clicked.connect(self.sell_currency)
        self.btnLogout.clicked.connect(self.logout)
        self.refresh_table()
        self.statusBar().showMessage(f"Sesión: {self.user.username}", 3000)

    def refresh_table(self):
        self.AccountTable.setRowCount(0)
        for currency, account in sorted(self.user.cuentas.items()):
            row = self.AccountTable.rowCount()
            self.AccountTable.insertRow(row)
            self.AccountTable.setItem(row, 0, QTableWidgetItem(currency))
            self.AccountTable.setItem(row, 1, QTableWidgetItem(str(account.saldo)))

    def deposit_ars(self):
        amount_str, ok = QInputDialog.getText(self, "Depósito de ARS", "Monto en ARS:")
        if not ok:
            return
        message = self.svc.depositar_ars(self.user, (amount_str or "").strip())
        QMessageBox.information(self, "Depósito", message)
        self.refresh_table()

    def create_account(self):
        currency, ok = QInputDialog.getText(self, "Crear cuenta", "Código de moneda (ej: USD, EUR):")
        if not ok:
            return
        currency = (currency or "").strip().upper()
        if not currency:
            QMessageBox.warning(self, "Crear cuenta", "Ingresá un código de moneda.")
            return
        rates = RatesRepository.load_rates()
        if currency in self.user.cuentas:
            QMessageBox.warning(self, "Crear cuenta", f"Ya tenés una cuenta en {currency}.")
            return
        if currency not in rates.keys():
            QMessageBox.warning(self, "Crear cuenta", f"La moneda '{currency}' no está disponible en rates.json.")
            return
        self.user.cuentas[currency] = Cuenta(currency, Decimal("0.00"))
        self.svc.repo.save_user(self.user)
        QMessageBox.information(self, "Crear cuenta", f"Cuenta en {currency} creada.")
        self.refresh_table()

    def buy_currency(self):
        dlg = ChangeCurrencyDialog(self)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        origin = (dlg.txtFrom.text() or "").strip().upper()
        target = (dlg.txtTo.text() or "").strip().upper()
        amount_target = (dlg.txtAmount.text() or "").strip()
        if not origin or not target or not amount_target:
            QMessageBox.warning(self, "Comprar moneda", "Completá todos los campos.")
            return
        if origin == target:
            QMessageBox.warning(self, "Comprar moneda", "Las monedas deben ser distintas.")
            return
        r = QMessageBox.question(
            self,
            "Confirmar compra",
            f"¿Confirmás comprar {amount_target} {target} pagando desde {origin}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if r != QMessageBox.StandardButton.Yes:
            QMessageBox.information(self, "Comprar moneda", "Operación cancelada.")
            return
        message = self.svc.comprar_moneda(self.user, origin, target, amount_target)
        QMessageBox.information(self, "Comprar moneda", message)
        self.refresh_table()

    def sell_currency(self):
        dlg = ChangeCurrencyDialog(self)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        origin = (dlg.txtFrom.text() or "").strip().upper()
        target = (dlg.txtTo.text() or "").strip().upper()
        amount_origin = (dlg.txtAmount.text() or "").strip()
        if not origin or not target or not amount_origin:
            QMessageBox.warning(self, "Vender moneda", "Completá todos los campos.")
            return
        if origin == target:
            QMessageBox.warning(self, "Vender moneda", "Las monedas deben ser distintas.")
            return
        r = QMessageBox.question(
            self,
            "Confirmar venta",
            f"¿Confirmás vender {amount_origin} {origin} para recibir en {target}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if r != QMessageBox.StandardButton.Yes:
            QMessageBox.information(self, "Vender moneda", "Operación cancelada.")
            return
        message = self.svc.vender_moneda(self.user, origin, target, amount_origin)
        QMessageBox.information(self, "Vender moneda", message)
        self.refresh_table()

    def logout(self):
        self.close()
        app = QApplication.instance()
        if app is not None:
            app.quit()
