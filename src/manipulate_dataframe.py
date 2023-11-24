import pandas as pd
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import os, glob
import scipy
import dask.dataframe as dd
from statsmodels.formula.api import ols
import re


def normalize(df, l = ['NAIV_1 [bool]', 'NAIV_2 [bool]','PRV_1 [bool]', 'PRV_2 [bool]']):
    if len(l)!=0 :
        df=  df.drop(columns = l)
    newname = []
    for col in df.columns :
        newname.append(re.sub(r' \[.*?\]', '', col))
    X = df.values
    X_norm = (X - np.mean(X,axis = 0))/np.std(X, axis = 0)
    df_norm = pd.DataFrame(data = X_norm, columns=newname, index= df.index)

    return df_norm


def regression(df, formula) :
    df2 = df.copy()
    import re 
    for col in df.columns :
        newname = re.sub(r' \[.*?\]', '', col)
        df2.rename(columns={col:newname}, inplace=True)
    model = ols(formula, data = df2).fit()
    r2 = model.rsquared
    pvals = model.pvalues
    IC = model.conf_int(0.05)
    n_obs = model.nobs
    params_list = model.params
    reg_dict = {'R2' :r2, 'pvaleur' : pvals.values, 'N_observations':n_obs, 'Paramètres' : params_list.values, 'Intervals': IC.values, 'ParamName': list(params_list.index) }
    return reg_dict

def generate_df_reg (all_reg):
    records = all_reg.index.values
    Params = all_reg[0]['ParamName']
    R2 = np.empty(len(records))
    N_obs= np.empty(len(records))
    pvals = np.empty((len(records), len(Params)))
    params_val = np.empty((len(records), len(Params)))
    IC_0 =  np.empty((len(records), len(Params)))
    IC_1 =  np.empty((len(records), len(Params)))

    for i, record in enumerate(records) :
        record_dict = all_reg[record]
        R2[i] = record_dict['R2']
        N_obs[i] = record_dict['N_observations']
        pvals[i, :] = record_dict['pvaleur']
        params_val[i, :] = record_dict['Paramètres']
        IC_0[i,:] = record_dict['Intervals'][:,0]
        IC_1[i,:] = record_dict['Intervals'][:,1]

    df_reg = pd.DataFrame({'record': records, 'R2': R2, 'N_obs': N_obs}).set_index('record')
    for i, param in enumerate(Params) :
        df_reg['coeff_'+param] = params_val[:,i]
        df_reg['pval_'+param] = pvals[:,i]
        df_reg['IC0_'+param] = IC_0[:,i]
        df_reg['IC1_'+param] = IC_1[:,i]

    return df_reg

def eliminate_records(df):
    #renvoie True si records est a éliminer
    alt_min=df['ALT [ft]'].min()
    alt_max=df['ALT [ft]'].max()
    alt_range=alt_max-alt_min
    bol=False
    
    if alt_range<15000:
        bol=True
    return bol

