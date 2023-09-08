import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

gesamteinnahmen = pd.read_csv("Gesamteinnahmen.csv")
zuwendungen = pd.read_csv("Zuwendungen.csv")

for Offenlegungslauf in set(gesamteinnahmen["Offenlegungslauf"]):
    fig, ax = plt.subplots(1,1, figsize=((8,8)))
    daten = gesamteinnahmen[gesamteinnahmen["Offenlegungslauf"] == Offenlegungslauf]
    sns.barplot(daten, x="Parteizugehörigkeit (Mutterpartei)", y="Gesamtbetrag der Einnahmen (in CHF)", ax=ax)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, horizontalalignment="right")
    plt.tight_layout()
    fig.suptitle("Durschnittliches gemeldetes Budget")
    plt.savefig(Offenlegungslauf+ ".svg")