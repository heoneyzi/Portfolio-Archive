# Evaluation scope

This note accompanies the [Virtual Cell Challenge 2026 research brief](../README.md). Its factual source is Jiheon Kang's CV, updated September 2026.

## What the reported quantities describe

| Quantity | Meaning in the CV |
|---|---|
| 18,533 genes | Gene scope of the submission-ready single-cell pipeline |
| 400 cells per perturbation | Cell count specified per perturbation |
| 0.5794 PDS | Result on the Jiang24 IFNG/BxPC3 public-proxy benchmark |

The output dimensions and the benchmark result describe different aspects of the project. They should remain separately labeled when this work is summarized in a portfolio, CV, or presentation.

## Evaluation methods reported

The CV reports two evaluation components: leakage-resistant shadow evaluation and a public-proxy benchmark. It also describes frozen feature, perturbation-effect, and raw-count generation stages in the pipeline.

The supplied CV does not specify the shadow split construction, PDS calculation, model configuration, repeated-run variability, or an official competition ranking. This documentation therefore does not supply those details or claim that the proxy result establishes official competition performance.

## Result wording

> Reached 0.5794 PDS on Jiang24 IFNG/BxPC3 in a public-proxy benchmark; this is not an official leaderboard score.

The project is ongoing as of the September 2026 CV. Its implementation and evaluation artifacts are not included in this release, so this repository cannot independently reproduce the reported score.
