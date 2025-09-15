import pandas as pd
import numpy as np


from VAR_by_KK import VAR
from cleaning_data import monthly_data, daily_data

var = VAR(monthly_data.iloc[:, 1:])
res = var.remove_trends('dollar_m')
print(res)