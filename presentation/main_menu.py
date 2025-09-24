# presentation/main_menu.py
from PyQt6.QtWidgets import QMainWindow, QTableWidgetItem, QInputDialog, QMessageBox, QDialog, QApplication
from decimal import Decimal
from business.account_service import AccountService
from business.models import Usuario, Cuenta
from data.rates_repository import RatesRepository
from presentation.screens.Main_ui import Ui_MainWindow
from presentation.screens.BuyDialog_ui import Ui_BuyDialog


class DialogComprar(QDialog, Ui_BuyDialog):
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

        self.btnAddAccount.clicked.connect(self._crear_cuenta)   # ahora pide moneda a mano
        self.btnDeposit.clicked.connect(self._depositar_ars)
        self.btnBuy.clicked.connect(self._comprar_moneda)
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
        moneda, ok = QInputDialog.getText(self, "Crear cuenta", "Código de moneda (ej: USD, EUR):")
        if not ok:
            return
        moneda = (moneda or "").strip().upper()
        if not moneda:
            QMessageBox.warning(self, "Crear cuenta", "Ingresá un código de moneda.")
            return

        rates = RatesRepository.load_rates()
        if moneda in self.user.cuentas:
            QMessageBox.warning(self, "Crear cuenta", f"Ya tenés una cuenta en {moneda}.")
            return
        if moneda not in rates.keys():
            QMessageBox.warning(self, "Crear cuenta", f"La moneda '{moneda}' no existe.")
            return

        self.user.cuentas[moneda] = Cuenta(moneda, Decimal("0.00"))
        self.svc.repo.save_user(self.user)
        QMessageBox.information(self, "Crear cuenta", f"Cuenta en {moneda} creada.")
        self._refresh_table()

    def _comprar_moneda(self):
        dlg = DialogComprar(self)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return

        origen = (dlg.txtFrom.text() or "").strip().upper()
        destino = (dlg.txtTo.text() or "").strip().upper()
        monto_dest = (dlg.txtAmount.text() or "").strip()

        if not origen or not destino or not monto_dest:
            QMessageBox.warning(self, "Comprar", "Completá todos los campos.")
            return
        if origen == destino:
            QMessageBox.warning(self, "Comprar", "Las monedas deben ser distintas.")
            return

        r = QMessageBox.question(
            self,
            "Confirmar compra",
            f"¿Confirmás comprar {monto_dest} {destino} pagando desde {origen}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if r != QMessageBox.StandardButton.Yes:
            QMessageBox.information(self, "Comprar", "Operación cancelada.")
            return

        mensaje = self.svc.comprar_moneda(self.user, origen, destino, monto_dest)
        QMessageBox.information(self, "Comprar", mensaje)
        self._refresh_table()

    def _logout(self):
        self.close()
        app = QApplication.instance()
        if app is not None:
            app.quit()
