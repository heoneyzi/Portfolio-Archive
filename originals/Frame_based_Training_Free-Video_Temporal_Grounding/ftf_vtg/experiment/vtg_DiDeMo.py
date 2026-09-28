"""DiDeMo temporal grounding adapter; requires explicit paths."""
from ftf_vtg.evaluation import evaluate

def vtg_DiDeMo(json_dir, ground_truth, parameters=None):
    return evaluate('vtg_didemo', json_dir, ground_truth=ground_truth, parameters=parameters)
