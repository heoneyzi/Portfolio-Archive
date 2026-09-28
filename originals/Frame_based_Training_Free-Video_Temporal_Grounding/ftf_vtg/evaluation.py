"""Explicit dataset adapters; no data loading or tuning at import time.

Historical sample-index endpoint conventions are retained. Scores below are
local experiment metrics, not official benchmark evaluator replacements.
"""
import json
from pathlib import Path
import numpy as np
from .main import FTF_VTG
from .src.utils.eval_metrics import compute_iou


def _load(path):
    with open(path, encoding='utf-8') as handle:
        return json.load(handle)


def _segment_pairs(pairs, count):
    if not isinstance(count, int) or isinstance(count, bool) or count < 1:
        raise ValueError('num_segments must be a positive integer.')
    if not isinstance(pairs, list) or not pairs:
        raise ValueError('Ground truth must contain at least one segment pair.')
    for pair in pairs:
        if (not isinstance(pair, (list, tuple)) or len(pair) != 2
            or not all(isinstance(value, int) and not isinstance(value, bool) for value in pair)
            or not 0 <= pair[0] <= pair[1] < count):
            raise ValueError('Ground-truth segment pairs must satisfy 0 <= start <= end < num_segments.')
    return [tuple(pair) for pair in pairs]


def evaluate(task, json_dir, *, ground_truth=None, parameters=None):
    files = sorted(Path(json_dir).glob('*.json'))
    if not files:
        raise ValueError(f'No JSON examples found in {json_dir}')
    parameters = parameters or {}
    gt_index = {}
    if task == 'vtg_didemo':
        if ground_truth is None:
            raise ValueError('vtg_didemo requires --ground-truth JSON.')
        for row in _load(ground_truth):
            gt_index.setdefault((row['video'], row['description']), []).append(row)
    results = []
    no_predictions = 0
    for path in files:
        data = _load(path)
        try:
            if task == 'vtg_vidstg':
                begin, end = data['used_segment']['begin_fid'], data['used_segment']['end_fid']
                curve = data['text_queries']['description']['similarities'][begin:end + 1]
                targets = [(data['ground']['begin_fid'] - begin, data['ground']['end_fid'] - begin)]
            else:
                curve = data['similarities']
            prediction = FTF_VTG(curve, **parameters)
            missing = prediction[0] is None
            no_predictions += int(missing)
            if task == 'vmr_didemo':
                fps, total, count = data['fps'], data['total_frames'], data['num_segments']
                if fps <= 0 or total <= 0 or count < 1:
                    raise ValueError('fps, total_frames and num_segments must be positive.')
                targets = _segment_pairs(data['gt_times'], count)
                if missing:
                    results.append((0., 0.))
                    continue
                candidates = [(start, start + length - 1) for length in range(1, count + 1)
                              for start in range(count - length + 1)]
                candidates.sort(key=lambda pair: compute_iou(*prediction, int(pair[0] * 5 * fps),
                    int(min((pair[1] + 1) * 5 * fps, total))), reverse=True)
                results.append((float(candidates[0] in targets),
                                float(any(pair in targets for pair in candidates[:5]))))
                continue
            if task == 'vtg_didemo':
                fps, total = data['fps'], data['total_frames']
                if fps <= 0 or total <= 0:
                    raise ValueError('fps and total_frames must be positive.')
                rows = gt_index.get((data['video'], data['query']), [])
                if not rows:
                    raise ValueError('No ground truth matching both video and query.')
                targets = []
                for row in rows:
                    for start, end in _segment_pairs(row['times'], row['num_segments']):
                        # Historical DiDeMo convention: final bin ends at actual video duration.
                        end_frame = int((end + 1) * 5 * fps) if end < row['num_segments'] - 1 else int(total)
                        targets.append((int(start * 5 * fps), end_frame))
            if task not in {'vtg_didemo', 'vtg_vidstg'}:
                raise ValueError(f'Unknown task: {task}')
            if not targets:
                raise ValueError('Example has no ground-truth segments.')
            best_iou = 0. if missing else max(compute_iou(*prediction, *target) for target in targets)
            results.append((best_iou, float(best_iou >= .5)))
        except (KeyError, TypeError, ValueError, IndexError) as exc:
            raise ValueError(f'{path.name}: {exc}') from exc
    first, second = np.mean(results, axis=0)
    metric_names = ('recall_at_1', 'recall_at_5') if task == 'vmr_didemo' else ('mean_iou', 'recall_at_iou_0_5')
    return {'task': task, 'examples': len(results), 'no_prediction': no_predictions,
            metric_names[0]: float(first), metric_names[1]: float(second), 'parameters': parameters}
