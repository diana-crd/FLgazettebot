import requests
import json
from re import findall, search
from os.path import isfile

api_endpoint = "https://fallenlondon.wiki/w/api.php"
headers = {
    'User-Agent': 'FLGazetteBot/0.1 python requests',
    'From': "carduccidiana1@gmail.com"}


rgx_string = (r'<section begin=\\"Current Value\\"/>(\d+)<section end=\\"Current Value\\"/>\|'
              r'<section begin=\\"Last Updated\\"/>(\d+)<section end=\\"Last Updated\\"/>')
qvalue_string = r"Value(\d+) = ([ \-\w]+)\\n"

with open("info/pagetitle.json") as f:
    wikipages: dict[str, str] = json.load(f)

with open("info/wiki.json") as f:
    wikidict = json.load(f)

def get_wikitext(page):
    params = {
        "action": "parse",
        "prop": "wikitext",
        "format": "json",
        "page": page
    }
    wiki_req = requests.get(url=api_endpoint, params=params, headers=headers)
    #TODO: catch bad requests
    wiki_text = wiki_req.content.decode()

    return wiki_text

def parse_quality_values():
    qvalues = {}

    for quality, history in wikipages.items():
        title = history[:-8]
        quality_dict = {"name": title, "name/history": history, "alias": ""}

        if not "demand" in quality:
            wikitxt = get_wikitext(title)
            values_list = findall(qvalue_string, wikitxt) # [("value", "name")...]
            values_dict = dict()
            for value, name in values_list:
                val_dict = {"name":name, "alias":""}
                values_dict[value] = val_dict
            quality_dict["values"]=values_dict

        qvalues[quality] = quality_dict

    with open('info/raw_wiki.json', 'w', encoding='utf-8') as f:
        json.dump(qvalues, f, ensure_ascii=False, indent=4)

def dump_items():
    items_list = []
    items_dict = {}
    for quality, quality_dict in wikidict.items():
        if quality == "demand":
            continue

        for value in quality_dict["values"].values():
            if "items" in value.keys():
                items_list.extend(value["items"])
    items_set = set(items_list)
    for item in items_set:
        items_dict[item] = {"alias": "", "ratvalue": "", "value": ""}
    
    with open("info/items.json", 'w', encoding='utf-8') as f:
        json.dump(items_dict, f, ensure_ascii=False, indent=4)


def parse_current_value(txt):

    re_parsed = search(rgx_string, txt)
    current_value = re_parsed.group(1)
    last_update = re_parsed.group(2)
    return current_value, last_update

def get_current_value(quality):

    if not quality in wikipages.keys():
        return None
    
    params = {
        "action": "parse",
        "prop": "wikitext",
        "format": "json"
    }

    params.update(page=wikidict[quality]["name/history"])
    wiki_req = requests.get(url=api_endpoint, params=params, headers=headers)
    #TODO: catch bad requests
    wiki_txt = wiki_req.content.decode()
    value_update = parse_current_value(wiki_txt)

    return value_update

if __name__ == "__main__":
    parse_quality_values()
    dump_items()