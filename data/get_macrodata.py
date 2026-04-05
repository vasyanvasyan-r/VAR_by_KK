import pandas as pd
import numpy as np
import re, os
from datetime import datetime as dt
from datetime import timedelta as td


import warnings
warnings.filterwarnings("ignore", message="Workbook contains no default style.*")

cbrate_and_inflation = pd.read_excel('data/Инфляция и ключевая ставка Банка России.xlsx', engine='openpyxl').set_axis(['date', 'key_rate', 'infl', 'target'], axis = 1)
cbrate_and_inflation['date'] = [i.split('.')[0] + '.' + i.split('.')[1] + '0' if  i.split('.')[1] == '202' else i for i in cbrate_and_inflation['date'].astype(str)]
cbrate_and_inflation['date'] = [dt.strptime(i, '%m.%Y') for i in cbrate_and_inflation['date'].astype(str)]
cbrate_and_inflation['date'] = cbrate_and_inflation['date'].dt.strftime('%Y-%m') # type: ignore

exchange_rate_data = pd.read_excel('data/exchange_rate.xlsx', engine='openpyxl').rename(columns={'Unnamed: 0':'name'}).set_index('name').rename_axis(None, axis=0)

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
df = pd.read_excel('data/usdrub_daily.xlsx', engine='openpyxl')
df['date'] = [dt.strftime(i, "%Y-%m") for i in df['data']]
usdrub_m = df.loc[:, ['date', 'curs']].groupby(['date']).agg({'curs' : 'mean'}).copy(deep=True).reset_index().rename(columns = {'curs': 'dollar_m'})
usdrub_d = df.loc[:, ['date', 'curs']].copy(deep=True)


monetary_agg = pd.read_excel('data/monetary_agg.xlsx', engine='openpyxl').rename(columns={'Денежные агрегаты*, млрд руб.':'name'})\
    .set_index('name').rename_axis(None, axis=0)
m_agg = monetary_agg.loc[[
    'Денежный агрегат М0', 'Денежный агрегат М1', 'Денежный агрегат М2'
]].set_axis(['m0', 'm1', 'm2']).T.reset_index().rename(columns = {'index':'date'})

m_agg['date'] = [dt.strftime(dt.strptime(str(i).split(" ")[0], "%Y-%m-%d"), "%Y-%m") for i in m_agg['date']]


monetary_agg = pd.read_excel('data//monetary_agg_SA.xlsx', engine='openpyxl').iloc[2:-5, :].rename(columns={'Денежные агрегаты':'name'}).set_index('name').rename_axis(None, axis=0)
m_agg_sa = monetary_agg.loc[:, [
    'Unnamed: 27', 'Unnamed: 24', 'Unnamed: 21'
]].set_axis(['m2x_sa_mom', 'm2_sa_mom', 'm1_sa_mom'], axis = 1).reset_index().rename(columns= {'index':'date'})

m_agg_sa['date'] = [dt.strftime(dt.strptime(str(i).split(" ")[0], "%Y-%m-%d"), "%Y-%m") for i in m_agg_sa['date']]



pmi = pd.read_excel('data/Бюллетень О чем говорят тренды.xlsx', sheet_name=9, engine='openpyxl').iloc[3:,:3]\
    .set_axis(['date', 'PMI_manufacturing', 'PMI_service'], axis = 1)\
            .reset_index(drop=True)
pmi['date'] = [pd.Timestamp(i) for i in pmi['date']]
pmi['date'] = [dt.strftime(dt.strptime(str(i).split(" ")[0], "%Y-%m-%d"), "%Y-%m") for i in pmi['date']]

ipi = pd.read_excel('data/ИПП.xlsx').iloc[:2, 1:].T.reset_index(drop = True).set_axis(['date', 'ipi'], axis=1)
ipi['date'] = [i.strftime("%Y-%m") for i in ipi['date']]

ruonia = pd.read_excel('data/ruonia.xlsx', engine='openpyxl').rename(columns = {'DT':'date', 'ruo':'ruonia'}).loc[:, ['date', 'ruonia']]
ruonia['date'] = [pd.Timestamp(i) for i in ruonia['date']]
ruonia_m = ruonia.copy(deep = True)
ruonia_m['date'] = [dt.strftime(dt.strptime(str(i).split(" ")[0], "%Y-%m-%d"), "%Y-%m") for i in ruonia_m['date']]
ruonia_m = ruonia_m.groupby('date').mean().reset_index(drop=False)


inf_exp_all_data = pd.read_excel('data/Наблюдаемая_и_ожидаемая_инфляция.xlsx', engine='openpyxl', sheet_name = 'Данные за все годы')\
                    .rename(columns={'Данные в таблице приводятся в % от всех опрошенных, если не указано иное.':'name'}).set_index('name').rename_axis(None, axis=0)

