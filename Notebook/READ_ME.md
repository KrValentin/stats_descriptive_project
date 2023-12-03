Authors :  Kraemer Valentin et HUSSON Félix
Date    :  3 dec 2023
Desc    :  Description du livrable 


Le livrable comprend les notebooks suivant :
    - vkr_data_frame_analysis         .ipynb : analyse d'un vol d'un seul avion pour appréhender le fil directeur de notre étude

    - vkr_data_frame_analysis_02      .ipynb : tentative d'amélioration du modèle en ajoutant des variables de contexte

    - vkr_data_flight_function        .ipynb : description/implémentation des fonctions généralisées d'analyse (regressions) compatible avec un dask.dataframe, application au cas N1~N2+T1 

    - vkr_data_flight_analysis        .ipynb : analyse sur tous les dataframe d'un même vol,utilisation de dask

    - vkr_data_fleet_analysis         .ipynb : analyse de toute la flotte d'avion 

    - Felix_clustering_valentin       .ipynb : poursuite de l'analyse de Valentin (clustering et ACP) 
    
    - EGT_felix                       .ipynb : Tentative de retrouver les résultats du TD: croissance de l'EGT max 

    - Felix002                        .ipynb : Comparaison entre étude globale et études sur la phase de la monté (Corrélation et ACP )

    - Analyse_Avions                  .ipynb : On reprends l'analyse sur le coefficient de corrélation sur TOUT les avions

Ces notebooks sont à lire dans l'ordre ci-dessus pour une meilleure compréhension. 


Rattaché au livrable se trouve les fichiers sources python dans le dossier src :
    - __init__                        .py

    - basic_func                      .py  : fonctions basiques non forcément maison

    - manipulate_dataframe            .py  : fonctions de manipulation de dataframe spécifique au problème

    - manipulate_dask_dataframe       .py  : fonctions de manipulations de dask.dataframe

    - plot_fun                        .py  : fonctions d'affichage