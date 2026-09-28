def generate_all_merge_candidates_by_gap(segments, gap_threshold=10):
    if not segments:
        return []

    merged = []
    N = len(segments)
    for i in range(N):
        start_i, end_i = segments[i]
        merged.append((start_i, end_i))
        current_start = start_i
        current_end = end_i
        for j in range(i+1, N):
            next_start, next_end = segments[j]
            if next_start - current_end <= gap_threshold:
                current_end = next_end
                merged.append((current_start, current_end))
            else:
                break
    return merged