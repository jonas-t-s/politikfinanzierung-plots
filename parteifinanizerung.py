import fnmatch
import os
import random
import re

import numpy as np
import pandas
import seaborn as sns
import matplotlib.pyplot as plt
from difflib import SequenceMatcher
import argparse
COLORS = {
    "SP": "red",
    "SVP": "yellow",
    "FDP.Die Liberalen": "blue",
    "Die Mitte": "orange"
}

def get_color(party):
    for key in COLORS.keys():
        if key in party:
            return COLORS[key]
    return [random.random(), random.random(), random.random()]
COLNAME_AMOUNT = "Wert (in CHF)"

pandas.options.mode.copy_on_write = True
def rightstrip_with_wildcards(s, pattern):
    regex_pattern = fnmatch.translate(pattern) + '$'
    regex = re.compile(regex_pattern)
    return regex.sub("", s)
PARTY_NAME = "Akteur"
NUMBEROFDONORSPERPLOT = 10


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


def plotpartydonorsperparty(filelocation, showrest, MULTIPLOTSINONE=True, threshold=0.9,fileformat : str = "png"):
    global rowsdonor
    df = get_excel_data(filelocation)
    print(df)

    for offenlegungslauf in set(df["Offenlegungslauf"]):

        ldf = extract_year_and_relevantdata(df, offenlegungslauf)
        parties = list(set(ldf[PARTY_NAME]))
        numparties = len(parties)
        if MULTIPLOTSINONE:
            fig, axes = plt.subplots(int(np.ceil(np.sqrt(numparties))), int(np.ceil(np.sqrt(numparties))), figsize=(21, 21))
        else:
            fig, axes = plt.subplots(1,1, figsize=(21, 21))
        plt.rcParams.update({'font.size': 14})

        os.makedirs(f"plots/{offenlegungslauf.replace(' ', '')}", exist_ok=True)

        for party in parties:
            partydonors = ldf[ldf[PARTY_NAME] == party]
            partydonors["Merged_Name"] = partydonors["Name des Urhebers der Zuwendung"].fillna('') + ' ' + partydonors[
                "Vorname des Urhebers der Zuwendung"].fillna('') + ' ' + partydonors["Wohnsitzgemeinde"].fillna('')
            partydonors["Merged"] = partydonors["Firma des Urhebers der Zuwendung"].fillna('') + ' ' + partydonors[
                "Merged_Name"].str.strip()
            partydonors["Merged"] = partydonors["Merged"].apply(lambda row: row.rstrip(" "))
            partydonors["Merged"] = partydonors["Merged"].apply(lambda row: rightstrip_with_wildcards(row, "(*)"))
            partydonors = renamesimilar(partydonors, "Merged", threshold=threshold)
            a = partydonors.nlargest(NUMBEROFDONORSPERPLOT, "Wert (in CHF)")

            if showrest and len(partydonors)> len(a):
                a.loc[len(a)] = {"Merged": "Rest", COLNAME_AMOUNT: 0, "Akteur": party}

                a.at[len(a)-1, COLNAME_AMOUNT] = partydonors["Wert (in CHF)"].sum() - a["Wert (in CHF)"].sum()
            def func(pct, allvals):
                absolute = int(pct / 100. * allvals[COLNAME_AMOUNT].sum())
                return "{:.1f}%\n({:d})".format(pct, absolute)

            colors = sns.color_palette('husl', len(a))
            if MULTIPLOTSINONE:
                ax = axes.flatten()[parties.index(party)]
                ax.pie(a["Wert (in CHF)"], labels=a["Merged"], autopct=lambda pct: func(pct, a), colors=colors)
                ax.set_title(f"Zuwendungen {party} {offenlegungslauf}")
            else:
                plt.pie(a["Wert (in CHF)"], labels=a["Merged"], autopct=lambda pct: func(pct, a), colors=colors)
                title = f"Zuwendungen {party} {offenlegungslauf}"
                if NUMBEROFDONORSPERPLOT < np.inf:
                    title = f"Zuwendungen {party} Top {NUMBEROFDONORSPERPLOT}"
                plt.title(title)
                # plt.show()
                plt.tight_layout()
                plt.savefig(f"plots/{offenlegungslauf.replace(' ', '')}/{party}.{fileformat}")
                plt.clf()
        if MULTIPLOTSINONE:
            for j in range(len(parties), len(axes.flatten())):
                fig.delaxes(axes.flatten()[j])

            fig.tight_layout(rect=[0, 0, 1, 0.95])
            suptitle = f"Zuwendungen für {offenlegungslauf}"
            if NUMBEROFDONORSPERPLOT < np.inf:
                suptitle += f" Top (n={NUMBEROFDONORSPERPLOT})"
            plt.suptitle(suptitle)
            plt.savefig(f"plots/{offenlegungslauf.replace(' ', '')}/all.{fileformat}")

        plt.clf()


