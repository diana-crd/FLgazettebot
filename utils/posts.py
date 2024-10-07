import json
from utils import wiki

with open("info/items.json") as f:
    items_dict: dict[str, list] = json.load(f)

with open("info/wiki.json") as f:
    wiki_dict: dict[str, list] = json.load(f)

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

def format_content(section, quality_name, quality_value):
    content = []
    quality_dict = wiki_dict[quality_name]
    
    if section["structure"] == "p":
        value_dict = quality_dict["values"][quality_value]
        if value_dict["alias"]:
            value_name = value_dict["alias"]
        else:
            value_name = value_dict["name"]

        item = value_dict["items"][0]
        item_info = items_dict[item]
        if item_info["alias"]:
            item_name = item_info["alias"]
        else:
            item_name = item

        text = section["p"].format(value=value_name, item=item_name, price=item_info["ratvalue"])
        content.append({"type": "text", "text": text})

    if section["structure"] == "p_u":
        value_dict = quality_dict["values"][quality_value]
        if value_dict["alias"]:
            value_name = value_dict["alias"]
        else:
            value_name = value_dict["name"]

        text = section["p"].format(value=value_name)
        content.append({"type": "text", "text": text})

        items = value_dict["items"]

        for item in items:
            item_info = items_dict[item]
            if item_info["alias"]:
                item_name = item_info["alias"]
            else:
                item_name = item

            text = section["u"].format(item=item_name, price=item_info["ratvalue"])
            content.append({"type": "text", "subtype": "unordered-list-item","text": text})
    
    if section["type"] == "demand":
        if quality_value in section.keys():
            text = section[quality_value].format(alias=quality_dict["alias"])
            content.append({"type": "text", "text": text})

            if quality_value in ("1", "2"):
                items = quality_dict["values"]["1"]["items"]
                for item in items:
                    item_info = items_dict[item]
                    if item_info["alias"]:
                        item_name = item_info["alias"]
                    else:
                        item_name = item

                    text = section["u"].format(item=item_name, price=item_info["ratvalue"])
                    content.append({"type": "text", "subtype": "unordered-list-item","text": text})

                if "p" in section.keys():
                    text = section["p"]
                    content.append({"type": "text", "text": text})
    
    return content