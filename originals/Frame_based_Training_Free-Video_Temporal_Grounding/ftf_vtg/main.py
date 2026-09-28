"""Training-free temporal localization from a precomputed similarity curve."""
import math
from numbers import Real
import numpy as np
import torch
from .segment_detector import detect_event_segments_with_gradient
from .segment_merger import generate_all_merge_candidates_by_gap
from .segment_scorer import compute_segment_score


def FTF_VTG(similarity_array, theta_high=0.1, lambda_weight=0.5, *,
            kernel_size=3, sigma=1.0, theta_low_ratio=0.5, min_seg_len=1,
            alpha=0.5, gap_threshold=100):
    """Return inclusive sample indices ``(start, end)``, or ``(None, None)``.

    Accepts a finite 1-D list/array/tensor or a single-row tensor. The released
    algorithm operates on one frame-query similarity curve, not raw video.
    Defaults preserve the original modular implementation.
    """
    scores = torch.as_tensor(similarity_array, dtype=torch.float32).detach().cpu()
    if scores.ndim == 2 and scores.shape[0] == 1:
        scores = scores[0]
    if scores.ndim != 1 or scores.numel() == 0:
        raise ValueError('Expected a non-empty 1-D similarity curve (or shape [1, T]).')
    if not torch.isfinite(scores).all():
        raise ValueError('Similarity values must be finite.')
    if not isinstance(kernel_size, int) or kernel_size < 1 or kernel_size % 2 == 0:
        raise ValueError('kernel_size must be a positive odd integer.')
    numeric = (sigma, theta_high, theta_low_ratio, min_seg_len, alpha, gap_threshold, lambda_weight)
    if not all(isinstance(value, Real) and math.isfinite(value) for value in numeric):
        raise ValueError('All numerical parameters must be finite real numbers.')
    if sigma <= 0 or theta_high < 0 or not 0 <= theta_low_ratio <= 1:
        raise ValueError('Require sigma > 0, theta_high >= 0, theta_low_ratio in [0, 1].')
    if not 0 <= alpha <= 1 or not 0 <= lambda_weight <= 1:
        raise ValueError('alpha and lambda_weight must be in [0, 1].')
    if min_seg_len < 1 or gap_threshold < 0:
        raise ValueError('Require min_seg_len >= 1 and gap_threshold >= 0.')
    if scores.numel() < max(3, (kernel_size - 1) // 2 + 1):
        return None, None
    segments, _, _ = detect_event_segments_with_gradient(
        scores, kernel_size=kernel_size, sigma=sigma, theta_high=theta_high,
        theta_low_ratio=theta_low_ratio, min_seg_len=min_seg_len, alpha=alpha)
    candidates = generate_all_merge_candidates_by_gap(segments, gap_threshold)
    curve = scores.numpy()
    if not candidates:
        return None, None
    return max(candidates, key=lambda segment: compute_segment_score(
        curve, *segment, lambda_weight=lambda_weight))
