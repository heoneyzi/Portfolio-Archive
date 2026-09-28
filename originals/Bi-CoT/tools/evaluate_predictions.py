#!/usr/bin/env python3
"""Answer-only evaluator wrapping scoring functions from the Bi-CoT notebook.

This CLI and its input validation are release packaging additions. Scores use
the original notebook metric, not HotpotQA supporting-fact or joint evaluation.
"""
import argparse
import json
from pathlib import Path

from notebook_metrics import max_over_golds


def load_gold(path):
    text = path.read_text(encoding="utf-8")
    try:
        rows = json.loads(text)
    except json.JSONDecodeError:
        rows = [json.loads(line) for line in text.splitlines() if line.strip()]
    if not isinstance(rows, list) or not rows:
        raise ValueError("Gold input must be a nonempty JSON list or JSONL file.")
    gold = {}
    for row in rows:
        if not isinstance(row, dict) or not isinstance(row.get("_id"), str) or not row["_id"]:
            raise ValueError("Every gold example needs a nonempty string _id.")
        answers = row.get("answer")
        if isinstance(answers, str):
            answers = [answers]
        if not isinstance(answers, list) or not answers or not all(isinstance(a, str) and a.strip() for a in answers):
            raise ValueError("Every gold answer must be a nonempty string or list of strings.")
        if row["_id"] in gold:
            raise ValueError("Gold input contains a duplicate _id.")
        gold[row["_id"]] = answers
    return gold


def evaluate(gold, predictions):
    em_sum = f1_sum = 0.0
    missing = 0
    for question_id, answers in gold.items():
        if question_id not in predictions:
            missing += 1
            continue
        em, f1 = max_over_golds(predictions[question_id], answers)
        em_sum += em
        f1_sum += f1
    count = len(gold)
    return {
        "metric": "archived_answer_em_f1",
        "gold_count": count,
        "predicted_gold_count": count - missing,
        "missing_prediction_count": missing,
        "extra_prediction_count": len(set(predictions) - set(gold)),
        "answer_em_percent": 100 * em_sum / count,
        "answer_f1_percent": 100 * f1_sum / count,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gold", required=True, type=Path)
    parser.add_argument("--predictions", required=True, type=Path)
    args = parser.parse_args()
    try:
        gold = load_gold(args.gold)
        predictions = json.loads(args.predictions.read_text(encoding="utf-8"))
        if isinstance(predictions, dict) and isinstance(predictions.get("answer"), dict):
            predictions = predictions["answer"]
        if not isinstance(predictions, dict) or not all(isinstance(k, str) and isinstance(v, str) for k, v in predictions.items()):
            raise ValueError("Predictions must map question IDs to answer strings.")
        result = evaluate(gold, predictions)
    except (OSError, ValueError, TypeError) as exc:
        parser.error(str(exc))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
