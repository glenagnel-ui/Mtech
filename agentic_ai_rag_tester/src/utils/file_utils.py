import pandas as pd
from datetime import datetime
import os
from pathlib import Path
from typing import List, Dict

def save_to_csv(data: List[Dict], directory: str, prefix: str = "data") -> str:
    """
    Saves a list of dictionaries to a CSV file timestamped to avoid overwrites.
    """
    if not data:
        return ""
        
    Path(directory).mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = os.path.join(directory, f"{prefix}_{timestamp}.csv")
    
    df = pd.DataFrame(data)
    df.to_csv(filepath, index=False)
    return filepath

def load_from_csv(filepath: str) -> List[Dict]:
    """Loads a CSV into a list of dicts."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Missing file: {filepath}")
    df = pd.read_csv(filepath)
    # Handle NaNs
    df = df.fillna("")
    return df.to_dict('records')
