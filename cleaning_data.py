import pandas as pd
import numpy as np

from datetime import datetime as dt
from datetime import timedelta as td

import os

# Получить путь к текущему .ipynb-файлу
BASE_DIR = os.path.dirname(__file__)



# Проверка
print("Текущая рабочая директория:", os.getcwd(), '\nОттуда буду брать данные, там должна быть папка data, а в ней данные по годам')

path = BASE_DIR + '\\data'

list_with_files= os.listdir(path)

cbrate_and_inflation = pd.read_excel(path + f'//{list_with_files[8]}', engine='openpyxl').set_axis(['date', 'key_rate', 'infl', 'target'], axis = 1)
cbrate_and_inflation['date'] = [i.split('.')[0] + '.' + i.split('.')[1] + '0' if  i.split('.')[1] == '202' else i for i in cbrate_and_inflation['date'].astype(str)]
cbrate_and_inflation['date'] = [dt.strptime(i, '%m.%Y') for i in cbrate_and_inflation['date'].astype(str)]

exchange_rate_data = pd.read_excel(path + f'//{list_with_files[0]}', engine='openpyxl').rename(columns={'Unnamed: 0':'name'}).set_index('name').rename_axis(None, axis=0)

ru_months = {
    '01':'Янв',
    '02':'Фев',
    '03':'Мар',
    '04':'Апр',
    '05':'Май',
    '06':'Июн',
    '07':'Июл',
    '08':'Авг',
    '09':'Сен',
    '10':'Окт',
    '11':'Ноя',
    '12':'Дек',
}
ru_months_r = {v:k for k, v in ru_months.items()}
dollar_m = exchange_rate_data.iloc[[
    0, 1, exchange_rate_data.index.to_list().index('Средний номинальный курс доллара США к рублю за период')
]].set_axis(['year', 'month', 'dollar_m'], axis = 0).T
dollar_m['date'] = [dt(year = int(y), month = int(ru_months_r[m]), day = 1) for y, m in zip(dollar_m['year'], dollar_m['month'])]
dollar_m = dollar_m.drop(['month', 'year'], axis = 1).reset_index(drop = True)


monetary_agg = pd.read_excel(path + f'//{list_with_files[1]}', engine='openpyxl').rename(columns={'Денежные агрегаты*, млрд руб.':'name'}).set_index('name').rename_axis(None, axis=0)
m_agg = monetary_agg.loc[[
    'Денежный агрегат М0', 'Денежный агрегат М1', 'Денежный агрегат М2'
]].set_axis(['m0', 'm1', 'm2']).T.reset_index().rename(columns = {'index':'date'})


credits = pd.read_excel(path + f'//{list_with_files[5]}', engine='openpyxl').rename(columns={'Баланс кредитных организаций, млн руб.*':'name'}).set_index('name').rename_axis(None, axis=0)
credits_hh = credits.loc[[
    'Кредиты и займы, предоставленные  населению (домашним хозяйствам)'
]].set_axis(['credits_hh']).T.reset_index().rename(columns = {'index':'date'})


pmi = pd.read_excel(path + f'//{list_with_files[6]}', sheet_name=9, engine='openpyxl').iloc[3:,:3].set_axis(['date', 'PMI_manufacturing', 'PMI_service'], axis = 1)\
            .reset_index(drop=True)
pmi['date'] = [pd.Timestamp(i) for i in pmi['date']]

ruonia = pd.read_excel(path + f'//{list_with_files[7]}', engine='openpyxl').set_axis(['date', 'ruonia'], axis = 1)
ruonia['date'] = [pd.Timestamp(i) for i in ruonia['date']]
ruonia_m = ruonia.groupby(ruonia["date"].dt.to_period("M")).mean().reset_index(drop=True)
ruonia_m['date'] = [pd.Timestamp(dt(year = i.year, month = i.month, day = 1)) for i in ruonia_m['date']]


inf_exp_all_data = pd.read_excel(path + f'//{list_with_files[9]}', engine='openpyxl', sheet_name = 'Данные за все годы')\
                    .rename(columns={'Данные в таблице приводятся в % от всех опрошенных, если не указано иное.':'name'}).set_index('name').rename_axis(None, axis=0)

