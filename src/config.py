"""
ComplaintScope: Configuration loader, seed setting, path helpers, and logging setup.
"""
from pathlib import Path
import os
import sys
import random
import logging
import json
import datetime
import subprocess
import yaml
import numpy as np

# Root directory of the repository
ROOT_DIR = Path(__file__).resolve().parent.parent

_CONFIG_CACHE = None

def get_project_root() -> Path:
    return ROOT_DIR

def load_config(config_path: str = None) -> dict:
    """Load config.yaml and cache it."""
    global _CONFIG_CACHE
    if config_path is None:
        target_path = ROOT_DIR / "config.yaml"
    else:
        target_path = Path(config_path)
    
    if not target_path.exists():
        raise FileNotFoundError(f"Configuration file not found at {target_path}")
        
    with open(target_path, "r", encoding="utf-8") as f:
        _CONFIG_CACHE = yaml.safe_load(f)
    return _CONFIG_CACHE

def get_path(path_key: str, default: str = None) -> Path:
    """Resolve a path from config['paths'] relative to ROOT_DIR."""
    cfg = load_config()
    paths = cfg.get("paths", {})
    if path_key in paths:
        return ROOT_DIR / paths[path_key]
    if default is not None:
        return ROOT_DIR / default
    raise KeyError(f"Path key '{path_key}' not found in configuration paths.")

def set_seeds(seed: int = None) -> int:
    """Set random seeds across standard library, numpy, and torch (if installed)."""
    if seed is None:
        cfg = load_config()
        seed = cfg.get("seed", 42)
    
    random.seed(seed)
    np.random.seed(seed)
    os.environ["PYTHONHASHSEED"] = str(seed)
    
    try:
        import torch
        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)
    except ImportError:
        pass
        
    return seed

def setup_logger(name: str = "complaintscope", log_file: str = None, level: int = logging.INFO) -> logging.Logger:
    """Configure structured logging."""
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Avoid duplicate handlers if called multiple times
    if logger.handlers:
        return logger
        
    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] [%(name)s]: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler
    if log_file is None:
        log_dir = ROOT_DIR / "results" / "metrics"
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / "execution.log"
    else:
        log_file = Path(log_file)
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
    file_handler = logging.FileHandler(str(log_file), encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger

def save_run_metadata(phase_name: str, duration_sec: float, extra_meta: dict = None) -> Path:
    """Update results/metrics/run_metadata.json with phase timings and library versions."""
    meta_path = get_path("results_metrics_dir") / "run_metadata.json"
    meta_path.parent.mkdir(parents=True, exist_ok=True)
    
    metadata = {}
    if meta_path.exists():
        try:
            with open(meta_path, "r", encoding="utf-8") as f:
                metadata = json.load(f)
        except Exception:
            metadata = {}
            
    cfg = load_config()
    
    # Git commit hash if in a git repo
    git_hash = "unknown"
    try:
        git_hash = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"], 
            cwd=str(ROOT_DIR), 
            stderr=subprocess.DEVNULL
        ).decode("utf-8").strip()
    except Exception:
        pass
        
    # Library versions
    lib_versions = {
        "python": sys.version.split()[0],
        "numpy": np.__version__,
    }
    for mod in ["scipy", "pandas", "sklearn", "nltk", "spacy", "gensim", "networkx", "torch"]:
        try:
            m = __import__(mod)
            lib_versions[mod] = getattr(m, "__version__", "installed")
        except ImportError:
            lib_versions[mod] = "not_installed"
            
    metadata["project"] = cfg.get("project_name", "ComplaintScope")
    metadata["mode"] = cfg.get("mode", "fast")
    metadata["seed"] = cfg.get("seed", 42)
    metadata["git_hash"] = git_hash
    metadata["environment"] = lib_versions
    metadata["last_updated"] = datetime.datetime.now().isoformat()
    
    if "phases" not in metadata:
        metadata["phases"] = {}
        
    metadata["phases"][phase_name] = {
        "duration_sec": round(duration_sec, 2),
        "completed_at": datetime.datetime.now().isoformat(),
        **(extra_meta or {})
    }
    
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
        
    return meta_path

if __name__ == "__main__":
    cfg = load_config()
    seed = set_seeds()
    logger = setup_logger()
    logger.info(f"Loaded config for {cfg['project_name']} (mode: {cfg['mode']}, seed: {seed})")
