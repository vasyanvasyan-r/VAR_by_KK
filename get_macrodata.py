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


cbrate_and_inflation = pd.read_excel(path + '//Инфляция и ключевая ставка Банка России.xlsx', engine='openpyxl').set_axis(['date', 'key_rate', 'infl', 'target'], axis = 1)
cbrate_and_inflation['date'] = [i.split('.')[0] + '.' + i.split('.')[1] + '0' if  i.split('.')[1] == '202' else i for i in cbrate_and_inflation['date'].astype(str)]
cbrate_and_inflation['date'] = [dt.strptime(i, '%m.%Y') for i in cbrate_and_inflation['date'].astype(str)]
cbrate_and_inflation['date'] = cbrate_and_inflation['date'].dt.strftime('%Y-%m')

exchange_rate_data = pd.read_excel(path + '//exchange_rate.xlsx', engine='openpyxl').rename(columns={'Unnamed: 0':'name'}).set_index('name').rename_axis(None, axis=0)

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
dollar_m['date'] = [dt.strptime('-'.join([str(y), ru_months_r[m]]), "%Y-%m") for y, m in zip(dollar_m['year'], dollar_m['month'])]
dollar_m['date'] = dollar_m['date'].dt.strftime('%Y-%m')
dollar_m = dollar_m.drop(['month', 'year'], axis = 1).reset_index(drop = True)


monetary_agg = pd.read_excel(path + '//monetary_agg.xlsx', engine='openpyxl').rename(columns={'Денежные агрегаты*, млрд руб.':'name'})\
    .set_index('name').rename_axis(None, axis=0)
m_agg = monetary_agg.loc[[
    'Денежный агрегат М0', 'Денежный агрегат М1', 'Денежный агрегат М2'
]].set_axis(['m0', 'm1', 'm2']).T.reset_index().rename(columns = {'index':'date'})

m_agg['date'] = [dt.strftime(dt.strptime(str(i).split(" ")[0], "%Y-%m-%d"), "%Y-%m") for i in m_agg['date']]


monetary_agg = pd.read_excel(path + f'//monetary_agg_SA.xlsx', engine='openpyxl').iloc[2:-5, :].rename(columns={'Денежные агрегаты':'name'}).set_index('name').rename_axis(None, axis=0)
m_agg_sa = monetary_agg.loc[:, [
    'Unnamed: 27', 'Unnamed: 24', 'Unnamed: 21'
]].set_axis(['m2x_sa_mom', 'm2_sa_mom', 'm1_sa_mom'], axis = 1).reset_index().rename(columns= {'index':'date'})

m_agg_sa['date'] = [dt.strftime(dt.strptime(str(i).split(" ")[0], "%Y-%m-%d"), "%Y-%m") for i in m_agg_sa['date']]


credits = pd.read_excel(path + '//Баланс кредитных организаций.xlsx', engine='openpyxl').rename(columns={'Баланс кредитных организаций, млн руб.*':'name'})\
    .set_index('name').rename_axis(None, axis=0)
credits_hh = credits.loc[[
    'Кредиты и займы, предоставленные  населению (домашним хозяйствам)'
]].set_axis(['credits_hh']).T.reset_index().rename(columns = {'index':'date'})
credits_hh['date'] = [dt.strftime(dt.strptime(str(i).split(" ")[0], "%Y-%m-%d"), "%Y-%m") for i in credits_hh['date']]


pmi = pd.read_excel(path + '//Бюллетень О чем говорят тренды.xlsx', sheet_name=9, engine='openpyxl').iloc[3:,:3]\
    .set_axis(['date', 'PMI_manufacturing', 'PMI_service'], axis = 1)\
            .reset_index(drop=True)
pmi['date'] = [pd.Timestamp(i) for i in pmi['date']]
pmi['date'] = [dt.strftime(dt.strptime(str(i).split(" ")[0], "%Y-%m-%d"), "%Y-%m") for i in pmi['date']]

ruonia = pd.read_excel(path + '//Динамика ставки RUONIA.xlsx', engine='openpyxl').set_axis(['date', 'ruonia'], axis = 1)
ruonia['date'] = [pd.Timestamp(i) for i in ruonia['date']]
ruonia_m = ruonia.copy(deep = True)
ruonia_m['date'] = [dt.strftime(dt.strptime(str(i).split(" ")[0], "%Y-%m-%d"), "%Y-%m") for i in ruonia_m['date']]
ruonia_m = ruonia_m.groupby('date').mean().reset_index(drop=False)


