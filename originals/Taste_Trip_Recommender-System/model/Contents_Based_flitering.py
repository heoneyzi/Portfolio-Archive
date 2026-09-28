from taste_trip.paths import data_path, image_path as local_image_path, output_path as local_output_path
import random
import pickle
import pandas as pd
import numpy as np
from scipy.spatial.distance import cosine

def cosine_similarity(vector1, vector2):
    # 코사인 거리를 계산한 후, 유사도를 계산 (1 - 코사인 거리)
    return 1 - cosine(vector1, vector2)

#word2vec한 값들을 돌리지 않고 저장하기 위해서 .pkl 파일로 아래에 저장함. 4가지 파일을 따로 딕셔너리 형태로 저장.

#평가 태그 벡터화
with open(data_path('sentence_vectors.pkl'), 'rb') as f:
    sentence_vectors = pickle.load(f)
#key (평가태그의 종류)
sentence_vectors_key = list(sentence_vectors.keys())

#가게마다 평가 태그의 벡터화
with open(data_path('store_vectors.pkl'), 'rb') as f:
    store_vectors = pickle.load(f)
#key (가게 이름)
store_vectors_key = list(store_vectors.keys())

#카테고리마다 벡터화
with open(data_path('unique_category_vectors.pkl'), 'rb') as f:
    unique_category_vectors = pickle.load(f)
#key (카테고리의 종류)
unique_category_vectors_key = list(unique_category_vectors.keys())

#가게마다 카테고리 벡터화
with open(data_path('store_category_vectors.pkl'), 'rb') as f:
    store_category_vectors = pickle.load(f)
#key (가게 이름)
store_category_vectors_key = list(store_category_vectors.keys())



#가게마다 제일 많은 5개의 평가 태그와 카테고리가 있는 엑셀 파일
file_path = data_path('Top5_tags.xlsx')
df = pd.read_excel(file_path, engine='openpyxl')

#가게 이름
first_row = df.iloc[:, 0]

#가게마다 평가태그 top5
second_row = df.iloc[:, 1]

#가게마다 카테고리
third_row = df.iloc[:, 2]

#가게 337개를 랜덤으로 6개 받는다고 가정. (개수나 방법은 추후 변경 가능)
demo_count = 6

numbers = random.sample(range(1, 338), demo_count)
numbers.sort()

#데모 사용자가 평가할 6개의 가게에 대한 리스트를 생성하고 제일 뒤에 평가 점수를 추가함.
User_store = []
for idx in range(demo_count):
    User_store.append([
        first_row[numbers[idx]],
        second_row[numbers[idx]],
        third_row[numbers[idx]],
        None
    ])

#점수를 받는 함수를 생성
def input_rating():
    file_path = data_path('user_item_matrix_with_imputation.csv')
    df = pd.read_csv(file_path)
    output_file_path = local_output_path('updated_user_item_matrix.xlsx')
    output_file_path2 = local_output_path('updated_user_item_matrix.csv')
    for i in range(len(User_store)):
        print(f"name: {User_store[i][0]}")
        print(f"tag: {User_store[i][1]}")
        print(f"Category: {User_store[i][2]}")
        k = float(input())
        print(k)
        User_store[i][3] = k

        name = User_store[i][0]

    #유저-아이템 매트릭스에 임의로 DEMO_USER라는 이름의 행을 2행에 만들어 놓음. 미리 모두 0으로 처리함.
        user_row_index = df[df.iloc[:, 0] == 'DEMO_USER'].index[0]
        column_index = df.columns.get_loc(name)

    # DEMO_USER 행에서 해당 열의 값을 업데이트
        df.iloc[user_row_index, column_index] = k
        #df.to_excel(output_file_path, index=False) #엑셀은 너무 느려서 배제.
        df.to_csv(output_file_path2, index=False)

    #df.to_excel(output_file_path, index=False) #엑셀은 너무 느려서 배제.

    #csv 파일로 저장함.
    df.to_csv(output_file_path2, index=False)
    print(f"Updated data has been saved to '{output_file_path2}'.")
# 수정된 데이터프레임을 엑셀 파일로 저장

#6개의 가게에 대한 rating을 받는다.
input_rating()

#유저의 평가태그에 대한 벡터를 생성.
User_vector = np.zeros(shape=(100,))

#받은 가게마다 평가태그를 ,로 나누고나서 각각의 문장의 벡터를 매칭해 평가한 점수를 가중치로 곱한다.
#그 이후에 받은 가게의 평가 태그를 모두 합하면 유저의 특성을 살린 평가태그 벡터가 완성된다.
for i in range(len(User_store)):
    User_sentences = []
    cell_sentences = []
    cell_sentences = [sentence.strip() for sentence in User_store[i][1].split(',')]
    User_sentences.extend(cell_sentences)
    User_i_vector = np.zeros(shape=(100,))
    for User_sentence in User_sentences:
        for g in range(56):
            if User_sentence == sentence_vectors_key[g]:
                User_i_vector += sentence_vectors[sentence_vectors_key[g]]
                User_i_vector = User_i_vector * (User_store[i][3]-2.5) # 2.5에서 빼서 부정적인 것은 음수로 나오게 만듦.

    #print(User_i_vector) #각각의 가게마다 유저의 평가 태그의 벡터
    #이를 모두 합하면 유저의 평가 태그에 대한 벡터 완성.
    User_vector += User_i_vector

#print(User_vector)

#유저의 선택한 카테고리에 대한 벡터를 생성.
User_category = np.zeros(shape=(100,))

#위의 평가태그와 같은 방법을 이용.
for i in range(len(User_store)):
    User_i_cat = np.zeros(shape=(100,))
    for g in range(66):
        if User_store[i][2] == unique_category_vectors_key[g]:
            User_i_cat = unique_category_vectors[unique_category_vectors_key[g]] * (User_store[i][3]-2.5)

    #print(User_i_cat) # 각 가게마다 카테고리에 대한 평가의 벡터

    #이를 모두 합하면 유저가 평가한 가게의 카테고리에 대한 선호도가 나온다.
    User_category += User_i_cat

#print(User_category)

#각각의 코사인 유사도에 a와 b의 가중치를 주기 위해 만든 함수
def store_ranking(a,b):
    return {store: (cosine_similarity(User_vector, store_vectors[store])*a + cosine_similarity(User_category, store_category[store])*b)/(a+b) for store in store_vectors_key}


contents_filtering_rank = store_ranking(0.5,0.5)

print(contents_filtering_rank)

#크기 순으로 value값을 정렬해 순서를 보여줌
sorted_keys_desc = sorted(contents_filtering_rank, key=lambda x: contents_filtering_rank[x], reverse=True)
print(sorted_keys_desc)
