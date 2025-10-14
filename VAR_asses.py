import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from statsmodels.tsa.stattools import adfuller, kpss
import statsmodels.api as sm

from scipy.stats import chi2
import inspect

import warnings
from statsmodels.tools.sm_exceptions import InterpolationWarning

warnings.simplefilter("ignore", InterpolationWarning)

from typing import Optional, Tuple, Union

class VAR_asses:
    def __init__(self, 
                    timeseries: Union[np.ndarray, pd.DataFrame],
                    list_with_names: Optional[list] = [], 
                    i_criteria: Optional[str] = 'aic',
                    p_max: Optional[int] = 10) -> None:


        if isinstance(timeseries, pd.DataFrame):
            print("Это pandas DataFrame!")
            self.df = timeseries.copy()
            timeseries = timeseries.sort_index(ascending=False).to_numpy().T
            self.var_names = [f'var_{i}' for i in range(1, self.K + 1)] if self.df.columns.to_list() == [] else self.df.columns.to_list()

        elif isinstance(timeseries, np.ndarray):
            print("Это NumPy массив!")
            self.var_names = [f'var_{i}' for i in range(1, self.K + 1)] if list_with_names == [] else list_with_names
        else:
            raise ValueError("timeseries должен быть либо DataFrame, либо ndarray")

        self.X: np.ndarray = timeseries
        self.p_max: int = p_max # type: ignore
        self.i_criteria: Optional[str] = i_criteria
        self.K, self.T = timeseries.shape 