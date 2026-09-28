from taste_trip.paths import data_path, image_path as local_image_path, output_path as local_output_path
import random
import pickle
import pandas as pd
import numpy as np
from scipy.spatial.distance import cosine
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset

# 코사인 유사도 계산 함수
def cosine_similarity(vector1, vector2):
    return 1 - cosine(vector1, vector2)

# 데이터 로드
with open(data_path('sentence_vectors.pkl'), 'rb') as f:
    sentence_vectors = pickle.load(f)

with open(data_path('store_vectors.pkl'), 'rb') as f:
    store_vectors = pickle.load(f)

with open(data_path('unique_category_vectors.pkl'), 'rb') as f:
    unique_category_vectors = pickle.load(f)

with open(data_path('store_category_vectors.pkl'), 'rb') as f:
    store_category_vectors = pickle.load(f)

# 가게 데이터 로드
file_path = data_path('Item_data.xlsx')
df = pd.read_excel(file_path, engine='openpyxl')

# 유저 평가 태그 및 카테고리 벡터 생성
def create_user_vectors(user_store, sentence_vectors_key, unique_category_vectors_key):
    User_vector = np.zeros(shape=(100,))
    User_category = np.zeros(shape=(100,))

    for i in range(len(user_store)):
        User_sentences = [sentence.strip() for sentence in user_store[i][1].split(',')]
        User_i_vector = np.zeros(shape=(100,))

        for User_sentence in User_sentences:
            if User_sentence in sentence_vectors_key:
                User_i_vector += sentence_vectors[User_sentence] * (user_store[i][3] - 2.5)

        User_vector += User_i_vector

        if user_store[i][2] in unique_category_vectors_key:
            User_category += unique_category_vectors[user_store[i][2]] * (user_store[i][3] - 2.5)

    return User_vector, User_category

# CBF 필터링 후 MF 훈련
def train_mf(rating_df, num_users, num_items, embedding_dim=10, epochs=10, learning_rate=0.01):
    class RatingsDataset(Dataset):
        def __init__(self, data):
            self.users = torch.tensor(data['userId'].values, dtype=torch.long)
            self.items = torch.tensor(data['itemId'].values, dtype=torch.long)
            self.ratings = torch.tensor(data['rating'].values, dtype=torch.float32)

        def __len__(self):
            return len(self.ratings)

        def __getitem__(self, idx):
            return self.users[idx], self.items[idx], self.ratings[idx]

    class MF(nn.Module):
        def __init__(self, num_users, num_items, embedding_dim):
            super(MF, self).__init__()
            self.user_embedding = nn.Embedding(num_users, embedding_dim)
            self.item_embedding = nn.Embedding(num_items, embedding_dim)

        def forward(self, user, item):
            user_embedded = self.user_embedding(user)
            item_embedded = self.item_embedding(item)
            return (user_embedded * item_embedded).sum(1)

    dataset = RatingsDataset(rating_df)
    dataloader = DataLoader(dataset, batch_size=64, shuffle=True)

    model = MF(num_users, num_items, embedding_dim)
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)
    criterion = nn.MSELoss()

    # 손실 값을 기록할 리스트
    loss_history = []

    for epoch in range(epochs):
        epoch_loss = 0  # 현재 epoch의 총 손실
        for users, items, ratings in dataloader:
            optimizer.zero_grad()
            outputs = model(users, items)
            loss = criterion(outputs, ratings)
            loss.backward()
            optimizer.step()
            epoch_loss += loss.item()  # 현재 배치의 손실을 더함

        # epoch의 평균 손실 계산 및 출력
        average_loss = epoch_loss / len(dataloader)
        loss_history.append(average_loss)
        print(f'Epoch {epoch + 1}/{epochs}, Loss: {average_loss:.4f}')

    return model, loss_history

# 추천 생성 함수
def recommend_for_user(user_id, model, item_mapping, top_n=5):
    user_id = torch.tensor(user_mapping[user_id])
    all_items = torch.arange(num_items)

    with torch.no_grad():
        predictions = model(user_id, all_items)

    top_values, top_items = torch.topk(predictions, top_n)
    recommended_items = [list(item_mapping.keys())[idx] for idx in top_items.cpu().numpy()]
    return recommended_items, top_values.cpu().numpy().tolist()


# 성능 평가 함수
def evaluate_performance(test_data, model, item_mapping, k=5):
    total_precision = 0
    total_recall = 0
    total_users = len(test_data['nickname'].unique())

    for user_id in test_data['nickname'].unique():
        actual_items = test_data[test_data['nickname'] == user_id]['store'].tolist()
        recommended_items, _ = recommend_for_user(user_id, model, item_mapping, top_n=k)

        true_positives = len(set(actual_items) & set(recommended_items))
        precision = true_positives / k if recommended_items else 0  # k로 나누기
        recall = true_positives / len(actual_items) if actual_items else 0

        total_precision += precision
        total_recall += recall

    average_precision = total_precision / total_users
    average_recall = total_recall / total_users

    return average_precision, average_recall

# 데이터 로드 및 전처리
train_data = pd.read_csv(data_path('final_train_data.csv'))
test_data = pd.read_csv(data_path('final_test_data.csv'))

# 유저 및 아이템 매핑
user_mapping = {user: idx for idx, user in enumerate(train_data['nickname'].unique())}
item_mapping = {item: idx for idx, item in enumerate(train_data['store'].unique())}

train_data['userId'] = train_data['nickname'].map(user_mapping)
train_data['itemId'] = train_data['store'].map(item_mapping)

# 모델 훈련
num_users = len(user_mapping)
num_items = len(item_mapping)
model, loss_history = train_mf(train_data, num_users, num_items)

# 성능 평가
average_precision, average_recall = evaluate_performance(test_data, model, item_mapping, k=5)
print(f'Average Precision@{5}: {average_precision:.4f}, Average Recall@{5}: {average_recall:.4f}')
