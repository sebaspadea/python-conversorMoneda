import getpass
from business.authentication import Authenticator
from presentation.main_menu import MainMenu
from data.rates_repository import RatesRepository

class InitFlow:
    def __init__(self):
        self.auth = Authenticator()
        self.rates_repo = RatesRepository()

    def enter_credentials(self, is_register=False):
        username = input("\n👤 Usuario: ").strip()

        if is_register:
            while True:
                password = getpass.getpass("🔐 Ingresá tu contraseña: ")
                valido, mensaje = self.auth.validar_password(password)
                if not valido:
                    print(f"❌ {mensaje}")
                    continue

                repeat_password = getpass.getpass("🔁 Repitá la contraseña: ")
                if password != repeat_password:
                    print("❌ Las contraseñas no coinciden. Intentá nuevamente.")
                    continue
                break
        else:
            password = getpass.getpass("🔐 Ingresá tu contraseña: ")

        return username, password

    def start(self):
        while True:
            print("\n---------------------------------------------")
            print("😁 Bienvenido. ¿Qué desea hacer?")
            print("1️⃣  - Login")
            print("2️⃣  - Registro")
            print("3️⃣  - Salir")
            print("---------------------------------------------")
            option = input("Seleccione una opción: ").strip()

            if option == "1":
                username, password = self.enter_credentials(is_register=False)
                result, message, user = self.auth.login(username, password)
                print(message)

                if result:
                    self.rates_repo.load_rates()
                    print(f"\n🔒 Usuario autenticado: {user.username}")
                    MainMenu(user).run()

            elif option == "2":
                username, password = self.enter_credentials(is_register=True)
                message = self.auth.register(username, password)
                print(message)

            elif option == "3":
                print("👋 Hasta luego.")
                break

            else:
                print("❌ Opción inválida. Intentá nuevamente.")
