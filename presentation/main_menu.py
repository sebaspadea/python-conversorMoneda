from decimal import Decimal
from business.account_service import AccountService
from business.models import Usuario, Cuenta
from data.rates_repository import RatesRepository
import time

class MainMenu:
    def __init__(self, user: Usuario):
        self.user = user
        self.account_service = AccountService()

    def run(self):
        while True:
            print("\n---------------------------------------------")
            print("\n=== MENÚ PRINCIPAL ===")
            print("1️⃣  - Depositar ARS")
            print("2️⃣  - Crear cuenta en nueva moneda")
            print("3️⃣  - Comprar moneda")
            print("4️⃣  - Vender moneda")
            print("5️⃣  - Ver saldos")
            print("6️⃣  - Cerrar sesión")
            option = input("Seleccione una opción: ").strip()

            if option == "1":
                self._depositar_ars()

            elif option == "2":
                self._crear_cuenta()

            elif option == "3":
                self._comprar_moneda()

            elif option == "4":
                self._vender_moneda()

            elif option == "5":
                self._ver_saldos()

            elif option == "6":
                print("\n🔄 Cerrando sesión y volviendo al menú inicial...")
                break

            else:
                print("❌ Opción inválida. Intentá nuevamente.")

    def _depositar_ars(self):
        print("\n--- Depósito de ARS ---")
        monto = input("Ingrese monto en ARS a depositar: ").strip()
        mensaje = self.account_service.depositar_ars(self.user, monto)
        print(mensaje)
        input("\nApreta Enter para volver al Menú Principal...")

    def _crear_cuenta(self):
        print("\n--- Crear cuenta en nueva moneda ---")
        moneda = input("Ingrese el código de la moneda (ej: USD, EUR): ").strip().upper()
        rates_str = RatesRepository.load_rates()
        if moneda in self.user.cuentas:
            print(f"❌ Ya tenés una cuenta en {moneda}.")
        elif moneda not in rates_str.keys():
            print(f"❌ La moneda '{moneda}' no está disponible. Por favor, ingresá una moneda válida.")
        else:
            self.user.cuentas[moneda] = Cuenta(moneda, Decimal("0.00"))
            self.account_service.repo.save_user(self.user)
            print(f"✅ Cuenta en {moneda} creada con saldo 0.00.")
        input("\nApreta Enter para volver al Menú Principal...")

    def _comprar_moneda(self):
        print("\n--- Compra de moneda ---")
        moneda_origen = input("Moneda de origen (ej: ARS): ").strip().upper()
        moneda_destino = input("Moneda destino (ej: USD): ").strip().upper()
        monto_destino = input(f"Cantidad de {moneda_destino} a comprar: ").strip()

        if not self.confirmar_operacion():
            print("\n❌ Operación cancelada.")
            print("\nVolviendo al Menú Principal...")
            return
        else:
            mensaje = self.account_service.comprar_moneda(
                self.user, moneda_origen, moneda_destino, monto_destino
            )
            print(mensaje)
            input("\nApreta Enter para volver al Menú Principal...")

    def _vender_moneda(self):
        print("\n--- Venta de moneda ---")
        moneda_origen = input("Moneda de origen (ej: USD): ").strip().upper()
        moneda_destino = input("Moneda destino (ej: ARS): ").strip().upper()
        monto_origen = input(f"Monto en {moneda_origen} a vender: ").strip()

        if not self.confirmar_operacion():
            print("\n❌ Operación cancelada.")
            print("\nVolviendo al Menú Principal...")
            return
        else:
            mensaje = self.account_service.vender_moneda(
                self.user, moneda_origen, moneda_destino, monto_origen
            )
            print(mensaje)
            input("\nApreta Enter para volver al Menú Principal...")

    def _ver_saldos(self):
        print("\n--- Saldo de todas las cuentas ---")
        for moneda, cuenta in self.user.cuentas.items():
            print(f"- {moneda}: {cuenta.saldo}")
        input("\nApreta Enter para volver al Menú Principal...")


    def confirmar_operacion(self) -> bool:
        tinicio = time.time()
        rta = input("Estas seguro que desea realizar la compra? (S/N)\n")

        if (time.time() - tinicio) > 120:
            rta = 'N'
        if rta in ('s','S','si','Si'):
            print("\nOperación confirmada.")
            return True
        else:
            return False
