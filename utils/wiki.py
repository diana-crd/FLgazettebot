import requests
import json
from re import findall, search
from os.path import isfile
from time import sleep


api_endpoint = "https://fallenlondon.wiki/w/api.php"

headers = {
    'User-Agent': 'FLGazetteBot/1.0 python requests',
    'From': "carduccidiana1@gmail.com"}


rgx_string = (r'<section begin="Current Value"/>(\d+)<section end="Current Value"/>\|'
              r'<section begin="Last Updated"/>(\d+)<section end="Last Updated"/>')
qvalue_string = r"Value(\d+) = ([ \-\w]+)\\n"
equip_string = r"Effects(\d+) = {{IL\|([ \-\w]+)}} ([\-\+\d]+)"
item_type_string = r"Item Type = ([ \-\w]+)"
alt_item_type_string = r"{{(\w+)"
redirect_string = r"\[\[([\(\)_,:.' \-\w]+)\]\]"

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
    wiki_dict = wiki_req.json()
    if "error" in wiki_dict.keys():
        return None
    #TODO: catch bad requests
    wiki_text = wiki_dict["parse"]["wikitext"]["*"]
    if "REDIRECT" in wiki_text:
        tru_page = search(redirect_string, wiki_text)
        wiki_text = get_wikitext(tru_page)

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

def parse_item_stats(item):
    print(item)
    wikitxt = get_wikitext(item)
    stats = {}
    if wikitxt is None:
        return "custom", stats
    
    
    effects_list = findall(equip_string, wikitxt) # [("effectN", "stat", "stat_value")...]
    if not effects_list:
        try:
            item_type = search(alt_item_type_string, wikitxt).group(1)
        except:
            print(wikitxt)
    
    else:
        item_type = search(item_type_string, wikitxt).group(1)
        for effects in effects_list:
            stats[effects[1]] = effects[2]

    return item_type, stats

def parse_all_stats():
    with open("info/items.json") as f:
        items_dict = json.load(f)
    
    for item, item_dict in items_dict.items():
        if "type" in item_dict.keys():
            continue
        # if item_dict["type"] in ("Item", "Quality"):
        #     continue
        item_type, stats = parse_item_stats(item)
        item_dict["type"] = item_type
        item_dict["stats"] = stats
        
        if stats:
            perk_str = "grants "
            for stat, stat_value in stats.items():
                perk_str += f"{stat_value} {stat}, "
            item_dict["perk"] = perk_str[:-2]
    
    with open("info/items.json", 'w', encoding='utf-8') as f:
        json.dump(items_dict, f, ensure_ascii=False, indent=4)
            
    

def extract_dict_items(qdict):
    item_list = []
    if "item" in qdict.keys() and not "|" in qdict["item"]:
        item_list.append(qdict["item"])
    if "items" in qdict.keys():
        item_list.extend(qdict["items"])

    return item_list

def dump_items():
    items_list = []
    with open("info/items.json") as f:
        items_dict = json.load(f)

    default_dict = {"alias": "", "ratprice": "", "kind" :"", "perk": ""}

    for quality, quality_dict in wikidict.items():
        if quality == "demand":
            continue

        items_list.extend(extract_dict_items(quality_dict))
        if "values" in quality_dict.keys():
            for value_dict in quality_dict["values"].values():
                items_list.extend(extract_dict_items(value_dict))

    items_set = set(items_list)
    missing_items = [item for item in items_set if item not in items_dict.keys()]
    for item in missing_items:
        items_dict[item] = default_dict
    
    with open("info/items.json", 'w', encoding='utf-8') as f:
        json.dump(items_dict, f, ensure_ascii=False, indent=4)


def parse_current_value(txt):

    re_parsed = search(rgx_string, txt)
    try:
        current_value = re_parsed.group(1)
    except:
        print(txt)
        raise AttributeError()
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

    wiki_txt = wiki_req.json()["parse"]["wikitext"]["*"]
    value_update = parse_current_value(wiki_txt)

    return value_update

def get_latest_values(qualities):
    min_update = 99991001110511 
    values_dict = {}
    
    for quality in qualities:
        cval, last_update = get_current_value(quality)
        values_dict[quality] = cval
        min_update = min(min_update, int(last_update))
    
    return values_dict, min_update

def get_current_values(*qualities):

    if isfile("current_values.json"):
        with open("current_values.json") as f:
            prev_dict = json.load(f)
    else:
        prev_dict = {}
    
    if not qualities:
        qualities = wikipages.keys()

    current_dict = {}

    for quality in qualities:
        cval, last_update = get_current_value(quality)
        current_dict[quality] = dict(current_value=cval, last_updated=last_update)
    
    prev_dict.update(current_dict)

    with open("current_values.json", 'w', encoding='utf-8') as f:
        json.dump(prev_dict, f, ensure_ascii=False, indent=4)

    return current_dict

if __name__ == "__main__":
    # parse_quality_values()
    # dump_items()
    # parse_all_stats()
    get_current_values()