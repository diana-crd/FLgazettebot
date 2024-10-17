import json
from re import finditer, UNICODE

# from utils import wiki

wiki_url = "https://fallenlondon.wiki/wiki/"

with open("info/items.json") as f:
    items_dict: dict[str, list] = json.load(f)
    for item_name, item_d in items_dict.items():
        item_d["value"] = item_name

with open("info/wiki.json") as f:
    wiki_dict: dict[str, list] = json.load(f)

def open_post(json_path):
    with open(json_path) as f:
        post_dict = json.load(f)

    for qual, item in post_dict.items():
        if qual in ["qualities", "title", "generic intro"]:
            continue

        for block in item:
            if not "type" in block.keys():
                block["type"] = "plain"
            if not "switch" in block.keys():
                block["switch"] = False

    if "demand_generic" in post_dict.keys():
        demands = [quality for quality in wiki_dict.keys() if "demand" in quality]
        for demand in demands:
            if demand in post_dict.keys():
                post_dict[demand] = [*post_dict["demand_generic"], *post_dict[demand]]
            else:
                post_dict[demand] = post_dict["demand_generic"]

    return post_dict


def format_intro(post_dict):
    content = [{
        "type": "text",
        "subtype": "heading1",
        "text": post_dict["title"]
        }]
    content.extend([
       {
        "type": "text",
        "text": paragraph
        } for paragraph in post_dict["generic intro"]
    ])
    
    return content

def format_text(text, value_dict):
    fmt_dict = {}
    for key, val in value_dict.items():
        if type(val) == str:
            fmt_dict[key] = val

    if value_dict["alias"]:
        fmt_dict["name"] = value_dict["alias"]
    else:
        fmt_dict["name"] = value_dict["value"]

    return text.format(**fmt_dict)

def format_block(block_text, block_type):
    block = {
        "type": "text",
        "text": block_text    
    }
    if "u" in block_type:
        block["subtype"] = "unordered-list-item"

    return block

def select_switch(block, value):

    for key, text in block.items():
        if value == key or (value in key and "_" in key):
            return text
    return False

def format_quality(section, quality_name, quality_value):
    content = []

    if "demand" in quality_name:
        value_dict = wiki_dict[quality_name]
    else:
        value_dict = wiki_dict[quality_name]["values"][quality_value]


    for block in section:

        if "text" in block.keys():
            block_template = block["text"]
        else:
            if not (block_template := select_switch(block, quality_value)):
                continue
        
        if block["source"] == "value":
            block_texts = [format_text(block_template, value_dict)]
        elif block["source"] == "none":
            block_texts = [block_template]
        else: 
            block_texts = []
            for item_name in value_dict["items"]:
                block_texts.append(format_text(block_template, items_dict[item_name]))

        for text in block_texts:
            content.append(format_block(text, block["type"]))

    return content


def format_wikiurl(string: str):
    rgx_simple = r"\[\[([\(\)_ \-\w]+)\]\]"
    rgx_alias = r"\[\[([\(\)_ \-\w]+)\|([\(\)_ \-\w]+)\]\]"
    simple_links = finditer(rgx_simple, string, UNICODE)
    for match in simple_links:
        url = wiki_url + match.group(1)
        href = f"<a href=\"{url}\">{match.group(1)}</a>"
        string = string.replace(match.group(0), href)

    alias_links = finditer(rgx_alias, string, UNICODE)
    for match in alias_links:
        url = wiki_url + match.group(1)
        href = f"<a href=\"{url}\">{match.group(2)}</a>"
        string = string.replace(match.group(0), href)

    return string

def format_npfhtml(block: dict):
    rgx_bold = r"<b>([,() \-\w\d']+)</b>"

    string = block["text"]
    if (not "formatting" in block.keys()) or (not block["formatting"]):
        formatting = []        
    else:
        formatting = block["formatting"]

    bold_text = finditer(rgx_bold, string, UNICODE)
    for match in bold_text:
        start = string.find(match.group(0))
        end = start + len(match.group(1))
        formatting.append({
            "start": start,
            "end": end,
            "type": "bold",
        })
        update_npformatting(formatting, prev_length=len(match.group(0)))
        print(formatting[-1])

        string = string.replace(match.group(0), match.group(1))

    block["text"] = string
    block["formatting"] = formatting


def format_npfwikiurl(block: dict):
    rgx_simple = r"\[\[([\(\)_,:.' \-éèòàù\w]+)\]\]"
    rgx_alias = r"\[\[([\(\)_,:.' \-éèòàù\w]+)\|([\(\)_,:.' \-éèòàù\w]+)\]\]"

    if "formatting" in block.keys():
        formatting = block["formatting"]
    else:
        formatting = []

    string: str = block["text"]
    simple_links = finditer(rgx_simple, string, UNICODE)

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
        update_npformatting(formatting, prev_length=len(match.group(0)))

        string = string.replace(match.group(0), match.group(1), 1)

    alias_links = finditer(rgx_alias, string, UNICODE)
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
        update_npformatting(formatting, prev_length=len(match.group(0)))
        string = string.replace(match.group(0), match.group(2))

    block["text"] = string
    block["formatting"] = formatting

def format_npfall(content):
    for block in content:
        if "[[" in block["text"]:
            format_npfwikiurl(block)
        if "<" in block["text"]:
            format_npfhtml(block)
        trim_brackets(block)

def trim_brackets(block):

    if block["text"][:2] == "[[":
        block["text"] = block["text"][2:]
        for format in block["formatting"]:
            format["start"] -= 2
            format["end"] -= 2

def update_npformatting(formatting, prev_length):
    start = formatting[-1]["start"]
    end = formatting[-1]["end"]
    shift = prev_length - (end - start)
    for format_item in formatting[:-1]:
        if format_item["start"] >= end:
            format_item["start"] -= shift
            format_item["end"] -= shift

 
def test_quality(section, quality):

    content = []
    quality_range = wiki_dict[quality]["all_values"].split(" ")
    print(quality_range)
    quality_values = range(int(quality_range[1]), 1 + int(quality_range[2]))

    for int_value in quality_values:
        value = str(int_value)
        nu_block = format_quality(section, quality, value)
        if nu_block: content.extend(nu_block)
    
    return content