inf_exp_all_data = inf_exp_all_data.rename(index = {inf_exp_all_data.index.to_list()[0]:'date'})
inf_exp = inf_exp_all_data.loc[[
    'date', 
    'ожидаемая инфляция среди тех, кто имеет сбережения (в %)', 
    'ожидаемая инфляция среди тех, кто не имеет сбережений (в %)',
    'ожидаемая инфляция (в %)',
    'наблюдаемая инфляция среди тех, кто имеет сбережения (в %)',
    'наблюдаемая инфляция среди тех, кто не имеет сбережений (в %)',
    'есть',
    'нет'
]]
inf_exp = inf_exp.iloc[[0,4, 5, 6, 7, 8, 9]].T.reset_index(drop = True).set_axis(['date', 'pi_e_ws', 'pi_e_wos', 'pi_e', 'pi_hat_ws', 'pi_hat_wos', 's1'], axis = 1)
inf_exp['s0'] = inf_exp_all_data.loc['нет'].iloc[0].astype(float).reset_index(drop=True)
inf_exp[['pi_e', 's1']] = inf_exp[['pi_e', 's1']].astype(float)
inf_exp['date'] = [pd.Timestamp(i) for i in inf_exp['date']]
inf_exp['date'] = [dt.strftime(dt.strptime(str(i).split(" ")[0], "%Y-%m-%d"), "%Y-%m") for i in inf_exp['date']]

roisfix = pd.read_excel('data/futures_ruonia.xlsx', engine='openpyxl').set_axis(['date', 'smth', 'ruonia_1m', 'ruonia_3m', 'ruonia_6m'], axis = 1).drop(['smth', 'ruonia_1m'], axis = 1)
roisfix['date'] = [pd.Timestamp(dt.strptime(str(i).split(" ")[0], "%Y-%m-%d")) for i in roisfix['date']]
roisfix_m = roisfix.copy(deep = True)
roisfix_m['date'] = [dt.strftime(i, "%Y-%m") for i in roisfix_m['date']]
roisfix_m = roisfix_m.groupby('date').mean().reset_index(drop=False)


brent = pd.read_csv('data/brent.csv').iloc[:, :2].set_axis(['date', 'price_brent'], axis = 1).replace({',': '.'}, regex=True)
brent['price_brent'] = brent['price_brent'].astype(float)
brent['price_brent'] = brent['price_brent'].astype(float)
brent['date'] = [dt.strptime(i, '%d.%m.%Y') for i in brent['date']]
brent_m = brent.copy(deep = True)
brent_m['date'] = [dt.strftime(i, "%Y-%m") for i in brent_m['date']]
brent_m = brent_m.groupby('date').mean().reset_index(drop=False)

cd = pd.read_excel('data/balance_odc.xlsx').set_index('Баланс кредитных организаций, млн руб.*')\
    .rename_axis(None, axis = 0).loc[['Кредиты и займы, предоставленные  населению (домашним хозяйствам)', 'Депозиты населения  (домашних хозяйств)']].T\
    .reset_index().set_axis(['date', 'credits_hh', 'deposits_hh'], axis = 1)
cd['date'] = [dt.strptime(str(i), '%Y-%m-%d %H:%M:%S').strftime('%Y-%m') for i in cd['date']]

zcyc = pd.read_csv('data//zcyc_1.csv', sep = ';').reset_index().set_axis(['date', 'time', f'rate_1'], axis = 1).iloc[1:, :]
temp_df = pd.read_csv('data//zcyc_05.csv', sep = ';').reset_index().set_axis(['date', 'time', f'rate_05'], axis = 1).iloc[1:, [0,2]]
zcyc = zcyc.merge(temp_df, how = 'inner', on = 'date')
temp_df = pd.read_csv('data/zcyc_025.csv', sep = ';').reset_index().set_axis(['date', 'time', f'rate_025'], axis = 1).iloc[1:, [0,2]]
zcyc = zcyc.merge(temp_df, how = 'inner', on = 'date').drop(columns=['time'])
zcyc['date'] = [pd.Timestamp(dt.strptime(str(i).split(" ")[0], "%d.%m.%Y")) for i in zcyc['date']]
zcyc.iloc[:, 1:] = zcyc.iloc[:, 1:].replace({',': '.'}, regex=True)
for col in zcyc.columns[1:]:
    zcyc[col] = pd.to_numeric(zcyc[col], errors='coerce')

zcyc_m = zcyc.copy(deep=True)

zcyc_m['date'] = zcyc_m['date'].dt.strftime('%Y-%m') # type: ignore
zcyc_m = zcyc_m.groupby('date').mean().reset_index(drop=False)

inf_us = pd.read_csv('data/us_infl.csv').set_axis(['date', 'inf_us_cum'], axis = 1)
inf_us['date'] = [dt.strptime(i, '%Y-%m-%d').strftime("%Y-%m") for i in inf_us['date']]
inf_us.iloc[945,1] = inf_us.iloc[944,1]

igrea = pd.read_excel('data/igrea.xlsx', engine='openpyxl').set_axis(['date', 'igrea'], axis = 1)
igrea['date'] = igrea['date'].dt.strftime('%Y-%m') # type: ignore

