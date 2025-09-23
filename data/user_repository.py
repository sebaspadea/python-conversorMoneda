import sqlobject as SO
from decimal import Decimal
from business.models import Usuario, Cuenta

DATABASE_URI = 'mysql://guest:1234@localhost:3306/tp_integrador_spadea_exchange?driver=pymysql&charset=utf8mb4'

__connection__ = SO.connectionForURI(DATABASE_URI)
SO.sqlhub.processConnection = __connection__

class Usuarios(SO.SQLObject):
    username     = SO.StringCol(length=50, unique=True)
    passwordHash = SO.StringCol()
    accounts     = SO.MultipleJoin('Cuentas', joinColumn='user_id')

class Cuentas(SO.SQLObject):
    currency = SO.StringCol(length=3)
    balance  = SO.StringCol()
    user     = SO.ForeignKey('Usuarios')

Usuarios.createTable(ifNotExists=True)
Cuentas.createTable(ifNotExists=True)

class UserRepository:
    def load_user(self, username: str) -> Usuario | None:
        try:
            usuario_db = Usuarios.selectBy(username=username.lower()).getOne()
        except SO.SQLObjectNotFound:
            return None

        cuentas = {
            acc.currency: Cuenta(acc.currency, Decimal(acc.balance))
            for acc in usuario_db.accounts
        }
        return Usuario(usuario_db.username, usuario_db.passwordHash, cuentas)

    def save_user(self, usuario: Usuario):
        try:
            usuario_db = Usuarios.selectBy(username=usuario.username).getOne()
        except SO.SQLObjectNotFound:
            usuario_db = Usuarios(
                username=usuario.username,
                passwordHash=usuario.password_hash
            )
        else:
            usuario_db.set(passwordHash=usuario.password_hash)

        db_accounts = {acc.currency: acc for acc in usuario_db.accounts}

        for moneda, cuenta in usuario.cuentas.items():
            if moneda in db_accounts:
                db_accounts[moneda].set(balance=str(cuenta.saldo))
            else:
                Cuentas(
                    currency=moneda,
                    balance=str(cuenta.saldo),
                    user=usuario_db
                )
