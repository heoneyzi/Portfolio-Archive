"""VidSTG temporal grounding adapter; no automatic hyperparameter search."""
from ftf_vtg.evaluation import evaluate

def vtg_VidSTG(json_dir, parameters=None):
    return evaluate('vtg_vidstg', json_dir, parameters=parameters)
