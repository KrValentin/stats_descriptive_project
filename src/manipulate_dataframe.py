# -*- coding: utf-8 -*-
"""
Module _init_ - projet de statistiques descriptives MACS3
@author: Kraemer Valentin 
"""
__date__ = "2023-11-27"
__version__ = '1.0'


import pandas as pd
import numpy as np
from statsmodels.formula.api import ols
from statsmodels.stats.stattools import durbin_watson
import re
from src import extraire_noms_variables


###
# Author : Kraemer Valentin 
# Introduction a ces fonctions : vkr_data_frame_analysis.ipynb
# Date : 27 nov 2023
# Version 1.0
###

def add_speed(df) :
    """
    @author : Kraemer Valentin 
    add_speed function 

    desc : ajout de la vitesse horizontale et verticale en [ft/s] au dataframe de vol

    Input : df, dataframe concernant un vol, possédant au moins les colonnes :
        -'M [Mach]'
        -'ALT [ft]'

    Ouput : df, dataframe avec les colonnes supplémentaires : 
        - 'dy [ft/s]' : la vitesse verticale de l'avion 
        - 'dx [ft/s]' : la vitesse horizontale de l'avion 
        - 'ON_AIR'    : un boléen valant True lorsque l'avion est en mouvement
    """

    # facteur de convertion de MACH en Feet/s
    MachToFeetS = 1125.33

    # boleen de mouvement de l'avion 
    ON_AIR = df['M [Mach]']>0

    # gradient des vitesses verticales
    dy= np.empty(len(df))
    y = df['ALT [ft]'].values
    dy[:-1] = y[1:]-y[:-1]
    dy[-1]=0

    # sauvegarde des donnees nouvellement calculees
    df['dy [ft/s]'] =dy
    df['dx [ft/s]'] = df['M [Mach]']*MachToFeetS
    df['ON_AIR'] = ON_AIR
    return df



def angle_analysis(df, stick_range = [2,33], physical_range = [-18,18]):
    """
    @author : Kraemer Valentin 
    angle_analysis 

    desc : analyse de la relation linéaire entre l'angle des vitesses et l'angle du levier

    Input :
        df : dataframe d'un vol 
        stick_range (facultatif): range de validité du levier où celui-ci n'est pas bloqué
        physical_range (facultatif):  range pour laquelle les angles de l'avion par rapport à la verticale sont physiquement acceptables

    Output : 

    """
    # acquisition des vitesses horizontales et verticales 
    df_speed = add_speed(df)

    # indices selectionnnes : il s'agit des instants durant lequels l'avion n'est pas immobile
    id_on_air =  df_speed['ON_AIR']
    id_stick_interval = (df_speed['TLA_1 [deg]']>stick_range[0]) * (df_speed['TLA_1 [deg]']<stick_range[1])
    id_study = id_on_air*id_stick_interval
    tps = df_speed[id_study].index.values

    # stockage des variables d'interet 
    vx = df_speed['dx [ft/s]'][id_study].values
    vy = df_speed['dy [ft/s]'][id_study].values 
    theta = np.arctan(vy/vx)*180/np.pi                      # converti en degres
    theta_levier = df_speed['TLA_1 [deg]'][id_study].values 

    # data_frame intermedaire 
    df_interm = pd.DataFrame({'theta_levier': theta_levier, 'theta_vitesse' : theta, 'vx': vx, 'vy':vy, 'time' :tps }).set_index('time')
    id_physically_admitted = (df_interm['theta_vitesse']>physical_range[0])*(df_interm['theta_vitesse']<physical_range[1])

    # data_frame d'analyse
    df_study = df_interm[id_physically_admitted]

    return df_study



###
# Author : Kraemer Valentin 
# Introduction a ces fonctions : vkr_flight_analysis.ipynb
# Date : 17 nov 2023
# Version 1.1
###


def normalize(df, l = ['NAIV_1 [bool]', 'NAIV_2 [bool]','PRV_1 [bool]', 'PRV_2 [bool]']):
    """
    @author : Kraemer Valenitn 
    normalize function 

    desc : élimination des valeurs boléennes du dataframe de vol et renommage des variables sans les crochets d'unité par souci de comptatibilité python

    Input : 
        df : dataframe d'un vol 
        l  : (facultatif) liste des colonnes à supprimer du dataframe pour éviter notamment les divisions par zéro

    Output : 
        df_norm : dataframe normalisé. 
    """
    if len(l)!=0 :
        df=  df.drop(columns = l)
    newname = []
    for col in df.columns :
        newname.append(re.sub(r' \[.*?\]', '', col))
    X = df.values
    #on pouvait reprendre la normalisation de sklearn
    X_norm = (X - np.mean(X,axis = 0))/np.std(X, axis = 0)
    df_norm = pd.DataFrame(data = X_norm, columns=newname, index= df.index)

    return df_norm


