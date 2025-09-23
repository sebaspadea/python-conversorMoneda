import bcrypt
from data.user_repository import UserRepository
from business.models import Usuario, Cuenta
from decimal import Decimal

class Authenticator:
    def __init__(self):
        self.user_repo = UserRepository()

    def hash_password(self, password: str) -> str:
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    def check_password(self, password: str, hashed: str) -> bool:
        return bcrypt.checkpw(password.encode(), hashed.encode())

    def register(self, username: str, password: str) -> str:
        username_norm = username.lower()

        if username_norm == "":
            return "\n🚫 El nombre de usuario no puede estar vacío."

        existing = self.user_repo.load_user(username_norm)
        if existing is not None:
            return "\n🚫 El usuario ya existe."

        hashed_pw = self.hash_password(password)

        cuentas_iniciales = {"ARS": Cuenta("ARS", Decimal("0.00"))}
        nuevo_usuario = Usuario(username_norm, hashed_pw, cuentas_iniciales)

        self.user_repo.save_user(nuevo_usuario)
        return "\n✅ Usuario registrado exitosamente."

    def login(self, username: str, password: str) -> tuple[bool, str, Usuario | None]:
        username_norm = username.lower()
        user = self.user_repo.load_user(username_norm)
        if user is None:
            return False, "\n🤷‍♂️ Usuario no encontrado.", None

        if not self.check_password(password, user.password_hash):
            return False, "\n🔑 Contraseña incorrecta.", None

        return True, f"\n🙌 Login exitoso. ¡Bienvenido, {username_norm}!", user

    def validar_password(self, password: str) -> tuple[bool, str]:
        if len(password) < 8:
            return False, "🔒 La contraseña debe tener al menos 8 caracteres."
        if " " in password:
            return False, "🚫 La contraseña no puede contener espacios."
        if not any(c.isupper() for c in password):
            return False, "🆙 La contraseña debe contener al menos una letra mayúscula."
        if not any(c.isdigit() for c in password):
            return False, "🔢 La contraseña debe contener al menos un número."
        return True, ""
