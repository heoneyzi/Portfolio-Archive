"""DiDeMo moment retrieval adapter; requires an explicit dataset directory."""
from ftf_vtg.evaluation import evaluate

def vmr_DiDeMo(json_dir, parameters=None):
    return evaluate('vmr_didemo', json_dir, parameters=parameters)
