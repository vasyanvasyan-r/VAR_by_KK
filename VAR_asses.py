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
                    endo_data: Union[np.ndarray, pd.DataFrame],
                    list_with_names: Optional[list] = [], 
                    i_criteria: Optional[str] = 'aic',
                    exog_data: Union[np.ndarray, pd.DataFrame] = pd.DataFrame([None]),
                    p_max: Optional[int] = 10) -> None:

        self.K_endo, self.T = endo_data.shape
        if isinstance(endo_data, pd.DataFrame):
            print("Endo pandas DataFrame!")
            self.df = endo_data.copy()
            endo_data = endo_data.sort_index(ascending=False).to_numpy().T
            self.var_names = [f'var_{i}' for i in range(1, self.K_endo + 1)] if self.df.columns.to_list() == [] else self.df.columns.to_list()


        elif isinstance(endo_data, np.ndarray):
            print("Это NumPy массив!")
            self.var_names = [f'var_{i}' for i in range(1, self.K_endo + 1)] if list_with_names == [] else list_with_names
        else:
            raise ValueError("Endo должен быть либо DataFrame, либо ndarray")
        
        self.K_exog = exog_data.shape[0]
        if isinstance(exog_data, pd.DataFrame):
            print("Это pandas DataFrame!")
            self.df = exog_data.copy()
            exog_data = exog_data.sort_index(ascending=False).to_numpy().T
            self.var_names = [f'var_{i}' for i in range(1, self.K_exog + 1)] if self.df.columns.to_list() == [] else self.df.columns.to_list()

        elif isinstance(exog_data, np.ndarray):
            print("Это NumPy массив!")
            self.var_names = [f'var_{i}' for i in range(1, self.K_exog + 1)] if list_with_names == [] else list_with_names
        else:
            raise ValueError("Endo должен быть либо DataFrame, либо ndarray")

        self.endo: np.ndarray = endo_data
        self.exog: np.ndarray = exog_data
        self.p_max: int = p_max # type: ignore
        self.i_criteria: Optional[str] = i_criteria

        del self.df

    def OLS_estimation(
                self,
                Nseries, #numpy array
                lag: int = 1,
                from_class : bool = True,
                lag_exog: int = 1,

                exog_data: Optional[np.ndarray] = None) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, int, int]:
        if from_class:
            X = self.exog_data
        X = Nseries.values
        p = lag
        K, T = X.shape
        # Основные лаги 
        p_ex = lag_exog
        if exog_data is not None:
            X_ex = exog_data.values
        
        # Основные лаги 
        Z = np.hstack(
            [np.concatenate([np.array([1]), X[:, i:i+p].T.flatten()]).reshape(-1, 1) # type: ignore
                for i in range(T - p)]
        )[:, 1:]
        if exog_data is not None:
            Z_ex = np.hstack(
            [X_ex[:, i:i+p_ex].T.flatten().reshape(-1, 1) # type: ignore
                for i in range(T - p_ex)])[:, 1:]
        
        if exog_data is not None:
            if p > p_ex:
                Z = np.vstack([Z, Z_ex[:, :p_ex-p]])
            elif p == p_ex:
                Z = np.vstack([Z, Z_ex])
            else:
                Z = np.vstack([Z[:, :p-p_ex], Z_ex])
        Y = X[:, :Z.shape[1]]

        B_hat = Y @ Z.T @ np.linalg.inv(Z @ Z.T)
        E = Y - B_hat @ Z
        B_hat_endo = B_hat[:, :K*p+1]
        P = np.linalg.cholesky(E@E.T)
        return Z, Y, B_hat, E, X.shape[0], T, B_hat_endo, P # type: ignore
    
    def irf_companion(
        A_mats : np.ndarray,
        B : np.ndarray, 
        horizon : int
                  ):
        """
        A_mats : list of A_i, i=1..p, каждая (n x n)
        B      : impact matrix (n x n)
        horizon: максимальный лаг
        """
        K = A_mats.shape[0]
        lag = int((A_mats.shape[1])/K)

        # Companion matrix
        
        bottom = np.eye(K*(lag-1), K*lag)
        A_comp = np.vstack([A_mats, bottom])

        # Selector
        J = np.hstack([np.eye(K), np.zeros((K, K*(lag-1)))])

        irfs = []
        for h in range(0, horizon):
            Ah = np.linalg.matrix_power(A_comp, h)
            irfs.append(J @ Ah @ J.T @ B)
        return np.array(irfs)
    def random_orthogonal(K):
        Q, _ = np.linalg.qr(np.random.normal(size=(K,K)))
        return Q
    