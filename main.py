import urllib.request
import http.client
from bs4 import BeautifulSoup
import pandas as pd
import json
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import time
# pip install pandas
# pip install beautifulsoup4
# pip install seaborn
# pip install numpy

# Config #

config_combat_csv = "final_combats.csv"
config_stats_url = "https://pokemondb.net/pokedex/stats/gen"
config_max_gen = 2 #8
sns.set_theme(style="darkgrid")

# Program #
# CSV Reading

data_arr = {
    "_index": {}
}
plot_data = {}

def get_csv_row(row):
    if len(row) < 3:
        return
        
    if row[0] in data_arr["_index"]:
        gen_id_0 = "gen_"+data_arr["_index"][row[0]]
        if (row[0] == row[2]):
            data_arr[gen_id_0][row[0]]["good_matchup"].append(row[1])
        else:
            data_arr[gen_id_0][row[0]]["bad_matchup"].append(row[1])
    if row[1] in data_arr["_index"]:
        gen_id_1 = "gen_"+data_arr["_index"][row[1]]
        if (row[1] == row[2]):
            data_arr[gen_id_1][row[1]]["bad_matchup"].append(row[0])
        else:
            data_arr[gen_id_1][row[1]]["bad_matchup"].append(row[0])


def get_csv_data():
    data_frame = pd.read_csv(config_combat_csv, header=None)
    for row in data_frame.itertuples(index=False, name=None):
        get_csv_row(row)

# Scrapping

def get_stats_from_gen(gen_num):
    request = urllib.request.build_opener()
    request.addheaders = [('User-Agent', 'v1')]
    urllib.request.install_opener(request)
    response = urllib.request.urlopen(config_stats_url + gen_num)
    
    raw_html = response.read().decode("utf-8")
    soup = BeautifulSoup(raw_html, "html.parser")
    
    dex_table = soup.find("table", id="pokedex")
    
    mon_rows = dex_table.find_all(['tr'])
    for row in mon_rows:
        td_items = row.find_all(['td'])
        if (len(td_items) < 10 or not td_items[0].has_attr("data-sort-value")):
            continue
        
        if not "gen_"+gen_num in data_arr:
            data_arr["gen_"+gen_num] = {}

        if td_items[1].find("small"):
            continue

        data_arr["_index"][td_items[0].get("data-sort-value")] = gen_num
        data_arr["gen_"+gen_num][td_items[0].get("data-sort-value")] = {
            "name": td_items[1].get_text(),
            "types": [i.get_text() for i in td_items[2].find_all('a')],
            "stats_total": td_items[3].get_text(),
            "stats_hp": td_items[4].get_text(),
            "stats_attack": td_items[5].get_text(),
            "stats_defence": td_items[6].get_text(),
            "stats_sp_attack": td_items[7].get_text(),
            "stats_sp_defence": td_items[8].get_text(),
            "stats_speed": td_items[9].get_text(),
            "good_matchup": [],
            "bad_matchup": [],
        }


def get_stats_data():
    for i in range(1, config_max_gen + 1):
        print("Gen " + str(i))
        get_stats_from_gen(str(i))
        time.sleep(1)


def calculate_se_weaknesses(types):
    pass

def cleanup_data():
    for gen in list(data_arr.keys()):
        if gen == "_index":
            continue

        plot_data[gen] = {
            "name": [],
            "good_matchups": [],
            "bad_matchups": [],
            "stats_total": []
        }

        for pokemom in list(data_arr[gen].values()):
            if pokemom["good_matchup"] and pokemom["bad_matchup"]:
                plot_data[gen]["name"].append(pokemom["name"])
                plot_data[gen]["good_matchups"].append(len(pokemom["good_matchup"]))
                plot_data[gen]["bad_matchups"].append(len(pokemom["bad_matchup"]))
                plot_data[gen]["stats_total"].append(int(pokemom["stats_total"]))
                """ plot_data[gen]["se_weaknesses"].append(calculate_se_weaknesses(value["types"])) """


def generate_plot():
    for gen, row in plot_data.items():
        dataframe = pd.DataFrame(row)
        fig, ax1 = plt.subplots(
            figsize=(max(32, len(dataframe) * 0.5), 7)
        )        

        sns.barplot(
            data=dataframe,
            x="name",
            y="stats_total",
            ax=ax1,
            color="cornflowerblue",
            label="Total stats"
        )

        ax1.set_xlabel("Pokemon")
        ax1.set_ylabel("Total stats", color="dimgray")
        ax1.tick_params(axis="y", labelcolor="dimgray")
        ax1.tick_params(axis="x", rotation=75)
        ax1.set_ylim(bottom=0)

        ax2 = ax1.twinx()

        sns.lineplot(
            data=dataframe,
            x="name",
            y="good_matchups",
            ax=ax2,
            color="green",
            marker="o",
            label="Good matchups"
        )

        sns.lineplot(
            data=dataframe,
            x="name",
            y="bad_matchups",
            ax=ax2,
            color="red",
            marker="o",
            label="Bad matchups"
        )

        ax2.set_ylabel("Matchup score")

        ax2.set_ylim(bottom=0)
        ax1.margins(x=0)
        ax2.margins(x=0)
        fig.subplots_adjust(left=0.03, right=0.97)

        plt.title("Generation " + gen.replace("gen_",""))
        plt.show()


get_stats_data()
get_csv_data()
cleanup_data()
generate_plot()


# Debugging #
""" print(json.dumps(data_arr, indent=4)) """

""" with open('result.json', 'w') as file:
    json.dump(data_arr, file) """

# python -m venv env
# env\Scripts\activate