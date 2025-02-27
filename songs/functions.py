# from config import CONFIG
# import random

# def get_slides(request):
#     return random.sample(CONFIG["slides"], 3)

from config import CONFIG
import random

def get_slides(request):
    interested_ids = CONFIG["interested_slide_ids"]
    slides = CONFIG["slides"]

    # Get slides matching interested_ids
    interested_slides = [slide for slide in slides if slide["id"] in interested_ids]

    # Get remaining slides excluding interested ones
    remaining_slides = [slide for slide in slides if slide["id"] not in interested_ids]

    # Fill remaining slots randomly
    num_to_pick = 3 - len(interested_slides)
    selected_slides = interested_slides + random.sample(remaining_slides, num_to_pick)

    return selected_slides
