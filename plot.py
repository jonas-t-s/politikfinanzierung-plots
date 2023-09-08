import os

import matplotlib.pyplot as plt
import pandas
import seaborn as sns
import pandas as pd

gesamtbetragdereinnahmen = "Gesamtbetrag der Einnahmen (in CHF)"

MUTTERPARTEI = "Parteizugehörigkeit (Mutterpartei)"
PLOTLOCATION = "plots/"
gesamteinnahmen = pd.read_csv("Gesamteinnahmen.csv")
zuwendungen = pd.read_csv("Zuwendungen.csv")

def getfigax():
    return plt.subplots(1,1, figsize=((10,10)))
def beautifyplot(fig, ax, force_no_scientific=False):
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, horizontalalignment="right")
    if force_no_scientific:
        ax.yaxis.get_major_formatter().set_scientific(False)
    fig.tight_layout()


for Offenlegungslauf in set(gesamteinnahmen["Offenlegungslauf"]):

    os.system(f"mkdir -p \'{PLOTLOCATION}{Offenlegungslauf}\'")

    # Plots the average per party
    fig, ax = getfigax()
    daten = gesamteinnahmen[gesamteinnahmen["Offenlegungslauf"] == Offenlegungslauf]
    sns.barplot(daten, x=MUTTERPARTEI, y=gesamtbetragdereinnahmen, ax=ax)
    plt.tight_layout()
    fig.suptitle("Durschnittliches gemeldetes Budget pro Partei")
    beautifyplot(fig, ax)
    plt.savefig(PLOTLOCATION+ Offenlegungslauf +"/" + "durchschnittlich gemeldetes Budget_pro_partei.svg")
    # Plots the total budget per party
    fig, ax = getfigax()
    aufsumiertebudgets = dict()
    for index, row in gesamteinnahmen.iterrows():
        alt = aufsumiertebudgets[row[MUTTERPARTEI]] if row[MUTTERPARTEI] in aufsumiertebudgets else 0
        aufsumiertebudgets[row[MUTTERPARTEI]] = alt + row[gesamtbetragdereinnahmen]
    df = pd.DataFrame(columns=[MUTTERPARTEI, "Budget"])
    # aufsumiertebudgets = pd.DataFrame.from_dict(aufsumiertebudgets, orient="index")
    for key,value in aufsumiertebudgets.items():
        new_record = pd.DataFrame([[key, value]], columns=df.columns)
        df = pd.concat([df, new_record], ignore_index=True)
    df = df.sort_values("Budget", ascending=False)
    df["Budget"] = df["Budget"].astype(int)
    sns.barplot(df, x=MUTTERPARTEI, y="Budget")
    beautifyplot(fig, ax)
    plt.suptitle("Totales Budget pro Partei")
    plt.savefig(PLOTLOCATION + Offenlegungslauf + "/" + "Totales Budget pro Partei.svg" )
