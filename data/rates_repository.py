from decimal import Decimal, InvalidOperation
import requests
import json
import os

class RatesRepository:
    RATES_FILE = "rates.json"
    API_KEY = "cf7fdde7e933468592a4e6b8c8852726"
    RATES_URL = f"https://api.currencyfreaks.com/v2.0/rates/latest?apikey={API_KEY}"

    @staticmethod
    def save_rates():
        try:
            respuesta = requests.get(RatesRepository.RATES_URL, timeout=10)
            respuesta.raise_for_status()
            data = respuesta.json()
            rates = data.get("rates", {})
            with open(RatesRepository.RATES_FILE, "w", encoding="utf-8") as f:
                json.dump(rates, f, indent=2, ensure_ascii=False)
            return True, ""
        except Exception as e:
            return False, f"Error al descargar cotizaciones: {e}"

    @staticmethod
    def load_rates():
        if not os.path.exists(RatesRepository.RATES_FILE):
            RatesRepository.save_rates()

        try:
            with open(RatesRepository.RATES_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    @staticmethod
    def getRates(monedaOrigen: str, monedaDestino: str) -> tuple[tuple[Decimal, Decimal], str]:
        monedaOrigen = monedaOrigen.upper()
        monedaDestino = monedaDestino.upper()
        url = f"{RatesRepository.RATES_URL}&symbols={monedaOrigen},{monedaDestino}"

        try:
            respuesta = requests.get(url, timeout=10)
            respuesta.raise_for_status()
            data = respuesta.json()
        except requests.RequestException as e:
            return None, f"Error de red o al consultar la API: {e}"
        except ValueError:
            return None, "La respuesta de la API no es un JSON válido."

        rates = data.get("rates", {})
        if not rates:
            return None, "No hay cotizaciones disponibles en la respuesta."

        if monedaOrigen not in rates:
            return None, f"La moneda origen '{monedaOrigen}' no existe."
        if monedaDestino not in rates:
            return None, f"La moneda destino '{monedaDestino}' no existe."

        try:
            rateOrigen = Decimal(rates[monedaOrigen])
            rateDestino = Decimal(rates[monedaDestino])
        except (InvalidOperation, TypeError):
            return None, "Error al convertir las cotizaciones a Decimal."

        return (rateOrigen, rateDestino), ""