inf_exp_all_data = pd.read_excel(path + '//Наблюдаемая_и_ожидаемая_инфляция.xlsx', engine='openpyxl', sheet_name = 'Данные за все годы')\
                    .rename(columns={'Данные в таблице приводятся в % от всех опрошенных, если не указано иное.':'name'}).set_index('name').rename_axis(None, axis=0)

inf_exp_all_data = inf_exp_all_data.rename(index = {inf_exp_all_data.index.to_list()[0]:'date'})
inf_exp = inf_exp_all_data.loc[[
    'date', 
    'ожидаемая инфляция среди тех, кто имеет сбережения (в %)', 
    'ожидаемая инфляция среди тех, кто не имеет сбережений (в %)',
    'ожидаемая инфляция (в %)'
]]
inf_exp = inf_exp.iloc[[0,4, 5, 6]].T.reset_index(drop = True).set_axis(['date', 'pi_e_ws', 'pi_e_wos', 'pi_e'], axis = 1)
inf_exp['pi_e'] = inf_exp['pi_e'].astype(float)
inf_exp['date'] = [pd.Timestamp(i) for i in inf_exp['date']]
inf_exp['date'] = [dt.strftime(dt.strptime(str(i).split(" ")[0], "%Y-%m-%d"), "%Y-%m") for i in inf_exp['date']]

roisfix = pd.read_excel(path + '//Ставка ROISfix (RUONIA Overnight Interest Rate Swap).xlsx', engine='openpyxl').iloc[1:, :]\
    .set_axis(['date', 'ruonia_1w', 'ruonia_2w', 'ruonia_1m', 'ruonia_2m', 'ruonia_3m', 'ruonia_6m', 'ruonia_1y', 'ruonia_2y'], axis = 1).fillna(0.0)
roisfix['date'] = [pd.Timestamp(dt.strptime(str(i).split(" ")[0], "%d-%m-%Y")) for i in roisfix['date']]
roisfix.iloc[:, 1:] = roisfix.iloc[:, 1:].replace('--', '0', regex=True).replace(',', '.', regex=True).astype(float)
roisfix_m = roisfix.copy(deep = True)
roisfix_m['date'] = [dt.strftime(i, "%Y-%m") for i in roisfix_m['date']]
roisfix_m = roisfix_m.groupby('date').mean().reset_index(drop=False)


brent = pd.read_excel(path + f'//Фьючерс на нефть Brent.xlsx').iloc[:, :2].set_axis(['date', 'price_brent'], axis = 1)
brent['date'] = [pd.Timestamp(i) for i in brent['date']]
brent_m = brent.copy(deep = True)
brent_m['date'] = [dt.strftime(dt.strptime(str(i).split(" ")[0], "%Y-%m-%d"), "%Y-%m") for i in brent_m['date']]
brent_m = brent_m.groupby('date').mean().reset_index(drop=False)


zcyc = pd.read_csv(path + f'//zcyc_1.csv', sep = ';').reset_index().set_axis(['date', 'time', f'rate_1'], axis = 1).iloc[1:, :]
temp_df = pd.read_csv(path + f'//zcyc_05.csv', sep = ';').reset_index().set_axis(['date', 'time', f'rate_05'], axis = 1).iloc[1:, [0,2]]
zcyc = zcyc.merge(temp_df, how = 'inner', on = 'date')
temp_df = pd.read_csv(path + f'//zcyc_025.csv', sep = ';').reset_index().set_axis(['date', 'time', f'rate_025'], axis = 1).iloc[1:, [0,2]]
zcyc = zcyc.merge(temp_df, how = 'inner', on = 'date').drop(columns=['time'])
zcyc['date'] = [pd.Timestamp(dt.strptime(str(i).split(" ")[0], "%d.%m.%Y")) for i in zcyc['date']]
zcyc.iloc[:, 1:] = zcyc.iloc[:, 1:].replace(',', '.', regex=True).astype(float)

zcyc_m = zcyc.copy(deep=True)

