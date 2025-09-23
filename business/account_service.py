from decimal import Decimal, InvalidOperation
from business.models import Cuenta, Usuario
from data.user_repository import UserRepository
from data.rates_repository import RatesRepository

class AccountService:
    def __init__(self):
        self.repo = UserRepository()

    def depositar_ars(self, user: Usuario, monto_str: str) -> str:
        try:
            dec_monto = Decimal(monto_str)
        except (InvalidOperation, ValueError):
            return "Monto inválido. Ingresá un número válido."

        if dec_monto <= 0:
            return "El monto debe ser mayor a 0."

        user.cuentas["ARS"].saldo += dec_monto
        self.repo.save_user(user)
        return f"✅ Depósito de {dec_monto} ARS exitoso. Nuevo saldo: {user.cuentas['ARS'].saldo}"

    def comprar_moneda(self, user: Usuario, moneda_origen: str, moneda_destino: str, monto_destino_str: str) -> str:
        moneda_origen = moneda_origen.upper()
        moneda_destino = moneda_destino.upper()

        if moneda_origen not in user.cuentas:
            return f"\nNo se puede realizar la operacion ya que no tenés cuenta en {moneda_origen}."

        if moneda_destino not in user.cuentas:
            return f"\nNo se puede realizar la operacion ya que no tenés cuenta en {moneda_destino}."

        try:
            monto_destino = Decimal(monto_destino_str)
        except (InvalidOperation, ValueError):
            return "Monto inválido. Ingresá un número válido para la cantidad de destino."

        if monto_destino <= 0:
            return "La cantidad de moneda destino debe ser mayor a 0."

        rates_tuple, err = RatesRepository.getRates(moneda_origen, moneda_destino)
        if rates_tuple is None:
            return err

        rate_origen, rate_destino = rates_tuple

        try:
            usd_necesarios = monto_destino / rate_destino
            origen_necesario = (usd_necesarios * rate_origen).quantize(Decimal("0.0001"))
        except (InvalidOperation, ZeroDivisionError):
            return "Error al calcular la conversión con las tasas obtenidas."

        saldo_disp = user.cuentas[moneda_origen].saldo
        if origen_necesario > saldo_disp:
            return f"Saldo insuficiente en {moneda_origen}. Necesitás {origen_necesario}, pero tenés {saldo_disp}."

        if moneda_destino not in user.cuentas:
            user.cuentas[moneda_destino] = Cuenta(moneda_destino, Decimal("0.0000"))

        user.cuentas[moneda_origen].saldo -= origen_necesario
        user.cuentas[moneda_destino].saldo += monto_destino

        self.repo.save_user(user)
        return f"✅ Compraste {monto_destino} {moneda_destino}, usando {origen_necesario} {moneda_origen}."

    def vender_moneda(self, user: Usuario, moneda_origen: str, moneda_destino: str, monto_origen_str: str) -> str:
        moneda_origen = moneda_origen.upper()
        moneda_destino = moneda_destino.upper()

        if moneda_origen not in user.cuentas:
            return f"\nNo se puede realizar la operacion ya que no tenés cuenta en {moneda_origen}."

        if moneda_destino not in user.cuentas:
            return f"\nNo se puede realizar la operacion ya que no tenés cuenta en {moneda_destino}."

        try:
            monto_origen = Decimal(monto_origen_str)
        except (InvalidOperation, ValueError):
            return "Monto inválido. Ingresá un número válido."

        if monto_origen <= 0:
            return "La cantidad a vender debe ser mayor a 0."

        saldo_disp = user.cuentas[moneda_origen].saldo
        if monto_origen > saldo_disp:
            return f"Saldo insuficiente en {moneda_origen}. Tenés {saldo_disp}, intentás vender {monto_origen}."

        rates_tuple, err = RatesRepository.getRates(moneda_origen, moneda_destino)
        if rates_tuple is None:
            return err

        rate_origen, rate_destino = rates_tuple

        try:
            usd_equiv = monto_origen / rate_origen
            destino_obtenido = (usd_equiv * rate_destino).quantize(Decimal("0.0001"))
        except (InvalidOperation, ZeroDivisionError):
            return "Error al calcular la conversión con las tasas obtenidas."

        if moneda_destino not in user.cuentas:
            user.cuentas[moneda_destino] = Cuenta(moneda_destino, Decimal("0.0000"))

        user.cuentas[moneda_origen].saldo -= monto_origen
        user.cuentas[moneda_destino].saldo += destino_obtenido

        self.repo.save_user(user)
        return f"✅ Vendiste {monto_origen} {moneda_origen} y recibiste {destino_obtenido} {moneda_destino}."
