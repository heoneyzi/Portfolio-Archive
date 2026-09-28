from taste_trip.paths import data_path, image_path as local_image_path, output_path as local_output_path
import torch
import torch.nn as nn
import pandas as pd
import numpy as np
from sklearn.metrics import precision_score, recall_score
import random
import pickle
from scipy.spatial.distance import cosine
from torch.utils.data import Dataset, DataLoader
import torch.optim as optim

# 데이터 로드 및 전처리
file_path = data_path('final_user_item_matrix_with_imputation.csv')
rating_data = pd.read_csv(file_path)

# 데이터 재배열
rating_df = rating_data.melt(id_vars=['nickname'], var_name='store', value_name='rating')
user_mapping = {user: idx for idx, user in enumerate(rating_df['nickname'].unique())}
item_mapping = {item: idx for idx, item in enumerate(rating_df['store'].unique())}
rating_df['userId'] = rating_df['nickname'].map(user_mapping)
rating_df['itemId'] = rating_df['store'].map(item_mapping)

class RatingsDataset(Dataset):
    def __init__(self, data):
        self.users = torch.tensor(data['userId'].values, dtype=torch.long)
        self.items = torch.tensor(data['itemId'].values, dtype=torch.long)
        self.ratings = torch.tensor(data['rating'].values, dtype=torch.float32)  # Ensure 'rating' is float


    def __len__(self):
        return len(self.ratings)

    def __getitem__(self, idx):
        return self.users[idx], self.items[idx], self.ratings[idx]

# MF 모델 정의
class MF(torch.nn.Module):
    def __init__(self, num_users, num_items, embed_size):
        super(MF, self).__init__()
        self.user_factors = torch.nn.Embedding(num_users, embed_size)  # 사용자의 임베딩
        self.item_factors = torch.nn.Embedding(num_items, embed_size)  # 항목의 임베딩

    def forward(self, user, item):
        user_embedding = self.user_factors(user)  # (batch_size, embed_size)
        item_embedding = self.item_factors(item)  # (batch_size, embed_size)
        return (user_embedding * item_embedding).sum(1)  # 내적

# CBF 모델 정의 (코사인 유사도 기반)
def cosine_similarity(vector1, vector2):
    return 1 - cosine(vector1, vector2)

# 추천을 위한 함수
def recommend_for_user(user_id, model, top_n=5):
    if isinstance(user_id, str):
        user_id = user_mapping.get(user_id)

# 유효한 사용자 ID인지 확인
    if user_id is None:
        raise ValueError(f"User ID '{user_id}' not found in user_mapping.")

    user_id = torch.tensor(user_id, dtype=torch.long)
    all_items = torch.arange(len(item_mapping))

    with torch.no_grad():
        predictions = model(user_id, all_items)

    top_values, top_items = torch.topk(predictions, top_n)
    recommended_items = [list(item_mapping.keys())[idx] for idx in top_items.cpu().numpy()]
    recommended_values = top_values.cpu().numpy().tolist()
    return recommended_items, recommended_values

# 사용자 벡터 생성
def get_user_vector(user_idx, mf_model):
    user_vector = mf_model.user_factors.weight[user_idx].detach().numpy()  # 사용자 벡터
    return user_vector

# CBF 스코어 계산
def calculate_cbf_scores(user_vector, item_vectors):
    scores = {}
    user_vector = user_vector.flatten()  # Ensure it's 1D
    for item, vector in item_vectors.items():
        vector = vector.flatten()  # Ensure each item vector is also 1D
        if user_vector.shape[0] == vector.shape[0]:  # Check dimensions
            score = cosine_similarity(user_vector.reshape(1, -1), vector.reshape(1, -1))[0][0]
            scores[item] = score
        else:
            print(f"Dimension mismatch: user_vector ({user_vector.shape}) vs item_vector ({vector.shape})")
    return scores