zcyc_m['date'] = zcyc_m['date'].dt.strftime('%Y-%m')
zcyc_m = zcyc_m.groupby('date').mean().reset_index(drop=False)

inf_us = pd.read_excel(path + '//us_infl.xlsx', sheet_name='Monthly', engine='openpyxl')
inf_us = inf_us.rename(columns= {'observation_date':'date', 'MEDCPIM158SFRBCLE':'inf_us'}).copy(deep = True)
inf_us['date'] = inf_us['date'].dt.strftime("%Y-%m")
inf_us['inf_us'] = inf_us['inf_us']/1200+1
inf_us['inf_us_cum'] = [np.prod(inf_us['inf_us'].iloc[:i+1].to_numpy()) for i in range(inf_us.shape[0])]

igrea = pd.read_excel(path + f'\\igrea.xlsx', engine='openpyxl').set_axis(['date', 'igrea'], axis = 1)
igrea['date'] = igrea['date'].dt.strftime('%Y-%m')

ipc = pd.read_excel(path + f'\\indicators_cpd.xlsx', engine='openpyxl')
ipc = ipc.T.iloc[1:, [0, 52, 53]].reset_index(drop=False).set_axis(['date', 'all_items', 'ru_cpi', 'ru_cpi_wo_servises'], axis = 1)
ipc['date'] = ipc['date'].dt.strftime("%Y-%m")

monthly_data = cbrate_and_inflation.merge(dollar_m, how = 'outer', on = 'date')\
    .merge(m_agg, how = 'outer', on = 'date')\
        .merge(inf_exp, how = 'outer', on = 'date')\
            .merge(credits_hh, how = 'outer', on = 'date')\
                .merge(pmi, how = 'outer', on = 'date')\
                    .merge(brent_m, how = 'outer', on = 'date')\
                        .merge(roisfix_m, how = 'outer', on = 'date')\
                            .merge(zcyc_m, how = 'outer', on = 'date')\
                                .merge(inf_us, how = 'outer', on = 'date')\
                                    .merge(igrea, how = "outer", on = 'date')\
                                        .merge(ipc, how = "outer", on = 'date')\
                                            .merge(ruonia_m, how = "outer", on = 'date')\
                                                .merge(m_agg_sa, how = "outer", on = 'date').sort_values('date')

daily_data = zcyc.merge(ruonia, how = 'outer', on = 'date')\
    .merge(roisfix, how = 'outer', on = 'date')\
    .merge(brent, how = 'outer', on = 'date').sort_values('date')

monthly_data = monthly_data.set_index('date').apply(lambda x: x.astype(float)).copy()
daily_data.iloc[:, 1:] = daily_data.iloc[:, 1:].apply(lambda x: x.astype(float)).copy()



monthly_data['real_brent'] = (monthly_data['price_brent']/monthly_data['inf_us_cum'])

monthly_data['rcwos_c'] = monthly_data['ru_cpi_wo_servises'].copy(deep = True)
cpi_array = monthly_data['ru_cpi_wo_servises'].loc[monthly_data['ru_cpi_wo_servises'].notna()].to_numpy()/100+1
monthly_data.loc[monthly_data['rcwos_c'].notna(), 'rcwos_c'] = [np.prod(cpi_array[:i+1]) for i in range(cpi_array.shape[0])]

monthly_data['rc_c'] = monthly_data['ru_cpi'].copy(deep = True)
cpi_array = monthly_data['ru_cpi'].loc[monthly_data['ru_cpi'].notna()].to_numpy()/100+1
monthly_data.loc[monthly_data['rc_c'].notna(), 'rc_c'] = [np.prod(cpi_array[:i+1]) for i in range(cpi_array.shape[0])]

monthly_data['real_dollar'] = monthly_data['dollar_m']*monthly_data['inf_us_cum']/monthly_data['rcwos_c']

monthly_data['real_rate'] = ((monthly_data['key_rate']/110+1)/(monthly_data['infl']/100+1)*100-100)
monthly_data['real_ruonia'] = ((monthly_data['ruonia']/110+1)/(monthly_data['infl']/100+1)*100-100)


monthly_data['log_credits_hh'] = np.log(monthly_data['credits_hh']/monthly_data['rc_c'])


monthly_data.index = [dt.strptime(i, '%Y-%m') for i in monthly_data.index.to_list()] # type: ignore