ipc = pd.read_excel('data/cpi.xlsx', engine='openpyxl')
ipc = ipc.T.iloc[1:, [0, 52, 53]].reset_index(drop=False).set_axis(['date', 'all_items', 'ru_cpi', 'ru_cpi_wo_servises'], axis = 1)
ipc['date'] = ipc['date'].dt.strftime("%Y-%m") # type: ignore

govspend = pd.read_excel('data/govspending.xlsx', sheet_name='Сезонно скорректированные2', engine='openpyxl')
govspend['date'] = govspend['date'].dt.strftime("%Y-%m") # type: ignore
govspend = govspend.rename(columns = {'Доля прироста исполененого к плану':'govspend'}).iloc[:, :2]

cons = pd.read_excel('data/pokupki_doverie.xlsx').iloc[:4, 30:].reset_index(drop = True).T.reset_index(drop = True).set_axis(['date', 'pos', 'neg', 'dna'], axis = 1)

# Словарь русских месяцев
RU_MONTHS = {
    'янв.': '01', 'фев.': '02', 'мар.': '03', 'апр.': '04',
    'май': '05', 'июн.': '06', 'июл.': '07', 'авг.': '08',
    'сен.': '09', 'окт.': '10', 'ноя.': '11', 'дек.': '12'
}

def parse_mixed_date(date_val):
    """
    Парсит дату в смешанном формате.
    Возвращает pd.Timestamp или NaT при ошибке.
    """
    if pd.isna(date_val):
        return pd.NaT
    
    date_str = str(date_val).strip()
    
    # Если уже стандартный формат — пробуем распарсить напрямую
    if re.match(r'\d{4}-\d{2}-\d{2}', date_str):
        try:
            return pd.to_datetime(date_str)
        except:
            pass
    
    # Если формат "окт.25" (рус. месяц + 2-значный год)
    match = re.match(r'([а-яё\.]+)\.?(\d{2})', date_str, re.IGNORECASE)
    if match:
        month_ru, year_short = match.groups()
        month_ru = month_ru.lower() + '.' if not month_ru.endswith('.') else month_ru.lower()
        
        # Ищем месяц в словаре (с точкой или без)
        month_num = RU_MONTHS.get(month_ru) or RU_MONTHS.get(month_ru.rstrip('.'))
        
        if month_num:
            # Предполагаем 2000-е годы для 2-значного года
            year = 2000 + int(year_short)
            return pd.Timestamp(year=year, month=int(month_num), day=1)
    
    # Если ничего не подошло
    return pd.NaT

# Применяем функцию к вашей колонке
cons['date'] = cons['date'].apply(parse_mixed_date).dt.strftime('%Y-%m') # type: ignore
cons['cons'] = cons['pos'] + 0.5*cons['dna']
cons = cons.loc[:, ['date', 'cons']]

wage = pd.read_csv('data/izmenenie-obema-fot.csv', sep = ';').query("category == 'Все отрасли'")
wage['date'] = [dt.strptime(i, '%Y-%m-%d').strftime("%Y-%m") for i in wage['date']]
wage['wage'] = np.log(wage['value'])
wage = wage.loc[:, ['date', 'wage']]

monthly_data = cbrate_and_inflation\
    .merge(usdrub_m, how = 'outer', on = 'date')\
    .merge(m_agg, how = 'outer', on = 'date')\
    .merge(inf_exp, how = 'outer', on = 'date')\
    .merge(pmi, how = 'outer', on = 'date')\
    .merge(brent_m, how = 'outer', on = 'date')\
    .merge(roisfix_m, how = 'outer', on = 'date')\
    .merge(zcyc_m, how = 'outer', on = 'date')\
    .merge(inf_us, how = 'outer', on = 'date')\
    .merge(igrea, how = "outer", on = 'date')\
    .merge(ipc, how = "outer", on = 'date')\
    .merge(ruonia_m, how = "outer", on = 'date')\
    .merge(m_agg_sa, how = "outer", on = 'date')\
    .merge(govspend, how = "outer", on = 'date')\
    .merge(ipi, how='outer', on='date')\
    .merge(wage, how = 'outer', on = 'date')\
    .merge(cons, how = 'outer', on = 'date')\
    .merge(cd, how = 'outer', on = 'date')\
    .sort_values('date')

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

monthly_data['real_rate'] = ((monthly_data['key_rate']/100+1)/(monthly_data['infl']/100+1)*100-100)
monthly_data['real_ruonia'] = ((monthly_data['ruonia']/100+1)/(monthly_data['infl']/100+1)*100-100)


monthly_data['log_credits_hh'] = np.log(monthly_data['credits_hh']/monthly_data['rc_c'])
monthly_data['log_deposits_hh'] = np.log(monthly_data['deposits_hh']/monthly_data['rc_c'])


monthly_data.index = [dt.strptime(i, '%Y-%m') for i in monthly_data.index.to_list()] # type: ignore

monthly_data.to_pickle('data/monthly_data.pkl')