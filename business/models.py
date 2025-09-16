from decimal import Decimal

class Cuenta:
    def __init__(self, moneda: str, saldo: Decimal):
        self.moneda = moneda.upper()
        self.saldo = saldo

    def to_dict(self) -> dict:
        return {
            "moneda": self.moneda,
            "saldo": str(self.saldo)
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Cuenta":
        return cls(data["moneda"], Decimal(data["saldo"]))


class Usuario:
    def __init__(self, username: str, password_hash: str, cuentas: dict[str, Cuenta]):
        self.username = username.lower()
        self.password_hash = password_hash
        self.cuentas = cuentas

    def to_dict(self) -> dict:
        return {
            "username": self.username,
            "passwordHash": self.password_hash,
            "cuentas": {
                moneda: cuenta.to_dict()
                for moneda, cuenta in self.cuentas.items()
            }
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Usuario":
        cuentas_dict = {}
        for moneda, sub in data.get("cuentas", {}).items():
            cuentas_dict[moneda] = Cuenta.from_dict(sub)
        return cls(
            data["username"],
            data.get("passwordHash", ""),
            cuentas_dict
        )