def hybrid_recommendation_with_training(train_data, test_data, mf_model, store_vectors, mf_weight, cbf_weight, top_n=5):
    recommended_items_dict = {}

    for user_id in train_data['nickname'].unique():
        # 사용자 ID를 정수형으로 변환
        user_idx = user_mapping[user_id]

        # MF 모델을 사용하여 추천 아이템과 점수 가져오기
        recommended_items_mf, mf_scores = recommend_for_user(user_idx, mf_model, top_n=337)

        # 사용자 벡터를 가져옴
        user_vector = get_user_vector(user_idx, mf_model)

        # CBF 모델의 유사도 계산
        cbf_results = calculate_cbf_scores(user_vector, store_vectors)

        # 유사도 기준으로 정렬
        sorted_cbf = {k: v for k, v in sorted(cbf_results.items(), key=lambda item: item[1], reverse=True)}

        # MF 추천과 동일한 수의 CBF 추천 선택
        recommended_items_cbf = list(sorted_cbf.keys())[:len(recommended_items_mf)]
        cbf_scores = [sorted_cbf[item] for item in recommended_items_cbf]

        # 두 모델의 결과를 가중합하여 최종 점수 계산
        df_final = pd.DataFrame({
            'Recommended Items': recommended_items_mf,
            'mf_scores': mf_scores,
            'cbf_scores': cbf_scores
        })

        df_final['final_scores'] = mf_weight * df_final['mf_scores'] + cbf_weight * df_final['cbf_scores']
        df_final_sorted = df_final.sort_values(by='final_scores', ascending=False)

        # 추천 아이템을 사전(dict)에 저장
        recommended_items_dict[user_id] = df_final_sorted.iloc[:top_n]['Recommended Items'].tolist()

    return recommended_items_dict

# 성능 평가 함수
def evaluate_performance(test_data, model, item_mapping, k=5):
    total_precision = 0
    total_recall = 0
    total_users = len(test_data['nickname'].unique())

    for user_id in test_data['nickname'].unique():
        actual_items = test_data[test_data['nickname'] == user_id]['store'].tolist()
        recommended_items, _ = recommend_for_user(user_id, model, top_n=k)

        true_positives = len(set(actual_items) & set(recommended_items))
        precision = true_positives / k if recommended_items else 0  # k로 나누기
        recall = true_positives / len(actual_items) if actual_items else 0

        total_precision += precision
        total_recall += recall

    average_precision = total_precision / total_users
    average_recall = total_recall / total_users

    return average_precision, average_recall

# 모델 학습 (MF 및 CBF)
num_users = len(user_mapping)
num_items = len(item_mapping)
embedding_dim = 10
mf_model = MF(num_users, num_items, embedding_dim)

# 데이터 로드 및 전처리
train_data = pd.read_csv(data_path('final_train_data.csv'))
test_data = pd.read_csv(data_path('final_test_data.csv'))

# 유저 및 아이템 매핑
train_data['userId'] = train_data['nickname'].map(user_mapping)
train_data['itemId'] = train_data['store'].map(item_mapping)

# Create DataLoader for training data
train_dataset = RatingsDataset(train_data)
train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)

# 데이터 로드
with open(data_path('sentence_vectors.pkl'), 'rb') as f:
    sentence_vectors = pickle.load(f)

with open(data_path('store_vectors.pkl'), 'rb') as f:
    store_vectors = pickle.load(f)

with open(data_path('unique_category_vectors.pkl'), 'rb') as f:
    unique_category_vectors = pickle.load(f)

with open(data_path('store_category_vectors.pkl'), 'rb') as f:
    store_category_vectors = pickle.load(f)

# 모델 훈련
train_loader = DataLoader(RatingsDataset(train_data), batch_size=64, shuffle=True)
optimizer = optim.Adam(mf_model.parameters(), lr=0.01)
loss_fn = nn.MSELoss()

for epoch in range(10):
    for users, items, ratings in train_loader:
        optimizer.zero_grad()
        predictions = mf_model(users, items)
        loss = loss_fn(predictions, ratings)
        loss.backward()
        optimizer.step()
    print(f'Epoch {epoch+1}, Loss: {loss.item()}')

# 성능 평가
average_precision, average_recall = evaluate_performance(test_data, mf_model, item_mapping, k=5)
print(f'Average Precision@{5}: {average_precision:.4f}, Average Recall@{5}: {average_recall:.4f}')
