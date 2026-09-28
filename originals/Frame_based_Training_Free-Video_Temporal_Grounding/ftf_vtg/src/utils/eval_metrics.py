def compute_iou(pred_start, pred_end, gt_start, gt_end):
    inter_start = max(pred_start, gt_start)
    inter_end = min(pred_end, gt_end)
    inter = max(0, inter_end - inter_start)
    union = max(pred_end, gt_end) - min(pred_start, gt_start)
    return inter / union if union > 0 else 0

