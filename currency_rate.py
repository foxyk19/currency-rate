import requests

url = "https://www.cbr-xml-daily.ru/daily_json.js"
try:
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    data = response.json()
except requests.RequestException:
    print("Ошибка сети или недоступность сервера. Пожалуйста, проверьте подключение к интернету и попробуйте снова.")
else:
    usd = data["Valute"]["USD"]
    eur = data["Valute"]["EUR"]
    print(f"USD: {usd['Value']:.2f} руб.")
    print(f"EUR: {eur['Value']:.2f} руб.")
