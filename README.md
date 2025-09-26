# 💸 Wallet FX – Trabajo Práctico Integrador

Aplicación de escritorio desarrollada con **Python + PyQt6**, organizada en capas (business, data, presentation).
Permite gestionar cuentas en distintas monedas, realizar depósitos en ARS y operaciones de compra/venta de divisas.

---

## 🚀 Requisitos

- Python **3.10+** (recomendado 3.13)
- MySQL (con un esquema creado para la app)
- Qt Designer (para modificar interfaces `.ui`)

---

## ⚙️ Instalación

1. **Clonar el repositorio**

```bash
git clone https://github.com/usuario/proyecto.git
cd proyecto
```
2. **Crear y activar entorno virtual**

```bash
python -m venv .venv
source .venv/bin/activate   # Linux/Mac
.venv\Scripts\activate      # Windows
```
3. **Instalar dependencias**

```bash
pip install -r requirements.txt
```

## 🛢️ Base de datos

1. **Crear la base de datos**
```bash
mysql -u root -p -e "CREATE DATABASE tp_integrador_spadea_exchange;"
```

2. **Importar el dump incluido**
```bash
mmysql -u root -p tp_integrador_spadea_exchange < dump.sql
```

3. **Verificar credenciales en**
```bash
data/user_repository.py
```

**Por defecto:**
```bash
mysql://guest:1234@localhost/tp_integrador_spadea_exchange
```

## ▶️ Ejecución
```bash
python main.py
```

Al iniciar, verás el menú inicial con:
- Login
- Registro
- Salir
Tras iniciar sesión, accederás a la ventana principal para operar con cuentas y monedas.

## 📂 Estructura del proyecto
```bash
.
├── business/              # Lógica de negocio (services, autenticación, modelos)
├── data/                  # Persistencia (repositorios con MySQL / JSON)
├── presentation/          # UI con PyQt6
│   ├── screens/           # Archivos generados desde .ui (Qt Designer → pyuic6)
│   ├── init_flow.py       # Flujo inicial (login/registro)
│   └── main_menu.py       # Ventana principal con operaciones
├── dump.sql               # Dump inicial de la DB
├── main.py                # Punto de entrada de la app
└── README.md
```

## 🎨 Editar interfaces gráficas

- Modificar .ui con Qt Designer
- Generar su .py con:

```bash
pyuic6 -o presentation/screens/NOMBRE_ui.py presentation/ui/nombre.ui
```

## ✅ Funcionalidades

- Login / Registro con validación de contraseñas
- Depósito en ARS
- Creación de cuentas en nuevas monedas (validación contra cotizaciones)
- Compra de monedas
- Venta de monedas
- Persistencia en MySQL

## 📌 Notas
* Si MySQL usa caching_sha2_password, instalar:
```bash
pip install cryptography
```
* El archivo rates.json se genera automáticamente con datos de la API Currency Freaks al iniciar sesión.

## ✨ Autor
Sebastián Spadea – Tecnicatura Superior en Análisis de Sistemas