def extract_year_and_relevantdata(df, offenlegungslauf):
    ldf = df[df["Offenlegungslauf"] == offenlegungslauf]
    ldf.drop(columns=["Offenlegungslauf", "Datenstand", "Datum", "Gewährungsdatum der Zuwendung"], inplace=True)
    return ldf


def get_excel_data(filelocation):
    df = pandas.read_excel(filelocation, sheet_name="Zuwendungen")
    return df


def plotperdonor(filelocation: str = "./2023_Parteifinanzierung.xlsx", threshold=0.9, fileformat : str = "png"):
    global rowsdonor
    df = get_excel_data(filelocation)
    for offenlegungslauf in set(df["Offenlegungslauf"]):
        ldf = extract_year_and_relevantdata(df, offenlegungslauf)
        ldf["Merged_Name"] = ldf["Name des Urhebers der Zuwendung"].fillna('') + ' ' + ldf[
            "Vorname des Urhebers der Zuwendung"].fillna('') + ' ' + ldf["Wohnsitzgemeinde"].fillna('')
        ldf["Merged"] = ldf["Firma des Urhebers der Zuwendung"].fillna('') + ' ' + ldf[
            "Merged_Name"].str.strip()
        ldf["Merged"] = ldf["Merged"].apply(lambda row: row.rstrip(" "))
        ldf["Merged"] = ldf["Merged"].apply(lambda row: rightstrip_with_wildcards(row, "(*)"))
        ldf["Merged"] = ldf["Merged"].apply(lambda row: row.lstrip(" "))
        ldf["Merged"] = ldf["Merged"].apply(lambda row: row.rstrip(" "))
        ldf = renamesimilar(ldf, "Merged", threshold=threshold)
        plotlocation = f"plots/{offenlegungslauf.replace(' ', '')}/DONORS"
        os.system(f"mkdir -p {plotlocation}")
        plt.rcParams.update({'font.size': 40})
        for donor in set(ldf["Merged"]):
            rowsdonor = ldf[ldf["Merged"] == donor]
            numrecipents = len(rowsdonor)
            sqrt_numrecpitents = int(np.ceil(np.sqrt(numrecipents)))
            df = pandas.DataFrame(columns=[PARTY_NAME, "DONOR", COLNAME_AMOUNT])
            for index, row in rowsdonor.iterrows():
                party = row[PARTY_NAME]
                merged = False
                for p2 in df[PARTY_NAME]:
                    if SequenceMatcher(None, party, p2).ratio() > threshold:
                        df[df[PARTY_NAME] == p2][COLNAME_AMOUNT] += row[COLNAME_AMOUNT]
                        merged = True
                        break
                if not merged:
                    df.loc[len(df)] = [party, "DONOR", row[COLNAME_AMOUNT]]
            rowsdonor = df

            plt.pie(rowsdonor["Wert (in CHF)"], labels=rowsdonor[PARTY_NAME],
                    autopct=lambda p: '{:.0f}'.format(p * rowsdonor[COLNAME_AMOUNT].sum() / 100), colors=[get_color(row) for row in rowsdonor[PARTY_NAME]])
            plt.title(f"Zuwendungen {donor}\n{offenlegungslauf}")
            plt.tight_layout()
            plt.savefig(f"{plotlocation}/{donor.replace('/', '')}.{fileformat}")
            plt.clf()
    return df


def main():
    parser = argparse.ArgumentParser(description='Parse financial contributions and generate plots.')
    parser.add_argument('--input_file', type=str, help='Path to the Excel file with the data', default="./2023_Parteifinanzierung.xlsx", required=False)
    parser.add_argument('--num_donors', type=int, default=10, help='Number of top donors to display in each plot')
    parser.add_argument("--show-rest", help="Show a reminder position in the plots", action="store_true")
    parser.add_argument("--top-n", type=int, default=np.inf, help="Only show the top n donors in each plot.")
    parser.add_argument("--multiple-plots-in-one", help="Show multiple plots in one figure", action="store_true")
    parser.add_argument("--threshold", type=float, default=0.9, help="Threshold for merging donors. Default: 0.9 (90%)")
    parser.add_argument("--only-partyplots", help="Only generate party plots. Do not generate donor plots.", action="store_true")
    parser.add_argument("--file-format", type=str, default="png", help="File format for the plots. Default: png. ")
    args = parser.parse_args()
    global NUMBEROFDONORSPERPLOT
    NUMBEROFDONORSPERPLOT = args.num_donors

    plotpartydonorsperparty(args.input_file, args.show_rest, args.multiple_plots_in_one, args.threshold, args.file_format)
    print(
        f"Plots are saved in the plots/ folder."
    )
    if not args.only_partyplots:
        plotperdonor(args.input_file, args.threshold, args.file_format)

if __name__ == '__main__':
    main()