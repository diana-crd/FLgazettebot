import json
from utils import wiki
from string import Formatter

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
        if qual in ["title", "generic intro"]:
            continue

        for block in item:
            if not "type" in block.keys():
                block["type"] = "reg"
            if not "switch" in block.keys():
                block["switch"] = False

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
            if quality_value in block.keys():
                block_template = block[quality_value]
            else: continue
        
        if block["source"] == "value":
            block_texts = [format_text(block_template, value_dict)]
        else: 
            block_texts = []
            for item_name in value_dict["items"]:
                block_texts.append(format_text(block_template, items_dict[item_name]))

        for text in block_texts:
            content.append(format_block(text, block["type"]))

    return content