"""Check local file prerequisites without loading data or starting training."""

import argparse
from .paths import data_path

VECTORS = (
    "sentence_vectors.pkl", "store_vectors.pkl",
    "unique_category_vectors.pkl", "store_category_vectors.pkl",
)
WORKFLOWS = {
    "demo": ("final_user_item_matrix_with_imputation.csv", "Item_data.xlsx", "Place_URL_with address.xlsx"),
    "mf": ("final_user_item_matrix_with_imputation.csv",),
    "poprec": ("final_user_item_matrix_with_imputation.csv", "df_modified.csv"),
    "content": VECTORS + ("Top5_tags.xlsx", "user_item_matrix_with_imputation.csv"),
    "hybrid": VECTORS + ("Item_data.xlsx", "final_train_data.csv", "final_test_data.csv"),
    "hybrid3": VECTORS + ("final_user_item_matrix_with_imputation.csv", "final_train_data.csv", "final_test_data.csv"),
    "imputation": ("Final_merged_similarity_matrix.xlsx", "final_user_item_matrix.csv"),
}


def missing_files(workflow):
    return [data_path(name) for name in WORKFLOWS[workflow] if not data_path(name).is_file()]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workflow", choices=WORKFLOWS, required=True)
    args = parser.parse_args()
    missing = missing_files(args.workflow)
    if missing:
        print("Missing local inputs (set TASTE_TRIP_DATA_DIR or populate data/):")
        for path in missing:
            print(f"  {path}")
        return 1
    print("Required files exist. This check does not validate their schemas or model quality.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
