import fastf1
import os

DEFAULT_CACHE_DIR = ".fastf1-cache"

def setup_cache(cache_dir = DEFAULT_CACHE_DIR) -> None:
    os.makedirs(cache_dir, exist_ok=True)
    fastf1.Cache.enable_cache(cache_dir)

def load_gp_session(year, gp_name, session_type):
    session = fastf1.get_session(year, gp_name, session_type)
    session.load()
    return session