inf_exp_all_data = inf_exp_all_data.rename(index = {inf_exp_all_data.index.to_list()[0]:'date'})
inf_exp = inf_exp_all_data.loc[[
    'date', 'ожидаемая инфляция среди тех, кто имеет сбережения (в %)', 'ожидаемая инфляция среди тех, кто не имеет сбережений (в %)' 
]].iloc[[0,4, 5]].T.reset_index(drop = True).set_axis(['date', 'pi_e_ws', 'pi_e_wos'], axis = 1)
inf_exp['date'] = [pd.Timestamp(i) for i in inf_exp['date']]

roisfix = pd.read_excel(path + f'//{list_with_files[10]}', engine='openpyxl').iloc[1:, :]\
    .set_axis(['date', 'ruonia_1w', 'ruonia_2w', 'ruonia_1m', 'ruonia_2m', 'ruonia_3m', 'ruonia_6m', 'ruonia_1y', 'ruonia_2y'], axis = 1).fillna(0.0)
roisfix['date'] = [pd.Timestamp(i) for i in roisfix['date']]
roisfix.iloc[:, 1:] = roisfix.iloc[:, 1:].replace('--', '0', regex=True).replace(',', '.', regex=True).astype(float)
roisfix_m = roisfix.groupby(roisfix["date"].dt.to_period("M")).mean().reset_index(drop=True)
roisfix_m['date'] = [pd.Timestamp(dt(year = i.year, month = i.month, day = 1)) for i in roisfix_m['date']]

brent = pd.read_excel(path + f'//{list_with_files[11]}').iloc[:, :2].set_axis(['date', 'price_brent'], axis = 1)
brent['date'] = [pd.Timestamp(i) for i in brent['date']]
brent_m = brent.groupby(brent["date"].dt.to_period("M")).mean().reset_index(drop=True)
brent_m['date'] = [pd.Timestamp(dt(year = i.year, month = i.month, day = 1)) for i in brent_m['date']]

zcyc = pd.read_csv(path + f'//zcyc_1.csv', sep = ';').reset_index().set_axis(['date', 'time', f'rate_1'], axis = 1).iloc[1:, :]
temp_df = pd.read_csv(path + f'//zcyc_05.csv', sep = ';').reset_index().set_axis(['date', 'time', f'rate_05'], axis = 1).iloc[1:, [0,2]]
zcyc = zcyc.merge(temp_df, how = 'inner', on = 'date')
temp_df = pd.read_csv(path + f'//zcyc_025.csv', sep = ';').reset_index().set_axis(['date', 'time', f'rate_025'], axis = 1).iloc[1:, [0,2]]
zcyc = zcyc.merge(temp_df, how = 'inner', on = 'date').drop(columns=['time'])
zcyc['date'] = [pd.Timestamp(i) for i in zcyc['date']]
zcyc.iloc[:, 1:] = zcyc.iloc[:, 1:].replace(',', '.', regex=True).astype(float)
zcyc_m = zcyc.groupby(zcyc["date"].dt.to_period("M")).mean().reset_index(drop = True)
zcyc_m['date'] = [pd.Timestamp(dt(year = i.year, month = i.month, day = 1)) for i in zcyc_m['date']]

monthly_data = cbrate_and_inflation.merge(dollar_m, how = 'inner', on = 'date')\
    .merge(m_agg, how = 'inner', on = 'date')\
        .merge(inf_exp, how = 'inner', on = 'date')\
            .merge(credits_hh, how = 'inner', on = 'date')\
                .merge(pmi, how = 'inner', on = 'date')\
                .merge(brent_m, how = 'inner', on = 'date')\
                .merge(roisfix_m, how = 'inner', on = 'date')\
                .merge(zcyc_m, how = 'inner', on = 'date').sort_values('date')

daily_data = zcyc.merge(ruonia, how = 'inner', on = 'date')\
    .merge(roisfix, how = 'inner', on = 'date')\
    .merge(brent, how = 'inner', on = 'date').sort_values('date')

monthly_data = monthly_data.set_index('date').apply(lambda x: x.astype(float)).copy()
daily_data.iloc[:, 1:] = daily_data.iloc[:, 1:].apply(lambda x: x.astype(float)).copy()