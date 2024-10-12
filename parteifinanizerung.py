import fnmatch
import os
import re

import numpy as np
import openpyxl
import pandas
import seaborn as sns
import matplotlib.pyplot as plt
from difflib import SequenceMatcher

COLNAME_AMOUNT = "Wert (in CHF)"

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
def renamesimilar(df: pandas.DataFrame, column: str, threshold: float = 0.9):
    droppedindexes = []
    for index, row in df.iterrows():
        for otherindex, otherrow in df.iterrows():
            if index == otherindex or (index in droppedindexes or otherindex in droppedindexes):
                continue
            similarity = SequenceMatcher(None, row[column].lower(), otherrow[column].lower()).ratio()
            if similarity > threshold:
                df.at[index, column] = otherrow[column]
    return df
for offenlegungslauf in set(df["Offenlegungslauf"]):

    ldf = df[df["Offenlegungslauf"] == offenlegungslauf]
    ldf.drop(columns=["Offenlegungslauf", "Datenstand", "Datum", "Gewährungsdatum der Zuwendung"], inplace=True)
    parties = list(set(ldf[PARTY_NAME]))
    numparties = len(parties)
    fig, axes = plt.subplots(int(np.ceil(np.sqrt(numparties))), int(np.ceil(np.sqrt(numparties))), figsize=(20, 20))
    plt.rcParams.update({'font.size': 14})

    os.system(f"mkdir -p plots/{offenlegungslauf.replace(' ', '')}")
    
    for party in parties:
        partydonors = ldf[ldf[PARTY_NAME] == party]
        partydonors["Merged_Name"] = partydonors["Name des Urhebers der Zuwendung"].fillna('') + ' ' + partydonors[
            "Vorname des Urhebers der Zuwendung"].fillna('') + ' ' + partydonors["Wohnsitzgemeinde"].fillna('')
        partydonors["Merged"] = partydonors["Firma des Urhebers der Zuwendung"].fillna('') + ' ' + partydonors[
            "Merged_Name"].str.strip()
        partydonors["Merged"] = partydonors["Merged"].apply(lambda row: row.rstrip(" "))
        partydonors["Merged"] = partydonors["Merged"].apply(lambda row: rightstrip_with_wildcards(row, "(*)"))
        mpartydonors = renamesimilar(partydonors, "Merged")
        a = partydonors.nlargest(NUMBEROFDONORSPERPLOT, "Wert (in CHF)")
        if MULTIPLEPLOTSINONE:
            ax = axes.flatten()[parties.index(party)]
            ax.pie(a["Wert (in CHF)"], labels=a["Merged"])
            ax.set_title(f"Zuwendungen {party} {offenlegungslauf}")
        else:
            plt.pie(a["Wert (in CHF)"], labels=a["Merged"])
            title = f"Zuwendungen {party} {offenlegungslauf}"
            if NUMBEROFDONORSPERPLOT < np.inf:
                f"Zuwendungen {party} Top {NUMBEROFDONORSPERPLOT}"
            plt.title(title)
            # plt.show()
            plt.tight_layout()
            plt.savefig(f"plots/{offenlegungslauf.replace(' ', '')}/{party}.png")
            plt.clf()
    if MULTIPLEPLOTSINONE:
        for j in range(len(parties), len(axes.flatten())):
            fig.delaxes(axes.flatten()[j])

        fig.tight_layout(rect=[0, 0, 1, 0.95])
        suptitle = f"Zuwendungen für {offenlegungslauf}"
        if NUMBEROFDONORSPERPLOT < np.inf:
            suptitle += f" Top (n={NUMBEROFDONORSPERPLOT})"
        plt.suptitle(suptitle)
        plt.savefig(f"plots/{offenlegungslauf.replace(' ', '')}/all.png")

    plt.clf()
    ldf["Merged_Name"] = ldf["Name des Urhebers der Zuwendung"].fillna('') + ' ' + ldf[
        "Vorname des Urhebers der Zuwendung"].fillna('') + ' ' + ldf["Wohnsitzgemeinde"].fillna('')
    ldf["Merged"] = ldf["Firma des Urhebers der Zuwendung"].fillna('') + ' ' + ldf[
        "Merged_Name"].str.strip()
    ldf["Merged"] = ldf["Merged"].apply(lambda row: row.rstrip(" "))
    ldf["Merged"] = ldf["Merged"].apply(lambda row: rightstrip_with_wildcards(row, "(*)"))
    ldf["Merged"] = ldf["Merged"].apply(lambda row: row.lstrip(" "))
    ldf["Merged"] = ldf["Merged"].apply(lambda row: row.rstrip(" "))
    ldf = renamesimilar(ldf, "Merged")
    plotlocation = f"plots/{offenlegungslauf.replace(' ', '')}/DONORS"
    os.system(f"mkdir -p {plotlocation}")
    plt.rcParams.update({'font.size': 40})

    for donor in set(ldf["Merged"]):
        rowsdonor = ldf[ldf["Merged"] == donor]
        numrecipents = len(rowsdonor)
        sqrt_numrecpitents = int(np.ceil(np.sqrt(numrecipents)))
        df = pandas.DataFrame(columns=[PARTY_NAME, "DONOR" ,COLNAME_AMOUNT])
        for index, row in rowsdonor.iterrows():
            party = row[PARTY_NAME]
            merged = False
            for p2 in df[PARTY_NAME]:
                if SequenceMatcher(None, party, p2).ratio() > 0.9:
                    df[df[PARTY_NAME] == p2][COLNAME_AMOUNT] += row[COLNAME_AMOUNT]
                    merged = True
                    break
            if not merged:
                df.loc[len(df)] = [party, "DONOR", row[COLNAME_AMOUNT]]
        rowsdonor = df
        plt.pie(rowsdonor["Wert (in CHF)"], labels=rowsdonor[PARTY_NAME],
                autopct=lambda p: '{:.0f}'.format(p * rowsdonor[COLNAME_AMOUNT].sum() / 100))
        plt.title(f"Zuwendungen {donor}\n{offenlegungslauf}")
        plt.tight_layout()
        plt.savefig(f"{plotlocation}/{donor.replace('/', '')}.png")
        plt.clf()

def main():
    pass
if __name__ == '__main__':
    main()