import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

from typing import Optional, Tuple, Union

class VAR:
        
    doc_en = """    

    A package for selecting an appropriate Vector Autoregression (VAR) model
    and estimating impulse response functions, developed by K and K.

    The implementation is based on methods from Lutkepohl and Kilian (2017)
    (Kilian, L., & Lütkepohl, H. (2017). *Structural Vector Autoregressive Analysis*.
    Cambridge University Press), as well as the earlier academic textbook:
    Lütkepohl, H. (2005). *New Introduction to Multiple Time Series Analysis*. 
    Springer.

    The main requirement for using the package is to pass time series data
    in a format the model can interpret. There are two supported options:

    1. A NumPy `ndarray` and a list of variable names.
    In this case, the ndarray should be KxT, hence the rows are the variables and the columns are lags 
    2. A `pandas.DataFrame` and a list of column names.  
    In this case, the DataFrame’s index must reflect the time structure,
    meaning that sorting it in ascending order should yield the proper
    chronological order from the first to the last observation.

    """
    doc_ru = """
    
    Пакет для подбора корректной модели векторной авторегрессии и оценки импульсных откликов, сделанный К и К
    За основу были взяты методы из Lutkepohl и Killian 2017 
    (Kilian, L., & Lütkepohl, H. (2017). Structural Vector Autoregressive Analysis. Cambridge University Press) 
    и более ранний академический учебник Lutkepohl H. 
    (Helmut Lütkepohl, 2005. "New Introduction to Multiple Time Series Analysis," Springer Books, Springer, number 978-3-540-27752-1, December.)

    Основным требованием для пакета, является передача ему временных рядов, так чтобы он понял. 
    Есть два варианта: 
    1. numpy ndarray и список имен переменных
    2. передать pandas DataFrame и список столбцов-переменных; обязательное условие, 
    что индексы в таблицы должны быть отражать временную структуру так,
    что сортировка по возрастанию по ним давала от первого наблюдения до последнего

    Если будет переданно, 
    """

    def __init__(self, 
                 timeseries: Union[np.ndarray, pd.DataFrame],
                 list_with_names: Optional[list] = [], 
                 i_criteria: Optional[str] = 'aic',
                 p_max: Optional[int] = 10) -> None:
        

        if isinstance(timeseries, pd.DataFrame):
            print("Это pandas DataFrame!")
            timeseries = timeseries.sort_index(ascending=False).to_numpy().T

        elif isinstance(timeseries, np.ndarray):
            print("Это NumPy массив!")
        else:
            raise ValueError("timeseries должен быть либо DataFrame, либо ndarray")
        
        self.X: np.ndarray = timeseries
        self.p_max: int = p_max
        self.i_criteria: Optional[str] = i_criteria
        self.K, self.T = timeseries.shape     
        self.var_names = [f'var_{i}' for i in range(1, self.K + 1)] if list_with_names == [] else list_with_names



    def OLS_estimation(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Performs OLS estimation for the VAR(p) model.

        Returns
        -------
        Z : np.ndarray
            Regressor matrix with constant and lags.
        Y : np.ndarray
            Matrix of dependent variables.
        B_hat : np.ndarray
            Estimated coefficient matrix.
        """
        X = self.X
        p = self.p_max
        T = self.T

        Z = np.concatenate(
            [np.concatenate([np.array([1]), X[:, i:i+p].T.flatten()]).reshape(-1, 1)
             for i in range(T - p)],
            axis=1
        )[:, 1:]

        Y = X[:, :Z.shape[1]]

        B_hat = Y @ Z.T @ np.linalg.inv(Z @ Z.T)

        return Z, Y, B_hat

