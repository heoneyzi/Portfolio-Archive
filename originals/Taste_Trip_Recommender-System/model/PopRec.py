from taste_trip.paths import data_path, image_path as local_image_path, output_path as local_output_path
import numpy as np
import pandas as pd

# Load user-item matrix
file_path1 = data_path('final_user_item_matrix_with_imputation.csv')
user_item_matrix = pd.read_csv(file_path1, index_col=0, encoding='cp949')

file_path2 = data_path('df_modified.csv')
df_modified = pd.read_csv(file_path2, index_col=0, encoding='cp949')

# Step 1: Calculate item popularity based on the sum of ratings
item_popularity = user_item_matrix.sum(axis=0)
print("Item Popularity (Sum of Ratings):")
print(item_popularity)

# Step 2: Rank the items by popularity (descending order)
item_popularity_sorted = item_popularity.sort_values(ascending=False)
print("\nRanked Items by Popularity:")
print(item_popularity_sorted)

# Step 3: Recommend top N items based on popularity
def recommend_poprec(top_n=5):
    return item_popularity_sorted.index[:top_n]

# Example: Recommend top 5 popular items
top_items = recommend_poprec(top_n=5)
print("\nTop 5 Popular Items Recommended to All Users:")
print(top_items)

# Step 4: Precision@K and Recall@K calculation functions
# df와 df_modified를 활용하여 성능 평가
def precision_at_k(true_items, predicted_items, k):
    predicted_items_at_k = predicted_items[:k]
    true_positives = len(set(predicted_items_at_k) & set(true_items))
    return true_positives / k

def recall_at_k(true_items, predicted_items, k):
    predicted_items_at_k = predicted_items[:k]
    true_positives = len(set(predicted_items_at_k) & set(true_items))
    return true_positives / len(true_items) if len(true_items) > 0 else 0

# Step 5: Evaluate Precision@K and Recall@K for each user
def evaluate_poprec(original_matrix, modified_matrix, top_n):
    precision_scores = []
    recall_scores = []

    for user_id in original_matrix.index:
        # Step 6: Extract true items (non-zero values) from modified_matrix for each user
        true_items = modified_matrix.loc[user_id][modified_matrix.loc[user_id] > 0].index.tolist()
        # Predicted items based on popularity from original_matrix
        predicted_items = recommend_poprec(top_n)

        precision = precision_at_k(true_items, predicted_items, top_n)
        recall = recall_at_k(true_items, predicted_items, top_n)

        precision_scores.append(precision)
        recall_scores.append(recall)

    avg_precision = np.mean(precision_scores)
    avg_recall = np.mean(recall_scores)

    return avg_precision, avg_recall

# Step 7: Calculate Precision@5 and Recall@5 using df and df_modified
avg_precision, avg_recall = evaluate_poprec(user_item_matrix, df_modified, top_n=5)
print(f"\nAverage Precision@5: {avg_precision:.4f}")
print(f"Average Recall@5: {avg_recall:.4f}")
