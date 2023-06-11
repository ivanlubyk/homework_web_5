import aiohttp
import asyncio
import argparse
from datetime import datetime, timedelta
from tabulate import tabulate

API_URL = "https://api.privatbank.ua/p24api/exchange_rates?json&date="

async def get_exchange_rates(date):
    url = f"{API_URL}{date}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                raise ValueError("Помилка отримання курсів валют.")
            data = await response.json()
            return data

def get_dates(num_days):
    dates = []
    today = datetime.now().date()
    for i in range(num_days):
        date = today - timedelta(days=i)
        dates.append(date.strftime("%d.%m.%Y"))
    return dates

def format_exchange_rates(rates):
    formatted_rates = []
    for rate in rates:
        date = rate["date"]
        currencies = rate["exchangeRate"]
        filtered_currencies = {currency["currency"]: {"sale": currency.get("saleRate"), "purchase": currency.get("purchaseRate")} for currency in currencies if currency["currency"] in ["USD", "EUR"]}
        formatted_rate = {date: filtered_currencies}
        formatted_rates.append(formatted_rate)
    return formatted_rates

async def main(num_days):
    if num_days > 10:
        print("Error: Кількість днів не може перевищувати 10.")
        return

    dates = get_dates(num_days)
    tasks = [get_exchange_rates(date) for date in dates]
    exchange_rates = await asyncio.gather(*tasks)
    formatted_rates = format_exchange_rates(exchange_rates)

    table = []
    for rate in formatted_rates:
        date = next(iter(rate))
        currencies = rate[date]
        table.append([date, currencies["USD"]["sale"], currencies["USD"]["purchase"], currencies["EUR"]["sale"], currencies["EUR"]["purchase"]])

    headers = ["Дата", "USD Купівля", "USD Продаж", "EUR Купівля", "EUR Продаж"]
    print(tabulate(table, headers, tablefmt="fancy_grid"))

#get_exchange_rates: Функція, яка отримує курси валют з API ПриватБанку.
#get_dates: Функція, яка отримує список дат на основі кількості днів.
#format_exchange_rates: Функція, яка форматує отримані курси валют.
#main: Основна функція, яка виконує усі необхідні кроки, включаючи отримання курсів валют, форматування їх і виведення у вигляді таблички.
#parser: Об'єкт парсера командного рядка для отримання кількості днів.
#args.num_days: Кількість днів, введена користувачем через командний рядок.

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Отримайте курси обміну євро та доларів США в API ПриватБанку.")
    parser.add_argument("num_days", type=int, help="Кількість днів для отримання курсів валют (макс.: 10)")
    args = parser.parse_args()

    asyncio.run(main(args.num_days))
