from tkinter import *
from tkinter import ttk
from tkinter import messagebox as mb
import requests
from datetime import datetime
import copy
import random
from time import sleep
import pprint
import matplotlib.pyplot as plt


def target_field_update(event=None):
    """Обновляет основной курс выбранной из списка криптовалюты"""
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
        target_field.config(text='Ошибка при загрузке курсов', font=('Verdana', 11))

    change_24_update()
    change_last_update()
    add_to_chart()
    root.after(500, diagram)


def change_24_update():
    """Показывает изменение курса за последние 24 часа в %"""
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
    """Показывает изменение курса относительно предыдущего обновления в %"""
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



def add_to_chart():
    """Создание словаря изменений котировок для графика"""
    if crypto_json:
        for base_cur in crypto.values():
            if base_cur not in crypto_json:
                continue
            else:
                value = crypto_json[base_cur]['usd_24h_change']
                chart.setdefault(base_cur, {'Изменение за 24 часа': [], 'Изменение с предыдущего запроса': [0.00]})

                if len(chart[base_cur]['Изменение за 24 часа']) < 3:
                    chart[base_cur]['Изменение за 24 часа'].append(round(value, 2))
                else:
                    chart[base_cur]['Изменение за 24 часа'].pop(0)
                    chart[base_cur]['Изменение за 24 часа'].append(round(value, 2))

    if previous_crypto_json:
        for base_cur in crypto.values():
            if base_cur not in crypto_json and base_cur not in previous_crypto_json:
                continue
            else:
                rate_prev = previous_crypto_json[base_cur]['usd']
                rate = crypto_json[base_cur]['usd']
                change = (rate - rate_prev) / rate_prev * 100

                if len(chart[base_cur]['Изменение с предыдущего запроса']) < 3:
                    chart[base_cur]['Изменение с предыдущего запроса'].append(round(change, 2))
                else:
                    chart[base_cur]['Изменение с предыдущего запроса'].pop(0)
                    chart[base_cur]['Изменение с предыдущего запроса'].append(round(change, 2))


    # pprint.pprint(chart)



def diagram():
    plt.figure(figsize=(10, 5))

    print(chart)
    base_c = crypto_combo.get()
    item = crypto[base_c]
    print(item)

    # Рисуем графики
    plt.plot(chart[item]['Изменение за 24 часа'],
             marker='o', label='за 24 часа')

    plt.plot(chart[item]['Изменение с предыдущего запроса'],
             marker='o', label='с предыдущего запроса')

    # Настраиваем оси
    plt.xlim(-0.3, 9.3)  # Всего 10 позиций
    plt.xticks(range(10))  # Деления от 0 до 9

    plt.title(f'Изменение курса {base_c}')
    plt.xlabel('Количество измерений')
    plt.ylabel('Изменение, %')

    plt.grid(True)
    plt.legend()
    plt.show()






def start_refresh():
    """Старт обновления курсов с сайта и запуск таймера обратного отсчета на кнопке"""
    global time_to_refresh, countdown

    countdown = None

    target_field.config(text='Загрузка курсов с сайта coingecko.com... ')
    refresh_btn.config(text='Обновление...')
    refresh_label.config(text='Загрузка... ')
    refresh_btn.config(state='disabled')

    root.update()
    sleep(2)
    refresh_rates()

    refresh_btn.config(state='normal')

    time_to_refresh = random.randint(35, 40)
    print('Старт')
    countdown = True
    button_countdown()


def button_countdown():
    """Таймер обратного отсчета на кнопке обновления курсов валют"""
    global time_to_refresh

    toggle_flag = flag.get()

    if countdown is None:
        return

    if toggle_flag:
        print(time_to_refresh)
        time_to_refresh -= 1
        if time_to_refresh > 0:
            refresh_btn.config(text=f'Автообновление курсов через {time_to_refresh} сек.')
            root.after(1000, button_countdown)
        else:
            refresh_btn.config(text='Обновление...')
            root.after(time_to_refresh * 1000, start_refresh)
    else:
        refresh_btn.config(text='Обновить курсы для списка криптовалют')


def refresh_rates():
    """Получение курсов с сайта в формате json"""
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
        refresh_label.config(text=f'Данные обновлены:   {now.strftime("%d.%m.%Y")}   {now.strftime("%H:%M:%S")}')

    except Exception as e:
        mb.showerror('Ошибка', f'Ошибка загрузки курсов: {e}')
        target_field.config(text='Ошибка при загрузке курсов', font=('Verdana', 11))
        refresh_label.config(text='Данные обновлены:   --.--.----   --:--:--')

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

chart = {}  # словарь изменения курса за 24 часа и с предыдущего запроса
crypto_json = {}  # json-файл полученный от сервера
previous_crypto_json = {}  # копия предыдущего json-файла для сравнения курсов
time_to_refresh = 0
countdown = None

root = Tk()
root.title('Курсы популярных криптовалют')
w = root.winfo_screenwidth()
h = root.winfo_screenheight()
w2 = w // 6
h2 = h // 4
root.geometry(f'910x430+{w2}+{h2}')

# Left frame -------------------------------------------
left = Frame(root, width=410)
left.pack(side="left", fill="y")
left.pack_propagate(False)  # не сжиматься под содержимое

