"""CLI for a similarity curve, a synthetic example, or dataset evaluation."""
import argparse
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--demo', action='store_true', help='Run one synthetic curve; no dataset/model download.')
    mode.add_argument('--scores', type=Path, help='JSON numeric array or object with a similarities array.')
    mode.add_argument('--task', choices=['vmr_didemo', 'vtg_didemo', 'vtg_vidstg'])
    parser.add_argument('--data-dir', type=Path)
    parser.add_argument('--ground-truth', type=Path)
    parser.add_argument('--theta-high', type=float, default=.1)
    parser.add_argument('--lambda-weight', type=float, default=.5)
    parser.add_argument('--output', type=Path, help='Optional results JSON file.')
    args = parser.parse_args()
    params = {'theta_high': args.theta_high, 'lambda_weight': args.lambda_weight}
    try:
        if args.task:
            from .evaluation import evaluate
            if args.data_dir is None:
                parser.error('--task requires --data-dir')
            result = evaluate(args.task, args.data_dir, ground_truth=args.ground_truth, parameters=params)
        else:
            from .main import FTF_VTG
            if args.demo:
                scores = [.1] * 12 + [.9] * 18 + [.1] * 12
            else:
                scores = json.loads(args.scores.read_text())
                if isinstance(scores, dict):
                    scores = scores['similarities']
            start, end = FTF_VTG(scores, **params)
            result = {'start_sample': start, 'end_sample': end,
                      'synthetic_example': args.demo, 'parameters': params}
    except (ValueError, KeyError, OSError) as exc:
        parser.error(str(exc))
    rendered = json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False)
    if args.output:
        args.output.write_text(rendered + '\n', encoding='utf-8')
    print(rendered)


if __name__ == '__main__':
    main()
