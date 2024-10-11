import requests
import json
from re import findall, search, finditer
from os.path import isfile
from time import sleep


api_endpoint = "https://fallenlondon.wiki/w/api.php"
wiki_url = "https://fallenlondon.wiki/wiki/"

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
    
    with open("info/raw_items.json", 'w', encoding='utf-8') as f:
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

def get_latest_values(qualities):
    min_update = 99991001110511 
    values_dict = {}
    
    for quality in qualities:
        cval, last_update = get_current_value(quality)
        values_dict[quality] = cval
        min_update = min(min_update, int(last_update))
    
    return values_dict, min_update


def format_wikiurl(string: str):
    rgx_simple = r"\[\[([ \-\w]+)\]\]"
    rgx_alias = r"\[\[([ \-\w]+)\|([ \-\w]+)\]\]"
    simple_links = finditer(rgx_simple, string)
    for match in simple_links:
        url = wiki_url + match.group(1)
        href = f"<a href=\"{url}\">{match.group(1)}</a>"
        string = string.replace(match.group(0), href)

    alias_links = finditer(rgx_alias, string)
    for match in alias_links:
        url = wiki_url + match.group(1)
        href = f"<a href=\"{url}\">{match.group(2)}</a>"
        string = string.replace(match.group(0), href)

    return string

def format_npfwikiurl(block: dict):
    rgx_simple = r"\[\[([ \-\w']+)\]\]"
    rgx_alias = r"\[\[([ \-\w']+)\|([ \-\w']+)\]\]"

    formatting = []
    simple_links = finditer(rgx_simple, string)

    for match in simple_links:
        url = wiki_url + match.group(1).replace(" ", "_")
        start = string.find(match.group(0))
        end = start + len(match.group(1))
        formatting.append({
            "start": start,
            "end": end,
            "type": "link",
            "url": url
        })
        print(formatting[-1])

        string = string.replace(match.group(0), match.group(1))

    alias_links = finditer(rgx_alias, string)
    for match in alias_links:
        url = wiki_url + match.group(1).replace(" ", "_")
        start = string.find(match.group(0))
        end = start + len(match.group(2))
        formatting.append({
            "start": start,
            "end": end,
            "type": "link",
            "url": url
        })
        print(formatting[-1])
        string = string.replace(match.group(0), match.group(2))

    block["formatting"] = formatting


if __name__ == "__main__":
    parse_quality_values()
    dump_items()