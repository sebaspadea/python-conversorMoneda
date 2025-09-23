import json
from pathlib import Path
from business.models import Usuario, Cuenta

USERS_DIR = Path("users")
USERS_DIR.mkdir(exist_ok=True)

class UserRepository:
    def load_user(self, username: str) -> Usuario | None:
        username_norm = username.lower()
        file_path = USERS_DIR / f"{username_norm}.json"
        if not file_path.exists():
            return None

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return Usuario.from_dict(data)
        except Exception:
            return None

    def save_user(self, usuario: Usuario):
        username_norm = usuario.username.lower()
        file_path = USERS_DIR / f"{username_norm}.json"
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(usuario.to_dict(), f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"\n❌ Error al guardar usuario '{usuario.username}': {e}")
