# Taste Trip

**Local food and café recommendations · Research project archive**

Taste Trip explores how venue descriptions, user ratings, and item popularity can support a restaurant-and-café selection flow. This repository contains the project's existing content-based, matrix-factorization, popularity, and hybrid experiments, together with a Korean Streamlit interface prototype.

한국어: 음식점과 카페를 함께 고르는 추천 시스템 프로젝트입니다. 기존 `jiheon` 브랜치의 실험 코드를 기본 브랜치에서 확인할 수 있도록 정리했습니다. 원본 데이터와 학습된 모델은 포함하지 않으며, 새로운 추천 성능이나 검증 결과를 주장하지 않습니다.

## Project status and provenance

The code is restored from the existing public [`jiheon` branch](https://github.com/heoneyzi/Taste_Trip_Recommender-System/tree/27329badc0bcd4270820b553cf8f46258ebdabc4), with portable local paths and setup documentation. The original `initial_repo` and `jiheon` branches remain the source history. See [SOURCE.md](docs/SOURCE.md) for exact commits and restoration changes.

This is an exploratory project, not a deployed recommendation service. In particular, the historical Streamlit demo initializes an **untrained matrix-factorization model**. Its example rankings illustrate the interface; the ratings collected by the interface do not train that model. The demo labels this limitation directly. No checkpoint, reproduced benchmark, or recommendation-quality claim accompanies this release.

## What's included

| Path | Purpose |
|---|---|
| `demo/demo.py` | Korean venue-rating and restaurant/café selection interface |
| `model/Contents_Based_flitering.py` | Content-based ranking from tag/category vectors; original filename retained |
| `model/Matrix_Factorization.py` | PyTorch user/item embeddings with an exploratory per-user train/test split |
| `model/PopRec.py` | Popularity ranking and precision/recall calculations |
| `model/model1.py`, `model/model2.py`, `model/model3.py` | Historical hybrid experiments combining content and collaborative signals |
| `preprocess/imputation.py` | Similarity-based rating imputation |
| `preprocess/plotting.py` | Historical static comparison plot; its embedded numbers have not been reproduced |
| `taste_trip/` | Lightweight path configuration and prerequisite checks |

The source branch's 135 data files, binary demo assets, model state, and caches are not bundled here.

## Environment

Use Python 3.10 or newer in a dedicated environment. Run commands from the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

On Windows, activate with `.venv\Scripts\activate`. The manifest provides dependency compatibility ranges; it is not a lockfile from a reproduced experiment. PyTorch device support depends on the installed build. The MF script selects available Apple MPS or CPU. No GPU or third-party packages are required for the prerequisite check.

## Local input configuration

Inputs default to `data/` at the repository root. Keep local data out of Git. To use existing directories:

```bash
export TASTE_TRIP_DATA_DIR="/absolute/path/to/taste-trip-inputs"
export TASTE_TRIP_IMAGE_DIR="/absolute/path/to/taste-trip-images"
export TASTE_TRIP_OUTPUT_DIR="/absolute/path/to/taste-trip-outputs"
```

Images default to `images/` beneath the selected data directory; generated files default to repository `outputs/`. Existing scripts do not automatically connect every output to the next stage: use the exact required filenames below when preparing the next experiment's inputs.

### Required inputs by workflow

| Workflow | Required files under the data directory |
|---|---|
| `demo` | `final_user_item_matrix_with_imputation.csv`, `Item_data.xlsx`, `Place_URL_with address.xlsx` |
| `mf` | `final_user_item_matrix_with_imputation.csv` |
| `poprec` | `final_user_item_matrix_with_imputation.csv`, `df_modified.csv` |
| `content` | Four vector dictionaries listed below, `Top5_tags.xlsx`, `user_item_matrix_with_imputation.csv` |
| `hybrid` (`model1`, `model2`) | Four vector dictionaries, `Item_data.xlsx`, `final_train_data.csv`, `final_test_data.csv` |
| `hybrid3` | Four vector dictionaries, `final_user_item_matrix_with_imputation.csv`, `final_train_data.csv`, `final_test_data.csv` |
| `imputation` | `Final_merged_similarity_matrix.xlsx`, `final_user_item_matrix.csv` |

Vector files: `sentence_vectors.pkl`, `store_vectors.pkl`, `unique_category_vectors.pkl`, and `store_category_vectors.pkl`. These are precomputed dictionaries, including the original 100-dimensional tag/category vectors. Obtain these artifacts from a trusted project source; this release does not train or provide replacement vectors.

### Data schemas and original assumptions

- **Wide ratings CSVs:** a `nickname` column followed by venue-name columns containing numeric ratings; zero represents an unrated entry in the historical evaluation code. The demo and interactive content experiment require a row named `DEMO_USER`. Keep venue identifiers consistent. `PopRec.py` reads its two CSVs with CP949 encoding and uses the first column as the user index; the other CSV readers use pandas' default UTF-8.
- **`Item_data.xlsx`:** the original first six columns are used positionally. Column 1 contains venue names (`Name`); columns 2 and 3 provide tags (`Top5 Tags`) and categories (`Category`); column 4 distinguishes `식사` and `디저트`; columns 5 and 6 are named `5열` and `6열` and provide displayed location and the restaurant/café location-matching value. Tags in the demo are separated by comma + space.
- **`Top5_tags.xlsx`:** its first three columns are venue name, comma-separated top tags, and category. The historical content script assumes the original venue/vector inventory, including fixed tag/category loops, and is not a generic arbitrary-size dataset loader.
- **`Place_URL_with address.xlsx`:** the first four columns are venue name, URL, address, and category.
- **Train/test CSVs:** `nickname`, `store`, and numeric `rating`; user/item identifiers must match the training mappings. Scripts generate `userId` and `itemId` from these names. Handle unseen test users/items before interpreting results.
- **Imputation inputs:** a square Excel venue-similarity matrix with venue labels in the first column and matching column headers, plus a user/venue CSV with the user index in the first column. Review the retained positional assumptions before using a different export.
- **Images:** the six initial demo venues need `<venue>.png`; result cards look for `<venue>.jpeg`. Missing images are reported by the UI. Initial venues are 서울객점, 강변서재, 스몰톡, 후무, 선유수제맥주, and 브링미커피 브루어스; these names must exist in the ratings matrix for the historical flow.

This repository does not supply or grant rights to review data, venue images, or third-party datasets. Arrange the original permitted inputs locally; no code downloads them automatically.

## Check prerequisites and run

The file check uses only Python's standard library. It checks existence, not schema correctness, and exits with status 1 when inputs are missing:

```bash
python -m taste_trip.check_data --workflow demo
python -m streamlit run demo/demo.py
```

For the historical experiments, check the relevant input set first:

```bash
python -m taste_trip.check_data --workflow mf
python -m model.Matrix_Factorization

python -m taste_trip.check_data --workflow poprec
python -m model.PopRec

python -m taste_trip.check_data --workflow content
python -m model.Contents_Based_flitering

python -m taste_trip.check_data --workflow hybrid
python -m model.model1
# Alternative retained experiment: python -m model.model2

python -m taste_trip.check_data --workflow hybrid3
python -m model.model3

python -m taste_trip.check_data --workflow imputation
python -m preprocess.imputation
```

These commands execute the original experiments; some start training or request interactive ratings. They are not lightweight import checks. Source modules retain top-level experiment execution, so avoid importing them as a reusable library.

## Evaluation limitations

Historical implementations include fixed inventory sizes, unseeded experiment randomness, data-split assumptions, and limited handling of sparse users or unseen items. Matrix-factorization splits need enough ratings per user for nonempty training and test sets. Imputation and hybrid experiments need a leakage review before results can support performance claims. The demo does not save or load a trained checkpoint. The plotting script contains historical constants rather than a generated experiment report.

For this restoration, Python syntax, source provenance, local path helpers, prerequisite-check behavior, and credential-pattern checks were verified. Full dependency installation, data loading, training, evaluation, and the interactive Streamlit flow have **not** been reproduced.

## Attribution

Maintained in [heoneyzi's GitHub](https://github.com/heoneyzi); [Jiheon Kang's portfolio](https://heoneyzi.github.io/). Consult the original branch history for individual contributions. No license file was present in the source snapshot, and this restoration does not assign a new license to collaborators' work.
