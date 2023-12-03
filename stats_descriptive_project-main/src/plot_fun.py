# -*- coding: utf-8 -*-
"""
Module _init_ - projet de statistiques descriptives MACS3
@author: Kraemer Valentin 
"""
__date__ = "2023-11-27"
__version__ = '1.0'

import matplotlib.pyplot as plt


###
# Author : Kraemer Valentin 
# Introduction a ces fonctions : vkr_flight_functions.ipynb
# Date : 28 nov 2023
# Version 1.0
###


def afficher_significativite(df_reg) :
    """
    afficher_siginificativite function 
    @author : Kraemer Valentin 

    Input : df_reg : dataframe de regression multi-vols

    Output : None

    """
    records = df_reg.index.values
    fig, axs = plt.subplots(2, figsize = (10,8))
    axs[0].plot(records, df_reg['R2'].values)
    axs[1].plot(records, df_reg['N_obs'].values)
    axs[0].set_xlabel('records')
    axs[0].set_ylabel('R2')
    axs[0].set_ylim((0,1))
    axs[1].set_xlabel('records')
    axs[1].set_ylabel("Nombre d'observations")

    plt.show()

def afficher_coeff(df_reg,window = 1, tol = 1e-10, norm= True):
    """
    afficher_coeff function
    @author : Kraemer Valentin 

    Input : 
        df_reg : dataframe de regression multi-vols
        window : (default = 1) la fenetre glissante surlaquelle on applique une mediane glissante
        tol    : (default = 1e-10) la tolérance au delà de laquelle on n'affiche plus les coefficients car la p-valeur est trop élevée
        norm   : (bolean, default = True) : permet d'afficher_coeff avec un y_range compris entre -1 et 1 dans le cas de données normalisées
    """
    
    l= df_reg.columns
    ParamName = [s.split('coeff_')[1] for s in l if 'coeff_' in s]
    if norm != True : ParamName.remove('Intercept')
    idx = df_reg.index.values
    plt.figure(figsize=(10, 8))
    for i,param in enumerate(ParamName) :
        df_param =df_reg.where(df_reg['pval_'+param]<tol)
        y_roll = df_param['coeff_'+param].rolling(window=window).median().values
        y_up = df_param['IC1_'+param].rolling(window= window).median().values
        y_down = df_param['IC0_'+param].rolling(window= window).median().values
        plt.plot(idx, y_roll, label = param)
        plt.fill_between(idx,y_up, y_down, alpha = 0.2)
    plt.xlabel('record')
    plt.ylabel('coefficient de regression')
    if norm == True : plt.ylim((-1,1))
    plt.legend()    
    plt.show()
    if norm != True : 
        plt.figure(figsize=(10, 8))
        param = 'Intercept'
        df_param =df_reg.where(df_reg['pval_'+param]<tol)
        y_roll = df_param['coeff_'+param].rolling(window=window).median().values
        y_up = df_param['IC1_'+param].rolling(window= window).median().values
        y_down = df_param['IC0_'+param].rolling(window= window).median().values
        plt.plot(idx, y_roll, label = param)
        plt.fill_between(idx,y_up, y_down, alpha = 0.2)
        plt.xlabel('record')
        plt.ylabel('coefficient de regression')
        plt.legend()    
        plt.show()