def regression(df, formula) :
    """
    @author : Kraemer Valentin 
    regression function 

    desc : fonction d'automatisation de la regression utilisable compatible avec la fonction generate_df_reg pour une implémentation sous dask

    Input : 
        df : dataframe d'étude 
        formula : la formule de regression à appliquer
    
    Output : 
        reg_dict : un dictionnaire contenant les informations nécessaires à une analyse multi-vol à savoir 
            - le R2 de regression                       (R2)
            - le nombre d'observation                   (N_observations)
            - le test de durbin waston                  (Durbin_Watson)
            - la liste des paramètres de regression     (ParamName)
            - les valeurs des paramètres de regression  (Paramètres)
            - la pvaleur de chaque paramètres           (pvaleur)
            - les intervalles de confiances de chq prm  (Intervals)

    """
    products = extraire_noms_variables(formula)
    df2 = df[products].copy()
    import re 
    for col in df.columns :
        newname = re.sub(r' \[.*?\]', '', col)
        df2.rename(columns={col:newname}, inplace=True)

    if len(df)<2 :
        r2 = np.nan, 
        pvals = np.nan*np.zeros((len(products)))
        IC = np.nan*np.zeros((len(products)))
        n_obs = np.nan
        params_list = np.nan*np.zeros((len(products)))
        params_list = products
    model = ols(formula, data = df2).fit()
    r2 = model.rsquared
    pvals = model.pvalues
    IC = model.conf_int(0.05)
    n_obs = model.nobs
    params_list = model.params
    reg_dict = {'R2' :r2, 'pvaleur' : pvals.values, 'N_observations':n_obs, 'Paramètres' : params_list.values, 'Intervals': IC.values, 'ParamName': list(params_list.index) , 'Durbin_Watson' : durbin_watson(model.resid)}
    return reg_dict

def generate_df_reg (all_reg):
    """
    @author : Kraemer Valentin 
    generate_df_reg function 

    desc : génération d'un dataframe contenant les analyses regressives d'un avion sur tous ses vols

    Input : 
        all_reg : liste de dictionnaire de la forme de l'output de manipulate_dataframe.regression;
            -> celui ci provient de la sortie de la computation de dask.map_partition(lambda df: regression(df))
    
    Output : 
        dataframe contenant toutes les analyses regressives de all_reg stockées sous forme de dataframe pour une meilleure manipulation    
    """
    records = all_reg.index.values
    Params = all_reg[0]['ParamName']
    R2 = np.empty(len(records))
    N_obs= np.empty(len(records))
    pvals = np.empty((len(records), len(Params)))
    params_val = np.empty((len(records), len(Params)))
    IC_0 =  np.empty((len(records), len(Params)))
    IC_1 =  np.empty((len(records), len(Params)))
    DurbinWatson =  np.empty(len(records))

    for i, record in enumerate(records) :
        record_dict = all_reg[record]
        R2[i] = record_dict['R2']
        N_obs[i] = record_dict['N_observations']
        pvals[i, :] = record_dict['pvaleur']
        params_val[i, :] = record_dict['Paramètres']
        IC_0[i,:] = record_dict['Intervals'][:,0]
        IC_1[i,:] = record_dict['Intervals'][:,1]
        DurbinWatson[i] = record_dict['Durbin_Watson']

    df_reg = pd.DataFrame({'record': records, 'R2': R2, 'N_obs': N_obs, 'Durbin_Waston': DurbinWatson}).set_index('record')
    for i, param in enumerate(Params) :
        df_reg['coeff_'+param] = params_val[:,i]
        df_reg['pval_'+param] = pvals[:,i]
        df_reg['IC0_'+param] = IC_0[:,i]
        df_reg['IC1_'+param] = IC_1[:,i]

    return df_reg


def eliminate_records(df):
    """
    @author : Husson Félix 
   eliminate_records function 

    desc :  Le but de la fonction eliminate_records est de vérifier la différence entre l'altitude minimum et maximum est d'au plus 15000 ft si c'est le cas alors elle renvoit False et True sinon.

    Input : 
        df : le dataframe d'un vol d'avion
            
    
    Output : 
       un boléen -> True: on elimine
                 -> False: on garde 
    """
    alt_min=df['ALT [ft]'].min()
    alt_max=df['ALT [ft]'].max()
    alt_range=alt_max-alt_min
    bol=False
    
    if alt_range<15000:
        bol=True
        
    return bol

def deriv_glissante(df):       
    """
    @author : Husson Félix 
   deriv_glissante function 

    desc : on cree une fonction qui prend un data frame qui l'augmente de la valeur dy en ft/s et qui renvoit  un nouveau dataframe contenant que la montée 

    Input : 
        #ATTENTION LA FONCTION PRENDS EN ENTREE DES DONNEES NORMALISEE d'un vol d'avion
        df : le dataframe
        
            
    
    Output : 
       un boléen -> True: on elimine
                 -> False: on garde 
    """

    dy=np.zeros(len(df))
    
    #on fait une moyenne glissante pour éviter d'être sensible aux bruit. En effet pour le cacul de dérivée le bruit 
    #fausse trés rapidement les données
    y = df['ALT'].rolling(window = 20).mean()
    I = range(y.index[0], y.index[-1],20)
    #calcul de la derivée
    dy[0:len(I)-1] = y[I[1:]].values- y[I[:-1]].values
    #creation d'une nouvelle colonne dans le dataframe
    df['dy']=dy
    #on selectionne le dataframe où les dérivées sont plus grande que 0.01 (la montée)
    df_monte=df[df['dy']>0.01]
    I4=np.zeros(len(df_monte))
    #on verifie qu' avec un shift des données on retombe bien sur les mêmes indices cela permet d'éviter 
    # de prendre en compte des valeurs qui ne serait pas dans la phase de la montée 
    #Attention cette façon de faire est lié aux cas d'un vol d'avion (l'hypothèse admise est que l'avion ne monte qu'une fois)
    #Et s'il existe plus de 6 données anormale consécutives alors elles seront prise en compte 
    
    I4[5:]=df_monte.index[5:]==(df_monte.index+5)[:-5]
    I4[:5]=1
    df_monte2=df_monte[I4==1]
    


    return [df_monte2]
