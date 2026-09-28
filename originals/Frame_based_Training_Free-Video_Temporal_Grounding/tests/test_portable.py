import importlib
import json
import numpy as np
import pytest
from ftf_vtg import FTF_VTG
from ftf_vtg.evaluation import evaluate
from ftf_vtg.segment_scorer import compute_segment_score


def test_synthetic_event_and_supported_inputs():
    curve = [.1] * 12 + [.9] * 18 + [.1] * 12
    start, end = FTF_VTG(curve)
    assert start is not None and end is not None
    assert 8 <= start <= 15 and 26 <= end <= 33
    assert FTF_VTG(np.array(curve)) == (start, end)


def test_short_flat_and_invalid_curves():
    assert FTF_VTG([.1]) == (None, None)
    assert FTF_VTG([.1] * 20) == (None, None)
    with pytest.raises(ValueError, match='finite'):
        FTF_VTG([1, float('nan'), 2])
    with pytest.raises(ValueError, match='odd'):
        FTF_VTG([.1] * 20, kernel_size=2)
    with pytest.raises(ValueError, match='1-D'):
        FTF_VTG([[1, 2, 3], [3, 2, 1]])


def test_zero_background_score_is_finite():
    assert np.isfinite(compute_segment_score([0., 1., 1., 0.], 1, 2))


def test_imports_do_not_read_colab_data():
    for name in ('vmr_DiDeMo', 'vtg_DiDeMo', 'vtg_VidSTG'):
        importlib.import_module('ftf_vtg.experiment.' + name)


def test_no_prediction_counts_as_miss(tmp_path):
    record = {'similarities': [.1] * 30, 'fps': 1, 'total_frames': 30,
              'num_segments': 6, 'gt_times': [[1, 2]]}
    (tmp_path / 'sample.json').write_text(json.dumps(record))
    result = evaluate('vmr_didemo', tmp_path)
    assert result['examples'] == 1 and result['no_prediction'] == 1
    assert result['recall_at_1'] == result['recall_at_5'] == 0


def test_ground_truth_matches_video_and_query(tmp_path):
    records = tmp_path / 'records'; records.mkdir()
    record = {'similarities': [.1] * 30, 'fps': 1, 'total_frames': 30,
              'video': 'video-a', 'query': 'same words'}
    (records / 'sample.json').write_text(json.dumps(record))
    gt = tmp_path / 'ground_truth.json'
    gt.write_text(json.dumps([{'video': 'video-b', 'description': 'same words',
                              'times': [[1, 2]], 'num_segments': 6}]))
    with pytest.raises(ValueError, match='both video and query'):
        evaluate('vtg_didemo', records, ground_truth=gt)

@pytest.mark.parametrize('parameter', ['sigma', 'theta_high', 'min_seg_len', 'gap_threshold'])
def test_nonfinite_parameters_rejected(parameter):
    with pytest.raises(ValueError, match='finite'):
        FTF_VTG([.1] * 20, **{parameter: float('nan')})


def test_invalid_ground_truth_rejected(tmp_path):
    record = {'similarities': [.1] * 30, 'fps': 1, 'total_frames': 30,
              'num_segments': 6, 'gt_times': [[999, -2]]}
    (tmp_path / 'broken.json').write_text(json.dumps(record))
    with pytest.raises(ValueError, match='broken.json: Ground-truth'):
        evaluate('vmr_didemo', tmp_path)


def test_last_didemo_bin_reaches_video_end(tmp_path, monkeypatch):
    records = tmp_path / 'records'; records.mkdir()
    record = {'similarities': [.1] * 27, 'fps': 1, 'total_frames': 27,
              'video': 'a', 'query': 'event'}
    (records / 'sample.json').write_text(json.dumps(record))
    gt = tmp_path / 'gt.json'
    gt.write_text(json.dumps([{'video': 'a', 'description': 'event',
                              'times': [[4, 4]], 'num_segments': 5}]))
    monkeypatch.setattr('ftf_vtg.evaluation.FTF_VTG', lambda *args, **kwargs: (20, 27))
    assert evaluate('vtg_didemo', records, ground_truth=gt)['mean_iou'] == 1.
