import torch
import numpy as np
import torch.nn.functional as F
import cv2
# 가장 기본적인 구간 단위 만들기
def detect_event_segments_with_gradient(
    scores,
    kernel_size=7,
    sigma=1.0,
    theta_high=0.1,
    theta_low_ratio=0.5,
    min_seg_len=3,
    alpha=0.5  # Morph vs Gradient 가중합 비율
):
    if scores.ndim == 1:
        scores = scores.unsqueeze(0)
    B, T = scores.shape
    assert B == 1
    device = scores.device

    # ① Gaussian smoothing
    pad = (kernel_size - 1) // 2
    x = torch.arange(-pad, pad + 1).float()
    gk = torch.exp(-x**2 / (2 * sigma**2))
    gk /= gk.sum()
    gk = gk.view(1, 1, -1).to(device)
    smoothed = F.conv1d(F.pad(scores.unsqueeze(1), (pad, pad), mode='reflect'), gk).squeeze(1)

    # ② Morphological Gradient
    scores_np = smoothed.squeeze(0).cpu().numpy().astype(np.float32)
    scores_2d = scores_np[None, :, None]
    morph_kernel = np.ones((kernel_size, 1), np.uint8)
    dilated = cv2.dilate(scores_2d, morph_kernel, iterations=1)
    eroded = cv2.erode(scores_2d, morph_kernel, iterations=1)
    morph_grad = (dilated - eroded).squeeze()

    # ③ 1차 미분 Gradient
    grad1 = np.abs(np.gradient(scores_np))

    # ④ Morph Gradient + 1차 Gradient 병합
    hybrid_grad = alpha * morph_grad + (1 - alpha) * grad1

    # ⑤ Dual-threshold + hysteresis
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

    # ⑥ Sequential start-end pairing (가장 강한 후보 1:1 매칭)
    segments = []
    i = 0
    state = 'search_start'
    current_s = None
    current_e = None

    while i < T:
        if edge_mask[i]:
            if state == 'search_start' and hybrid_grad[i] > 0:
                s_group = [(i, hybrid_grad[i])]
                j = i + 1
                while j < T and edge_mask[j] and hybrid_grad[j] > 0:
                    s_group.append((j, hybrid_grad[j]))
                    j += 1
                current_s = max(s_group, key=lambda x: x[1])
                i = j
                state = 'search_end'
                continue

            elif state == 'search_end' and hybrid_grad[i] > 0:
                e_group = [(i, hybrid_grad[i])]
                j = i + 1
                while j < T and edge_mask[j] and hybrid_grad[j] > 0:
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

# 기본 구간 단위에서 합쳐서 최종 구간 후보 만들기
def generate_all_merge_candidates_by_gap(segments, gap_threshold=10):
    if not segments:
        return []

    merged = []
    N = len(segments)

    for i in range(N):
        start_i, end_i = segments[i]
        merged.append((start_i, end_i))  # 자기 자신도 후보로 포함

        current_start = start_i
        current_end = end_i

        for j in range(i+1, N):
            next_start, next_end = segments[j]
            gap = next_start - current_end

            if gap <= gap_threshold:
                current_end = next_end
                merged.append((current_start, current_end))
            else:
                break  # 더 이상 연속되지 않음

    return merged

# 최종 점수 구하기
def compute_segment_score(similarity_array, start, end, lambda_weight=0.5):
    # 전체 유사도
    all_scores = similarity_array
    seg_scores = all_scores[start:end+1]

    # 구간 내/외
    mask = np.ones_like(all_scores, dtype=bool)
    mask[start:end+1] = False
    out_scores = all_scores[mask]

    # a, b
    a = seg_scores.mean() if len(seg_scores) > 0 else 1e-6
    b = out_scores.mean() if len(out_scores) > 0 else 1e-6
    score1 = a / b

    # c = 전체 평균
    c = all_scores.mean()
    d = (seg_scores >= c).sum()
    e = (out_scores >= c).sum()
    score2 = (d / e) if e > 0 else 1.0

    # 최종 점수
    final_score = lambda_weight * score1 + (1 - lambda_weight) * score2
    return final_score

# 최종 결랍
def FTF_VTG(
    similarity_array,
    # detect_event_segments_with_gradient 관련
    kernel_size=7,
    sigma=1.0,
    theta_high=0.1,
    theta_low_ratio=0.5,
    min_seg_len=3,
    alpha=0.5,

    # segment 병합 관련
    gap_threshold=10,

    # segment 점수화 관련
    lambda_weight=0.5
):
    # 1. 기본 segment 감지
    segments, _, _ = detect_event_segments_with_gradient(
        similarity_array,
        kernel_size=kernel_size,
        sigma=sigma,
        theta_high=theta_high,
        theta_low_ratio=theta_low_ratio,
        min_seg_len=min_seg_len,
        alpha=alpha
    )

    # 2. 병합된 segment 후보 생성
    merged_segments = generate_all_merge_candidates_by_gap(
        segments,
        gap_threshold=gap_threshold
    )

    # 3. 각 구간에 점수 매기기
    scored = []
    if isinstance(similarity_array, torch.Tensor):
        similarity_array = similarity_array.squeeze().cpu().numpy()
    for (s, e) in merged_segments:
        score = compute_segment_score(similarity_array, s, e, lambda_weight=lambda_weight)
        scored.append((s, e, score))

    # 4. 점수순 정렬
    if scored:
        scored.sort(key=lambda x: x[2], reverse=True)
        best_start, best_end, best_score = scored[0]
        return best_start, best_end
    else:
        return None, None