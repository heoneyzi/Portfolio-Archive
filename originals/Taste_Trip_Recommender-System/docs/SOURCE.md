# Source and restoration notes

This publication candidate restores existing project code to the repository's default `main` branch. It does not present the implementation as newly written or as a new research result.

- Repository: https://github.com/heoneyzi/Taste_Trip_Recommender-System
- Default-branch base: `9365bf3f0d9ba60ac6ef3feb57ff52a3e18a2d2e` (`main`).
- Source snapshot: `27329badc0bcd4270820b553cf8f46258ebdabc4` (`jiheon`).
- Earlier source branch: `initial_repo`, commit `9e726e418337e0cc169ade034ce4c9233cc14e60`.

Restored files: `demo/demo.py`, all six existing Python files under `model/`, `preprocess/imputation.py`, `preprocess/plotting.py`, and `preprocess/preprocess.md`. The public branch history remains the authority for contributor attribution; ownership of the repository does not imply sole authorship of every file.

The 135 files in the source branch's `data/` directory, demo binary assets, caches, and credentials were not copied into this candidate. No remote branch has been deleted or rewritten.

Restoration changes are limited to documentation, dependency/configuration helpers, local path portability, a bounded demo ranking size, basic demo input checks, a supported MPS availability check, whitespace cleanup, and clear labeling of the demo's untrained model. The original recommendation algorithms and exploratory evaluation logic are retained. No training run or new benchmark result is claimed.

The source snapshot did not provide a license file. This restoration does not grant a new license or override any contributor or dataset rights.
