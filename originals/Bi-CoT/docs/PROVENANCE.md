# Provenance and release preparation

The six notebooks originate in Jiheon Kang's `AI_Study` local research archive, whose Git remote identifies `https://github.com/heoneyzi/AI_Study.git`. They were untracked experiment files in the recovered working copy, so the Git commit history does not prove their individual authorship or exact dates. They are released as recovered author-provided project material associated with the coauthored Bi-CoT research.

Research description and historical table values were summarized from the supplied `Plug_and_Play_Bi-CoT.docx` manuscript. Publication listing and the abbreviated title were cross-checked against the supplied CV. Personal contact details and unrelated documents were not copied into the repository. The manuscript itself was not redistributed. Its method diagram is included as `docs/pipeline.png` with attribution; unrelated media are excluded.

## Changes to release copies

- Removed all code-cell outputs and execution counts: 35 output blocks in total.
- Removed notebook/cell host metadata and attachments; retained only a generic Python kernel declaration.
- Replaced five embedded API credential literals with `OPENAI_API_KEY` environment lookups.
- Replaced 65 occurrences of personal or Colab absolute workspace roots with `../data/workspace`.
- Converted the historical Colab/bootstrap cells and one standalone recursive-cleanup cell in `MDR_own.ipynb` into non-executing markdown.
- Added notebook introductions, repository documentation, requirements, ignore rules, citation metadata, and synthetic evaluation examples.
- Extracted the normalization, EM, F1, and best-reference functions unchanged from `MDR2DATA.ipynb`, original zero-based cell 5, into `tools/notebook_metrics.py`. The command-line input validation and full-gold-set reporting in `tools/evaluate_predictions.py` are release packaging additions.

Original local source files were not modified. Original Git history, datasets, prediction dumps, model weights, third-party repository copies, and private execution logs are excluded.

## Attribution and rights

Research authors are credited in the README and citation metadata. The English spelling of the coauthor follows the local manuscript. MDR, HotpotQA, UnifiedQA, and API models remain the work of their respective authors and providers; follow the linked upstream documentation and terms. No blanket software license is inferred from possession of the source archive.
