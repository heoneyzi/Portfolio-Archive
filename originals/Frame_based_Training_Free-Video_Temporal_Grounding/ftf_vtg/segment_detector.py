import torch
import torch.nn.functional as F
import numpy as np
import cv2

def detect_event_segments_with_gradient(
    scores,
    kernel_size=7,
    sigma=1.0,
    theta_high=0.1,
    theta_low_ratio=0.5,
    min_seg_len=3,
    alpha=0.5
):
    if scores.ndim == 1:
        scores = scores.unsqueeze(0)
    B, T = scores.shape
    device = scores.device

    pad = (kernel_size - 1) // 2
    x = torch.arange(-pad, pad + 1).float()
    gk = torch.exp(-x**2 / (2 * sigma**2))
    gk /= gk.sum()
    gk = gk.view(1, 1, -1).to(device)
    smoothed = F.conv1d(F.pad(scores.unsqueeze(1), (pad, pad), mode='reflect'), gk).squeeze(1)

    scores_np = smoothed.squeeze(0).cpu().numpy().astype(np.float32)
    scores_2d = scores_np[None, :, None]
    morph_kernel = np.ones((kernel_size, 1), np.uint8)
    dilated = cv2.dilate(scores_2d, morph_kernel, iterations=1)
    eroded = cv2.erode(scores_2d, morph_kernel, iterations=1)
    morph_grad = (dilated - eroded).squeeze()

    grad1 = np.abs(np.gradient(scores_np))
    hybrid_grad = alpha * morph_grad + (1 - alpha) * grad1

    high_th = theta_high
    low_th = theta_high * theta_low_ratio
    strong = hybrid_grad > high_th
    weak = (hybrid_grad > low_th) & ~strong
    edge_mask = np.zeros_like(hybrid_grad, dtype=np.uint8)
    for i in range(1, T - 1):
        if strong[i]:
            edge_mask[i] = 1
        elif weak[i] and (edge_mask[i - 1] or edge_mask[i + 1]):
            edge_mask[i] = 1

    segments = []
    i = 0
    state = 'search_start'
    current_s = None
    current_e = None

    while i < T:
        if edge_mask[i]:
            if state == 'search_start':
                s_group = [(i, hybrid_grad[i])]
                j = i + 1
                while j < T and edge_mask[j]:
                    s_group.append((j, hybrid_grad[j]))
                    j += 1
                current_s = max(s_group, key=lambda x: x[1])
                i = j
                state = 'search_end'
                continue

            elif state == 'search_end':
                e_group = [(i, hybrid_grad[i])]
                j = i + 1
                while j < T and edge_mask[j]:
                    e_group.append((j, hybrid_grad[j]))
                    j += 1
                current_e = max(e_group, key=lambda x: x[1])
                i = j
                if current_s and current_s[0] < current_e[0]:
                    seg_len = current_e[0] - current_s[0]
                    if seg_len >= min_seg_len:
                        segments.append((current_s[0], current_e[0]))
                current_s, current_e = None, None
                state = 'search_start'
                continue
        i += 1

    return segments, hybrid_grad, scores_np