# frame1 -------------------------------------------
frame1 = Frame(left, bg='lightgray')
frame1.pack(padx=10, pady=4, fill='both')

base_l = Label(frame1, text='Список криптовалют', font=('Verdana', 10),
               bg='lightgray')  # Заголовок выпадающего списка
base_l.pack(pady=(10, 5))
crypto_combo = ttk.Combobox(frame1, values=list(crypto.keys()), state='readonly')  # Выпадающий список криптовалют
crypto_combo.current(0)
crypto_combo.pack(padx=10, pady=(5, 10), fill='both')
crypto_combo.bind('<<ComboboxSelected>>', target_field_update)

# frame2 -------------------------------------------
frame2 = Frame(left, bg='lightgray')
frame2.pack(padx=10, pady=4, fill='both')

target_l = Label(frame2, text='Целевая валюта', bg='lightgray', font=('Verdana', 10))
target_l.pack(padx=10, pady=(10, 5))

target_USD = Label(frame2, text='USD', bg='lightgray', font=('Verdana', 10))
target_USD.pack(padx=10, pady=(5, 10))

# frame3 -------------------------------------------
frame3 = Frame(left, bg='lightgray')
frame3.pack(padx=10, pady=(4, 0), fill='both')

target_field = Label(frame3, text='Загрузка курсов с сайта coingecko.com... ', font=('Verdana', 11, 'bold'), height=3,
                     bg='Lavender')  # Поле для вывода текущего курса
target_field.pack(padx=10, pady=10, fill='both')

# frame4 -------------------------------------------
frame4 = Frame(left, bg='lightgray')
frame4.pack(padx=10, pady=(0, 4), fill='both')

change_label = Label(frame4, text='Изменение курса за последние 24 часа', bg='lightgray', font=('Verdana', 10))
change_label.grid(row=0, column=0, padx=(10, 0), pady=(5, 5), sticky='w')

change24_value = Label(frame4, text='-', bg='lightgray', font=('Verdana', 10, 'bold'), width=8)
change24_value.grid(row=0, column=2, sticky='e')

last_change_label = Label(frame4, text='Изменение курса c предыдущего запроса', bg='lightgray', font=('Verdana', 10))
last_change_label.grid(row=1, column=0, padx=(10, 0), pady=(5, 10), sticky='w')

last_change_value = Label(frame4, text='-', bg='lightgray', font=('Verdana', 10, 'bold'), width=8)
last_change_value.grid(row=1, column=2, sticky='e')

# frame5 -------------------------------------------
frame5 = Frame(left, bg='lightgray')
frame5.pack(padx=10, pady=(4, 0), fill='both')

refresh_btn = Button(frame5, text='Обновление...',
                     command=start_refresh, bg='Lavender', font=('Verdana', 10))
refresh_btn.pack(padx=10, pady=(10, 0), fill='both')

flag = BooleanVar(value=True)
auto_scenario = Checkbutton(frame5, text="Включить / отключить автообновление",
                            bg='lightgray', variable=flag, offvalue=False)
auto_scenario.pack(pady=3)

refresh_label = Label(frame5, text='Загрузка... ', fg='DimGray')
refresh_label.pack(pady=(4, 0), fill='both')

# frame6 right--------------------------------------
frame6 = Frame(root, bg='lightgray')
frame6.pack(side="left", padx=(0, 10), pady=(4, 10), fill='both', expand=True)

start_refresh()

root.mainloop()



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


chart = {'binancecoin': {'Изменение за 24 часа': [0.44368187197112374],
                 'Изменение с предыдущего запроса': [0]},
 'bitcoin': {'Изменение за 24 часа': [-0.6353413888620077],
             'Изменение с предыдущего запроса': [0]},
 'bitcoin-cash': {'Изменение за 24 часа': [-2.9922718797642047],
                  'Изменение с предыдущего запроса': [0]},
 'bittensor': {'Изменение за 24 часа': [-0.055168515669738356],
               'Изменение с предыдущего запроса': [0]},
 'ethereum': {'Изменение за 24 часа': [-1.6612432298216158],
              'Изменение с предыдущего запроса': [0]},
 'hyperliquid': {'Изменение за 24 часа': [-0.2041200824058869],
                 'Изменение с предыдущего запроса': [0]},
 'monero': {'Изменение за 24 часа': [-8.31115664834746],
            'Изменение с предыдущего запроса': [0]},
 'pax-gold': {'Изменение за 24 часа': [-0.712822548362917],
              'Изменение с предыдущего запроса': [0]},
 'quant-network': {'Изменение за 24 часа': [-7.419764625295189],
                   'Изменение с предыдущего запроса': [0]},
 'solana': {'Изменение за 24 часа': [-2.7409496011289636],
            'Изменение с предыдущего запроса': [0]},
 'tether-gold': {'Изменение за 24 часа': [-0.7226662295295294],
                 'Изменение с предыдущего запроса': [0]},
 'zcash': {'Изменение за 24 часа': [-5.872940188517272],
           'Изменение с предыдущего запроса': [0]}}

item = crypto[crypto_combo.get()]
print(item)

plt.plot(chart[item]['Изменение за 24 часа'],
         marker='o', label='за 24 часа')