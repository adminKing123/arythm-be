from config import CONFIG
import random

def get_slides(request):
    return random.sample(CONFIG["slides"], 3)
