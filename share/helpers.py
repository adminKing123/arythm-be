from config import CONFIG

GET_APP_REDIRECT_URI = lambda path="": f'{CONFIG["SHARE_APP_REDIRECT_URL"]}{path}'
GET_SRC_URI = lambda path="": f'{CONFIG["SHARE_SRC_URI"]}{path}'
GET_SONGS_ARTISTS = lambda artists: ", ".join(aa.artist.name for aa in artists)

SHARE_API_MAPS = {
    "SONG": lambda id: f"song/{id}",
    "PLAYLIST": lambda id: f"playlist/{id}",
}

def is_bot(request):
    user_agent = request.META.get("HTTP_USER_AGENT", "").lower()
    return any(bot in user_agent for bot in ["bot", "spider", "crawler", "curl", "facebookexternalhit", "whatsapp", "discord", "telegram", "linkedin", "webexteams"])

def format_time(seconds):
    minutes, secs = divmod(int(seconds), 60)
    return f"{minutes:02}:{secs:02}"

def make_og_tags(meta):
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta property="og:title" content="{meta['title']}">
        <meta property="og:description" content="{meta['description']}">
        <meta property="og:image" content="{meta['image']}">
        <meta property="og:url" content="{meta['url']}">
        <meta property="og:type" content="{meta['type']}">
    </head>
    </html>
    """

def default_og():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta property="og:title" content="ARhythm - Discover & Enjoy Music" />
        <meta property="og:description" content="Listen to your favorite songs, explore new music, and create personalized playlists on ARhythm." />
        <meta property="og:image" content="https://arhythm.netlify.app/favicon.ico" />
        <meta property="og:url" content="https://arhythm.netlify.app" />
        <meta property="og:type" content="website" />
    </head>
    </html>
    """
