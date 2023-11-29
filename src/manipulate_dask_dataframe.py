# -*- coding: utf-8 -*-
"""
Module src - fonctions de manipulation de dask.dataframe caractérisiques du projet - projet de statistiques descriptives MACS3
@author: Kraemer Valentin 
"""
__date__ = "2023-11-29"
__version__ = '1.0'



import dask.dataframe as dd

# basic func
from src import lire_hdf_dask, interval_conf

# plot_fun
from src import afficher_significativite, afficher_coeff 

# manipulate_dataframe 
from src import regression, generate_df_reg, angle_analysis, normalize


###
# Author : Kraemer Valentin 
# Introduction a ces fonctions : vkr_flight_analysis.ipynb
# Date : 29 nov 2023
# Version 1.0
###


def eliminate_records(df):
    """
    eliminate record function
    @author : Félix Husson 

    Input : 
        dataframe à analyser
    
    Output :
        bol : un boléen qui indique True lorsque le dataframe est problématique (à savoir lorsque l'amplitude des altitudes de l'avion est inférieure à 15k pieds)
    """
    # recuperation du max et du min d'altitude 
    alt_min=df['ALT [ft]'].min()
    alt_max=df['ALT [ft]'].max()
    alt_range=alt_max-alt_min
    bol=False
    
    # verification de l'amplitude d'altitude
    if alt_range<15000:
        bol=True
    return bol

def select_ddf(ddf):
    """
    select_ddf function 
    @author : Kraemer Valentin 
    Surcouche de la fonction eliminate_records de Félix Husson 

    Input : 
        ddf : dask.dataframe que l'on souhaite traiter pour éliminer les dataframes problématiques 

    Output :
        ddf : dask.dataframe sans les dataframes problématiques 
    """
    I = ddf.map_partitions(lambda df: eliminate_records(df)).compute()
    return ddf.partitions[I==False]


def analyse_flight(file,data_dir, window = 1): 
    """
    analyse_flight function
    @author : Kraemer Valentin 

    Input : 
        file : nom du fichier.h5 de données dask d'un avion 
        data_dir : le repertoire dans lequel est stocké la donnée extracted (cf lire_hdf_dask de basic_func.py)
        window  : la fenetre glissante que l'on applique pour l'affichage de l'évolution des coefficients - default : pas de fenetre  
    
    Ouput : 
        affichage graphique du R2, nombre d'observations, des coeeficients de regression 
        df_reg : le dataframe de regression 
    """
    # selection du dask.dataframe non corrompu
    ddf = select_ddf(lire_hdf_dask(file, repertoire= data_dir))

    # nouveau dask dataframe sur les angles
    ddf_study= ddf.map_partitions(lambda df : angle_analysis(df))

    # regression lineaire sur chaque vols
    formula = 'theta_levier~theta_vitesse'
    regression_dict = ddf_study.map_partitions(lambda df : regression(df, formula)).compute()

    # collecte de la liste des dictionnaires sous la forme d'un dataframe 
    df_reg = generate_df_reg(regression_dict)


    # affichage graphique 
    afficher_significativite(df_reg)
    print(f"La valeur moyenne de R^2 est de {df_reg['R2'].mean()} pour un intervalle de confiance à 0.95 de {interval_conf('R2', df_reg, alpha = 0.95)}")
    print(f"La valeur moyenne du test de Durbin Waston est de {df_reg['Durbin_Waston'].mean()} pour un intervalle de confiance à 0.95 de {interval_conf('Durbin_Waston', df_reg, alpha = 0.95)}")

    afficher_coeff(df_reg, norm = False, window=window)
    print(f"La valeur moyenne du coeff  est de {df_reg['coeff_theta_vitesse'].mean()} pour un intervalle de confiance à 0.95 de {interval_conf('coeff_theta_vitesse', df_reg, alpha = 0.95)}")
    print(f"La valeur moyenne du coeff  est de {df_reg['coeff_Intercept'].mean()} pour un intervalle de confiance à 0.95 de {interval_conf('coeff_Intercept', df_reg, alpha = 0.95)}")

    return df_reg

def analyse_flight_norm(file,data_dir, window = 1): 
    """
    analyse_flight_norm function
    @author : Kraemer Valentin 

    IDEM que analyse flight mais normalisé

    Input : 
        file : nom du fichier.h5 de données dask d'un avion 
        data_dir : le repertoire dans lequel est stocké la donnée extracted (cf lire_hdf_dask de basic_func.py)
        window  : la fenetre glissante que l'on applique pour l'affichage de l'évolution des coefficients - default : pas de fenetre 
    
    Ouput : 
        affichage graphique du R2, nombre d'observations, des coeeficients de regression 
        df_reg : le dataframe de regression 
    """
    # selection du dask.dataframe non corrompu
    ddf = select_ddf(lire_hdf_dask(file, repertoire= data_dir))

    # nouveau dask dataframe sur les angles
    ddf_study= ddf.map_partitions(lambda df : angle_analysis(df))

    # normalisation du jeu de données 
    ddf_study_norm = ddf_study.map_partitions(lambda df : normalize(df,  l =[]))

    # regression lineaire sur chaque vols
    formula = 'theta_levier~theta_vitesse'
    regression_dict = ddf_study_norm.map_partitions(lambda df : regression(df, formula)).compute()

    # collecte de la liste des dictionnaires sous la forme d'un dataframe 
    df_reg = generate_df_reg(regression_dict)


    # affichage graphique 
    afficher_significativite(df_reg)
    print(f"La valeur moyenne de R^2 est de {df_reg['R2'].mean()} pour un intervalle de confiance à 0.95 de {interval_conf('R2', df_reg, alpha = 0.95)}")
    print(f"La valeur moyenne du test de Durbin Waston est de {df_reg['Durbin_Waston'].mean()} pour un intervalle de confiance à 0.95 de {interval_conf('Durbin_Waston', df_reg, alpha = 0.95)}")

    afficher_coeff(df_reg, norm = True, window = window)
    print(f"La valeur moyenne du coeff  est de {df_reg['coeff_theta_vitesse'].mean()} pour un intervalle de confiance à 0.95 de {interval_conf('coeff_theta_vitesse', df_reg, alpha = 0.95)}")
    print(f"La valeur moyenne du coeff  est de {df_reg['coeff_Intercept'].mean()} pour un intervalle de confiance à 0.95 de {interval_conf('coeff_Intercept', df_reg, alpha = 0.95)}")

    return df_reg

