# Evaluation scope

This note accompanies the [PhenoFocus research brief](../README.md). Its factual source is Jiheon Kang's CV, updated September 2026.

## Concept and evaluated scope

The CV distinguishes a broader phenotype-guided drug-discovery concept from the structure-first MVP that was developed. The reported quantitative results concern a 31-compound HDAC screen.

| Reported quantity | Scope |
|---|---|
| 0.97 AUROC | The 31-compound HDAC screen |
| 6.2× top-5 enrichment | The same screen's top-five selection |
| Tanimoto similarity as low as 0.10 | Hits reported within the MVP evaluation |

The Tanimoto value is a similarity result, not a success rate. The CV does not specify the molecular fingerprint, exact similarity comparison, screen composition, or statistical uncertainty. This release therefore preserves the original description rather than adding methodological precision that the source does not provide.

## Interpretation boundaries

The 31-compound scope should appear alongside the quantitative results. The available CV does not establish performance across a larger compound collection, other targets, or a complete phenotype-guided discovery system. It also does not provide enough experimental detail to infer what form of biological validation, if any, was used to define the reported hits.

Advancement to the competition main round is a separate project milestone. The CV does not name the competition or provide a final ranking, so this release does not supply either.

## Result wording

> Developed a structure-first MVP within a broader phenotype-guided discovery concept. On a 31-compound HDAC screen, reported 0.97 AUROC, 6.2× top-5 enrichment, and hits down to 0.10 Tanimoto similarity.

The project is ongoing as of the September 2026 CV. Its implementation and evaluation artifacts are not included in this release, so this repository cannot independently reproduce those measurements.
