import urllib.request
import http.client
from bs4 import BeautifulSoup
import csv
import json

# Config #

config_combat_csv = "final_combats.csv"
config_stats_url = "https://pokemondb.net/pokedex/all"

# Program #
# CSV Reading

data_arr = {}

def get_csv_row(row):
    if len(row) < 3:
        return
        
    if row[0] in data_arr:
        if (row[0] == row[2]):
            data_arr[row[0]]["counters"].append(row[1])
        else:
            data_arr[row[0]]["loses"].append(row[1])
    if row[1] in data_arr:
        if (row[1] == row[2]):
            data_arr[row[1]]["counters"].append(row[0])
        else:
            data_arr[row[1]]["loses"].append(row[0])


def get_csv_data():
    with open(config_combat_csv, 'r') as csv_data:
        for row in csv.reader(csv_data):
            get_csv_row(row)

# Scrapping

def get_stats_data():
    request = urllib.request.build_opener()
    request.addheaders = [('User-Agent', 'v1')]
    urllib.request.install_opener(request)
    response = urllib.request.urlopen(config_stats_url)
    
    raw_html = response.read().decode("utf-8")
    soup = BeautifulSoup(raw_html, "html.parser")
    
    dex_table = soup.find("table", id="pokedex")
    
    mon_rows = dex_table.find_all(['tr'])
    for row in mon_rows:
        td_items = row.find_all(['td'])
        if (len(td_items) < 10 or not td_items[0].has_attr("data-sort-value")):
            continue
        
        data_arr[td_items[0].get("data-sort-value")] = {
            "name": td_items[1].get_text(),
            "types": [i.get_text() for i in td_items[2].find_all('a')],
            "stats_total": td_items[3].get_text(),
            "stats_hp": td_items[4].get_text(),
            "stats_attack": td_items[5].get_text(),
            "stats_defence": td_items[6].get_text(),
            "stats_sp_attack": td_items[7].get_text(),
            "stats_sp_defence": td_items[8].get_text(),
            "stats_speed": td_items[9].get_text(),
            "counters": [],
            "loses": [],
        }

print()
get_stats_data()
get_csv_data()
print(json.dumps(data_arr, indent=4))

# python -m venv env
# env\Scripts\activate