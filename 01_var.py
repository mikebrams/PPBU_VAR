from tkinter import *
from tkinter import ttk
from tkinter import messagebox as mb
import requests
from datetime import datetime
import copy
import random
from time import sleep


def target_field_update(event=None):
    if crypto_json:
        item = crypto_combo.get()
        base = crypto[item]
        try:
            rate = crypto_json[base]['usd']
            target_field.config(text=f'{item} = {rate:>10,.2f} USD')
        except KeyError:
            target_field.config(text=f'{'___'} = {'_' * 7}.00 USD')
            change24_value.config(text='-', fg='black')
            last_change_value.config(text='-', fg='black')
            mb.showerror('Ошибка', f'Валюта {item} отсутствует в ответе API')
    else:
        target_field.config(text='Ошибка при загрузке курсов криптовалют', font=('Verdana', 11))

    change_24_update()
    change_last_update()


def change_24_update():
    if crypto_json:
        item = crypto_combo.get()
        base = crypto[item]
        try:
            value = crypto_json[base]['usd_24h_change']
            if value > 0:
                change24_value.config(text=f'↑ {value:+.2f} %', fg='green')
            elif value < 0:
                change24_value.config(text=f'↓ {value:.2f} %', fg='red')
            else:
                change24_value.config(text=f'= {value:.2f} %', fg='black')
        except KeyError:
            change24_value.config(text='-', fg='black')
    else:
        change24_value.config(text='-', fg='black')


def change_last_update():
    if crypto_json and previous_crypto_json:
        item = crypto_combo.get()
        base = crypto[item]
        try:
            rate_prev = previous_crypto_json[base]['usd']
            rate = crypto_json[base]['usd']
            change = (rate - rate_prev) / rate_prev * 100
            if change > 0:
                last_change_value.config(text=f'↑ {change:+.2f} %', fg='green')
            elif change < 0:
                last_change_value.config(text=f'↓ {change:.2f} %', fg='red')
            else:
                last_change_value.config(text=f'= {change:.2f} %', fg='black')
        except KeyError:
            last_change_value.config(text='-', fg='black')
    else:
        last_change_value.config(text='-', fg='black')


def auto_refresh():
    """Функция автоматического обновления главного окна программы
    через произвольный период времени - 45-60 сек - и загрузки новых котировок"""
    target_field.config(text='Загрузка курсов с сайта coingecko.com... ')
    refresh_label.config(text='Загрузка... ')
    root.update()
    sleep(2)
    refresh_rates()
    root.after(random.randint(45000, 60000), auto_refresh)


def refresh_rates():
    global crypto_json
    global previous_crypto_json

    previous_crypto_json = copy.deepcopy(crypto_json)

    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        "ids": ",".join(crypto.values()),
        "vs_currencies": "usd",
        "include_24hr_change": "true",
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        crypto_json = response.json()

        now = datetime.now()
        refresh_label.config(text=f'Курсы обновлены:   {now.strftime("%d.%m.%Y")}   {now.strftime("%H:%M:%S")}')

    except Exception as e:
        mb.showerror('Ошибка', f'Ошибка загрузки курсов: {e}')
        target_field.config(text='Ошибка при загрузке курсов криптовалют', font=('Verdana', 11))
        refresh_label.config(text='Курсы обновлены:   --.--.----   --:--:--')

    target_field_update()


crypto = {
    'Bitcoin (BTC)': 'bitcoin',
    'Binancecoin (BNB)': 'binancecoin',
    'Bitcoin-cash (BCH)': 'bitcoin-cash',
    'Bittensor (TAO)': 'bittensor',
    'Ethereum (ETH)': 'ethereum',
    'Hyperliquid (HYPE)': 'hyperliquid',
    'Monero (XMR)': 'monero',
    'Pax-gold (PAXG)': 'pax-gold',
    'Quant-network (QNT)': 'quant-network',
    'Solana (SOL)': 'solana',
    'Tether-gold (XAUT)': 'tether-gold',
    'Zcash (ZEC)': 'zcash'
}

crypto_json = {}
previous_crypto_json = {}

root = Tk()
root.title('Курсы популярных криптовалют')
w = root.winfo_screenwidth()
h = root.winfo_screenheight()
w2 = w // 4
h2 = h // 3
root.geometry(f'410x400+{w2}+{h2}')

# frame1 -------------------------------------------
frame1 = Frame(bg='lightgray')
frame1.pack(padx=10, pady=4, fill='both')

base_l = Label(frame1, text='Список популярных криптовалют', font=('Verdana', 10),
               bg='lightgray')  # Заголовок выпадающего списка
base_l.pack(pady=(10, 5))
crypto_combo = ttk.Combobox(frame1, values=list(crypto.keys()), state='readonly')  # Выпадающий список криптовалют
crypto_combo.current(0)
crypto_combo.pack(padx=10, pady=(5, 10), fill='both')
crypto_combo.bind('<<ComboboxSelected>>', target_field_update)

# frame2 -------------------------------------------
frame2 = Frame(bg='lightgray')
frame2.pack(padx=10, pady=4, fill='both')

target_l = Label(frame2, text='Целевая валюта', bg='lightgray', font=('Verdana', 10))
target_l.pack(padx=10, pady=(10, 5))

target_USD = Label(frame2, text='USD', bg='lightgray', font=('Verdana', 10))
target_USD.pack(padx=10, pady=(5, 10))

# frame3 -------------------------------------------
frame3 = Frame(bg='lightgray')
frame3.pack(padx=10, pady=(4, 0), fill='both')

target_field = Label(frame3, text='Загрузка курсов с сайта coingecko.com... ', font=('Verdana', 11, 'bold'), height=3,
                     bg='Lavender')  # Поле для вывода текущего курса
target_field.pack(padx=10, pady=10, fill='both')

# frame4 -------------------------------------------
frame4 = Frame(bg='lightgray')
frame4.pack(padx=10, pady=(0, 4), fill='both')

change_label = Label(frame4, text='Изменение курса за последние 24 часа', bg='lightgray', font=('Verdana', 10))
change_label.grid(row=0, column=0, padx=(10, 0), pady=(5, 5), sticky='w')

change24_value = Label(frame4, text='0.00 %', bg='lightgray', font=('Verdana', 10, 'bold'), width=8)
change24_value.grid(row=0, column=2, sticky='e')

last_change_label = Label(frame4, text='Изменение курса c предыдущего запроса', bg='lightgray', font=('Verdana', 10))
last_change_label.grid(row=1, column=0, padx=(10, 0), pady=(5, 10), sticky='w')

last_change_value = Label(frame4, text='0.00 %', bg='lightgray', font=('Verdana', 10, 'bold'), width=8)
last_change_value.grid(row=1, column=2, sticky='e')

# -------------------------------------------------
refresh_btn = Button(text='Обновить курсы для списка криптовалют', command=refresh_rates, bg='lightgray',
                     font=('Verdana', 10))
refresh_btn.pack(padx=10, pady=(4, 5), fill='both')

# -------------------------------------------------
refresh_label = Label(text='Загрузка... ', fg='DimGray')
refresh_label.pack(pady=(5, 0))

# root.after(1500, auto_refresh)
auto_refresh()

root.mainloop()
