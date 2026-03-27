import pandas as pd
import numpy as np
from datetime import datetime as dt
from datetime import date as dte
from datetime import timedelta as td
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings("ignore", message="Workbook contains no default style.*")

futures = pd.read_excel('data/futures_ruonia.xlsx', engine='openpyxl').set_axis(['date', 'smth', 'ruonia_1m', 'ruonia_3m', 'ruonia_6m'], axis = 1).drop(['smth', 'ruonia_1m'], axis = 1)
dates_df = pd.read_excel('data/keyrate_dates.xlsx')
ruonia = pd.read_excel('data/ruonia.xlsx', engine='openpyxl').rename(columns = {'DT':'date', 'ruo':'ruonia'}).loc[:, ['date', 'ruonia']]
ruonia['date'] = [i.date() for i in ruonia['date']]
futures['date'] = [i.date() for i in futures['date']]

dates = [dt.strptime(i, '%d.%m.%Y').date() for i in dates_df['date']]
dates_pairs = [(i, j) for i, j in zip(dates[:-1], dates[1:])]

def diffrence(df):
    v = ((df.diff().iloc[1:, 1:])**2).sum().item()
    if v == 0:
        share_of_v = 1
    else:
        share_of_v = ((df.diff().iloc[1:, 1:])**2).iloc[-1].item()/((df.diff().iloc[1:, 1:])**2).sum().item()
    share_of_d = abs(abs((df.iloc[-1, 1:].item() - df.iloc[-2, 1:].item())) - abs((df.iloc[-1, 1:].item() - df.iloc[0, 1:].item())))
    return share_of_v, share_of_d
keyrate = pd.read_excel('data/keyrate.xlsx')
keyrate['date'] = [dt.strptime(i, '%d.%m.%Y') for i in keyrate['date']]
keyrate = keyrate.sort_values('date').copy()
keyrate['rate'] = keyrate['rate'].replace(',', '.', regex=True)
keyrate['rate'] = keyrate['rate'].astype(float).diff().iloc[1:].to_list() + [0.0]



increase_i = [i.date() for i in keyrate.loc[keyrate['rate'] > 0.0, 'date']]
decrease_i = [i.date() for i in keyrate.loc[keyrate['rate'] < 0.0, 'date']]
unchange_i = [i for i in dates if i not in increase_i + decrease_i]
data = []
for date in dates_pairs:
    i, j = date
    results = []
    results.append((j-i).days)
    r_now = ruonia.loc[(ruonia['date'] > i) & (ruonia['date'] <= j),:].copy(deep = True).reset_index(drop=True)
    r_now = diffrence(r_now)
    results.append(r_now[0])
    results.append(r_now[1].item())
    r_3m = futures.loc[(futures['date'] > i) & (futures['date'] <= j),:].copy(deep = True).reset_index(drop=True).loc[:, ['date', 'ruonia_3m']]
    r_3m = diffrence(r_3m)
    results.append(r_3m[0])
    results.append(r_3m[1])
    r_6m = futures.loc[(futures['date'] > i) & (futures['date'] <= j),:].copy(deep = True).reset_index(drop=True).loc[:, ['date', 'ruonia_6m']]
    r_6m = diffrence(r_6m)
    results.append(r_6m[0])
    results.append(r_6m[1])
    data += [results]

months_ru = ['Янв', 'Фев', 'Мар', 'Апр', 'Май', 'Июн', 
             'Июл', 'Авг', 'Сен', 'Окт', 'Ноя', 'Дек']

for year in range(2014, 2026):
    i = dte(year = year, month=1, day=1)
    j = dte(year = year+1, month=1, day=1)
    x_pos = [dte(year = year, month=m, day=1) for m in range(1, 13)]

    temp_df = ruonia.loc[(ruonia['date'] >= i) & (ruonia['date'] < j),:].copy(deep = True).reset_index(drop=True)
    plt.figure(figsize=(10,5))
    ruonia_plot, = plt.plot(temp_df['date'], temp_df['ruonia'], color='black', label='RUONIA')
    
    increase_y = [d for d in increase_i if i <= d < j]
    for idx, date in enumerate(increase_y):
        # Label ставим только для первой линии (idx == 0), иначе пустая строка
        lbl = 'Повышение ключевой ставки' if idx == 0 else ""
        plt.axvline(date, color='red', lw=2, linestyle='--', alpha=0.7, label=lbl)

    # Понижение (Синие)
    decrease_y = [d for d in decrease_i if i <= d < j]
    for idx, date in enumerate(decrease_y):
        lbl = 'Понижение ключевой ставки' if idx == 0 else ""
        plt.axvline(date, color='blue', lw=2, linestyle='--', alpha=0.7, label=lbl)

    # Без изменений (Оранжевые)
    unchange_y = [d for d in unchange_i if i <= d < j]
    for idx, date in enumerate(unchange_y):
        lbl = 'Сохранение ключевой ставки' if idx == 0 else ""
        plt.axvline(date, color='darkgoldenrod', lw=2.4, linestyle=':', alpha=0.7, label=lbl) # type: ignore
    plt.xticks(ticks=x_pos,  # type: ignore
           labels=months_ru, 
           rotation=45,    # Угол поворота в градусах
           ha='right') 
    plt.xlabel("Время")
    plt.ylabel("%")
    plt.legend()
    fig_name = f"RUONIA и решение по ключевой ставке в {year} году"
    plt.title(fig_name)
    
    plt.savefig(f'data/ruonia_plots/{fig_name}.jpeg')
res_df = pd.DataFrame(data, columns = ['Дни',
                              'Доля от квадратичного отклонения (RUONIA)',
                              'Доля от линейного изменения (RUONIA)',
                              'Доля от квадратичного отклонения (RUONIA 3м)',
                              'Доля от линейного изменения (RUONIA 3м)',
                              'Доля от квадратичного отклонения (RUONIA 6м)',
                              'Доля от линейного изменения (RUONIA 6м)']).describe()\
                              .set_axis(['кол-во',
                                         'среднее',
                                         'стандартное отклонение',
                                         'минимум',
                                         '1-ый квантиль',
                                         'медиана',
                                         '3-ий квантиль',
                                         'максимум'], axis = 0).round(4)
res_df['Дни'] = res_df['Дни'].round(0).copy()
res_df.iloc[0] = res_df.iloc[0].round(0).copy()
res_df.iloc[1:, 1:] = res_df.iloc[1:, 1:] * 100
print(res_df.to_latex())
res_df.to_excel('data/keyrate_decisions_contrib.xlsx')