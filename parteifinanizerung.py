import fnmatch
import os
import re

import numpy as np
import openpyxl
import pandas
import seaborn as sns
import matplotlib.pyplot as plt
pandas.options.mode.copy_on_write = True
def rightstrip_with_wildcards(s, pattern):
    regex_pattern = fnmatch.translate(pattern) + '$'
    regex = re.compile(regex_pattern)
    return regex.sub("", s)
PARTY_NAME = "Akteur"
NUMBEROFDONORSPERPLOT = 10
MULTIPLEPLOTSINONE =True

wb = openpyxl.load_workbook("./2023_Parteifinanzierung.xlsx")
sheet = wb.sheetnames
print(sheet)
df = pandas.read_excel("./2023_Parteifinanzierung.xlsx", sheet_name="Zuwendungen")
print(df)

for offenlegungslauf in set(df["Offenlegungslauf"]):

    ldf = df[df["Offenlegungslauf"] == offenlegungslauf]
    ldf.drop(columns=["Offenlegungslauf", "Datenstand", "Datum", "Gewährungsdatum der Zuwendung"], inplace=True)
    parties = list(set(ldf[PARTY_NAME]))
    numparties = len(parties)
    fig, axes = plt.subplots(int(np.ceil(np.sqrt(numparties))), int(np.ceil(np.sqrt(numparties))), figsize=(20, 20))


    os.system(f"mkdir -p plots/{offenlegungslauf.replace(' ','')}")

    for party in parties:
        partydonors = ldf[ldf[PARTY_NAME] == party]
        partydonors["Merged_Name"] = partydonors["Name des Urhebers der Zuwendung"].fillna('') + ' ' + partydonors[
            "Vorname des Urhebers der Zuwendung"].fillna('') + ' ' + partydonors["Wohnsitzgemeinde"].fillna('')
        partydonors["Merged"] = partydonors["Firma des Urhebers der Zuwendung"].fillna('') + ' ' + partydonors[
            "Merged_Name"].str.strip()
        partydonors["Merged"] = partydonors["Merged"].apply(lambda row: row.rstrip(" "))
        partydonors["Merged"] = partydonors["Merged"].apply(lambda row: rightstrip_with_wildcards(row, "(*)"))
        a = partydonors.nlargest(NUMBEROFDONORSPERPLOT, "Wert (in CHF)")
        if MULTIPLEPLOTSINONE:
            ax = axes.flatten()[parties.index(party)]
            ax.pie(a["Wert (in CHF)"], labels=a["Merged"])
            ax.set_title(f"Zuwendungen {party} {offenlegungslauf}")
        else:
            plt.pie(a["Wert (in CHF)"], labels=a["Merged"])
            plt.title(f"Zuwendungen {party} {offenlegungslauf}")
            # plt.show()
            plt.tight_layout()
            plt.savefig(f"plots/{offenlegungslauf.replace(' ','')}/{party}.png")
            plt.clf()
    if MULTIPLEPLOTSINONE:
        for j in range(len(parties), len(axes.flatten())):
            fig.delaxes(axes.flatten()[j])

        fig.tight_layout(rect=[0,0, 1, 0.95])
        plt.suptitle(f"Zuwendungen für {offenlegungslauf}")
        plt.savefig(f"plots/{offenlegungslauf.replace(' ','')}/all.png")