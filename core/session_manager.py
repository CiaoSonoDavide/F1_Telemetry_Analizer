import fastf1
import os

def setup_cache(cache_dir = '.fastf1-cache'):
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)
    fastf1.Cache.enable_cache(cache_dir)

def load_gp_session(year, gp_name, session_type):
    session = fastf1.get_session(year, gp_name, session_type)
    session.load()
    return session
