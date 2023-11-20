import matplotlib.pyplot as plt

def afficher_significativite(df_reg) :
    records = df_reg.index.values
    fig, axs = plt.subplots(2, figsize = (10,8))
    axs[0].plot(records, df_reg['R2'].values)
    axs[1].plot(records, df_reg['N_obs'].values)
    axs[0].set_xlabel('records')
    axs[0].set_ylabel('R2')
    axs[0].set_ylim((0,1))
    axs[1].set_xlabel('records')
    axs[1].set_ylabel("Nombre d'observations")