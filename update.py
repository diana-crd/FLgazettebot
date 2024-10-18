from datetime import datetime,timezone
from time import sleep
import sys
import json
import pytumblr2 as pyt
from utils import posts, wiki

wq_templates = {
    "Monday": "rat_closing",
    "Tuesday": "tuesday",
    "Wednesday": None,
    "Thursday": "sacroboscan",
    "Friday": "rat_opening",
    "Saturday": None,
    "Sunday": None
}

weekly_tags = {
    "Monday": ["The Rat Market"],
    "Tuesday": ["The Bone Market", "The Copper Quarter", "Khan's Heart"],
    "Wednesday": None,
    "Thursday": ["The Sacroboscan Calendar"],
    "Friday": ["The Rat Market"],
    "Saturday": None,
    "Sunday": None
}

blogname = "theunexpurgatedlondongazette"
default_tags = ["The Unexpurgated London Gazette", "Fallen London", "Fallen London World Qualities"]
fmt_timestr = "%Y%m%d"

def tumblr_login():
    with open("apikeys.json") as f:
        apikeys = json.load(f)
        
    client = pyt.TumblrRestClient(**apikeys)

    return client

def test_post(day, quality=None, draft_post=True):

    if not wq_templates[day]:
        return None
    
    template_path = f"content/{wq_templates[day]}.json"
    post_template = posts.open_post(template_path)

    if quality:
        qualities = [quality]
    
    else:
        to_check = post_template["qualities"]["to_check"]
        other_qualities = post_template["qualities"]["other"]
        qualities = to_check + other_qualities

    client = tumblr_login()
    print(f"{day}:")
    for quality in qualities:
        print(f"\t{quality}")
        content = [{
            "type": "text",
            "subtype": "heading1",
            "text": f"{day} {quality} test"
        }]
        content.extend(posts.test_quality(post_template[quality], quality))

        tags = ["test", day, quality]
        posts.format_npfall(content)
        if draft_post:
            result = client.create_post(blogname, content=content, tags=tags, state="draft")
            if "errors" in result.keys():
                for block in content[1:]:
                    sngl_result = client.create_post(blogname, content=[block], tags=tags, state="draft")
                    print(sngl_result)
        if not draft_post:
            for block in content:
                print(block)
                print(f"Text length: {len(block['text'])}")
        


def test_posts():
    for day in wq_templates.keys():
        test_post(day)


# not implemented: check for presence of live events
def live_event_check():
    pass

def wq_update():

    current_time = datetime.now(timezone.utc)
    day = current_time.strftime("%A")
    
    if not wq_templates[day]:
        return None
    
    time_str = current_time.strftime(fmt_timestr)

    time_update = time_str + "110000"
    # time_update = "00000000110000"

    template_path = f"content/{wq_templates[day]}.json"
    post_template = posts.open_post(template_path)


    to_check = post_template["qualities"]["to_check"]
    other_qualities = post_template["qualities"]["other"]
    qualities = to_check + other_qualities
    
    while True:
        
        current_values = wiki.get_current_values(*to_check)
        for quality_updates in current_values.values():
            last_updated = quality_updates["last_updated"]
            value = quality_updates["current_value"]
            # this behaviour is based on the fact that the only regular wq qualities with a possible "0" value are Rat Market presence (which changes predictably) and Demand qualities, which can remain at "0" over multiple weeks
            is_updated = (value == "0") or (last_updated >= time_update)
            if not is_updated:
                sleep(180)
                break
        
        else:
            break

    if other_qualities:
        current_values.update(wiki.get_current_values(*other_qualities))

    content = posts.format_intro(post_template)

    for quality in qualities:
        value = current_values[quality]["current_value"]
        section = post_template[quality]
        nu_block = posts.format_quality(section, quality, value)
        if nu_block: content.extend(nu_block)

    posts.format_npfall(content)
    
    tags = default_tags + weekly_tags[day]
    client = tumblr_login()
    result = client.create_post(blogname, content=content, tags=tags) # , state="draft")
    return result


if __name__ == "__main__":

    if len(sys.argv) > 1:
        task = sys.argv[1]
    else:
        task = "update"

    if task == "update":
        print(wq_update())
    elif task == "test":
        if len(sys.argv) == 3:
            test_post(sys.argv[2])
        elif len(sys.argv) == 4:
            test_post(sys.argv[2], sys.argv[3])
        else:
            test_posts()

    
