from taste_trip.paths import data_path, image_path as local_image_path, output_path as local_output_path
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset, random_split
from sklearn.model_selection import train_test_split
import pandas as pd
import numpy as np

# MPS 확인
device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
print(f"Using device: {device}")

# 데이터 불러오기
file_path = data_path('final_user_item_matrix_with_imputation.csv')
rating_data = pd.read_csv(file_path)

# 각 유저의 총 리뷰 개수 계산 (0이 아닌 리뷰만 카운트)
rating_data['review_count'] = (rating_data.iloc[:, 1:] > 0).sum(axis=1)

# 리뷰 수가 0개인 사람 필터링
rating_data_filtered = rating_data[rating_data['review_count'] > 0].drop(columns='review_count')

# 데이터 재배열
rating_df = rating_data_filtered.melt(id_vars=['nickname'], var_name='store', value_name='rating')

# User/ Item 맵핑
user_mapping = {user: idx for idx, user in enumerate(rating_df['nickname'].unique())}
item_mapping = {item: idx for idx, item in enumerate(rating_df['store'].unique())}

# mapping 적용
rating_df['userId'] = rating_df['nickname'].map(user_mapping)
rating_df['itemId'] = rating_df['store'].map(item_mapping)

# Pytorch 데이터 세트로 변환
class RatingsDataset(Dataset):
    def __init__(self, data):
        self.users = torch.tensor(data['userId'].values, dtype=torch.long)
        self.items = torch.tensor(data['itemId'].values, dtype=torch.long)
        self.ratings = torch.tensor(data['rating'].values, dtype=torch.float32)

    def __len__(self):
        return len(self.ratings)

    def __getitem__(self, idx):
        return self.users[idx], self.items[idx], self.ratings[idx]

# 유저별 리뷰 수 계산
review_counts = rating_df[rating_df['rating'] > 0].groupby('nickname').size()

# 사용자별로 훈련/테스트 데이터 나누기
train_data = pd.DataFrame()
test_data = pd.DataFrame()
total_users = len(review_counts)

# 진행 상태 출력
for i, (user, count) in enumerate(review_counts.items(), start=1):
    user_reviews = rating_df[(rating_df['nickname'] == user) & (rating_df['rating'] > 0)]

    # 훈련 데이터 비율을 80%로 설정하고 반올림
    train_size = int(np.round(0.8 * count))

    # 테스트 데이터 수는 전체 데이터 수에서 훈련 데이터 수를 뺀 값
    test_size = count - train_size

    # 리뷰를 훈련/테스트 데이터로 분할
    train_reviews, test_reviews = train_test_split(user_reviews, train_size=train_size, test_size=test_size)

    # 훈련 데이터와 테스트 데이터를 각각 추가
    train_data = pd.concat([train_data, train_reviews])
    test_data = pd.concat([test_data, test_reviews])

    # 진행 상태 출력
    print(f"Processing user {i}/{total_users}: {user} (Total reviews: {count})")

# Pytorch 데이터셋으로 변환
train_dataset = RatingsDataset(train_data)
test_dataset = RatingsDataset(test_data)

# DataLoader
train_dataloader = DataLoader(train_dataset, batch_size=64, shuffle=True)
test_dataloader = DataLoader(test_dataset, batch_size=64, shuffle=False)

#  Matrix Factorization model (ALS)
class MF(nn.Module):
    def __init__(self, num_users, num_items, embedding_dim=10):
        super(MF, self).__init__()
        self.user_embedding = nn.Embedding(num_users, embedding_dim)
        self.item_embedding = nn.Embedding(num_items, embedding_dim)

    def forward(self, user, item):
        user_embedded = self.user_embedding(user)
        item_embedded = self.item_embedding(item)
        return (user_embedded * item_embedded).sum(1)

# 모델 초기화
num_users = len(user_mapping)
num_items = len(item_mapping)
embedding_dim = 10
model = MF(num_users, num_items, embedding_dim).to(device)

# Loss function & optimizer
loss_fn = nn.MSELoss()
optimizer = optim.Adam(model.parameters(), lr=0.01)

# 훈련
epochs = 10
for epoch in range(epochs):
    model.train()
    total_loss = 0
    for users, items, ratings in train_dataloader:
        users, items, ratings = users.to(device), items.to(device), ratings.to(device)

        # Forward pass
        predictions = model(users, items)
        loss = loss_fn(predictions, ratings)

        # Backward pass
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        total_loss += loss.item()

    print(f"Epoch {epoch+1}/{epochs}, Loss: {total_loss/len(train_dataloader)}")
def recommend_for_user(user_id, model, item_mapping, top_n=5):
    # 사용자 ID를 tensor로 변환
    user_index = user_mapping[user_id]
    user_tensor = torch.tensor([user_index], dtype=torch.long).to(device)

    # 모든 item에 대한 예측 점수 계산
    item_ids = torch.tensor(list(item_mapping.values()), dtype=torch.long).to(device)
    scores = model(user_tensor.repeat(len(item_ids)), item_ids).detach().cpu().numpy()

    # 추천된 항목을 점수에 따라 정렬
    top_indices = np.argsort(scores)[-top_n:][::-1]
    recommended_items = [list(item_mapping.keys())[idx] for idx in top_indices]

    return recommended_items, scores[top_indices]

def evaluate_performance(test_data, model, item_mapping, k=5):
    total_precision = 0
    total_recall = 0
    total_users = len(test_data['nickname'].unique())

    for user_id in test_data['nickname'].unique():
        # 해당 사용자가 실제로 평가한 항목들
        actual_items = test_data[test_data['nickname'] == user_id]['store'].tolist()

        # 사용자에게 추천된 항목
        recommended_items, _ = recommend_for_user(user_id, model, item_mapping, top_n=k)

        # True Positives 계산
        true_positives = len(set(actual_items) & set(recommended_items))

        # Precision과 Recall 계산
        precision = true_positives / k if recommended_items else 0  # 추천된 항목이 없을 경우 0
        recall = true_positives / len(actual_items) if actual_items else 0  # 실제 항목이 없을 경우 0

        total_precision += precision
        total_recall += recall

    # 모든 사용자에 대한 평균 Precision과 Recall 계산
    average_precision = total_precision / total_users
    average_recall = total_recall / total_users

    return average_precision, average_recall

    # 성능 평가
average_precision, average_recall = evaluate_performance(test_data, model, item_mapping, k=5)
print(f'Average Precision@5: {average_precision:.4f}, Average Recall@5: {average_recall:.4f}')
