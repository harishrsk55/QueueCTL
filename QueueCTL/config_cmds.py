from utils import load, save
import os

config_file = "data/config.json"
config_lock = "data/config.lock"

def load_config():
    if not os.path.exists(config_file):
        return {"max_retries": 3, "base_delay": 2}
    cfg = load(config_file, config_lock)
    if not cfg:
        return {"max_retries": 3, "base_delay": 2}
    return cfg

def save_config(cfg):
    save(cfg, config_file, config_lock)

def config(args):
    cfg = load_config()
    if args.dest == "max-retries":
        cfg["max_retries"] = args.count
        save_config(cfg)
        print(f"max-retries updated to {args.count}")
    elif args.dest == "base":
        cfg["base_delay"] = args.count
        save_config(cfg)
        print(f"base delay updated to {args.count}")
