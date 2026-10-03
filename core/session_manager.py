from pathlib import Path
import fastf1

DEFAULT_CACHE_DIR = (Path(__file__).resolve().parent.parent / ".fastf1-cache")

def setup_cache(cache_dir = DEFAULT_CACHE_DIR) -> None:
    if cache_dir is None:
        cache_dir = DEFAULT_CACHE_DIR

    cache_path = Path(cache_dir).resolve()
    cache_path.mkdir(parents=True, exist_ok=True)

    fastf1.Cache.enable_cache(str(cache_path))

def load_gp_session(year: int, gp_name: str, session_type: str):
    if not year:
        raise ValueError("Year not valid")
    if not gp_name:
        raise ValueError("GP name not valid")
    if not session_type:
        raise ValueError("Session type not valid")

    session = fastf1.get_session(year, gp_name, session_type)
    session.load()
    return session
