import sys
from utils import posts
from update import *


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


if __name__ == "__main__":

    if len(sys.argv) == 2:
        
        if sys.argv[1] == "select":
            qual = input("Select day to test: ")
        else:
            qual = sys.argv[1]
        test_post(qual)
        
    elif len(sys.argv) == 3:
        test_post(sys.argv[1], sys.argv[2])
    else:
        test_posts()