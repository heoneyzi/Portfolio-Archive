from taste_trip.paths import data_path, image_path as local_image_path, output_path as local_output_path
## imputation code

import pandas as pd
import numpy as np
import openpyxl

file_path_1 = data_path('Final_merged_similarity_matrix.xlsx')
file_path_2 = data_path('final_user_item_matrix.csv')
sim_df = pd.read_excel(file_path_1, index_col=0) # 337 * 337
user_item_df = pd.read_csv(file_path_2, index_col=0)


# similarity df의 대각원소를 모두 0으로 만들기

for i in range(min(sim_df.shape)):
    sim_df.iat[i, i] = 0


# 유사도 top n 가게 함수

def top_n_similar(sim_dict, n):
    sim_dict_sorted = dict(sorted(sim_dict.items(), key=lambda item: item[1], reverse=True))
    top_n = dict(list(sim_dict_sorted.items())[:n])
    return top_n


# 긍정/부정에 따른 점수 부여 함수

def calc_rating(origin_score, similarity):
    # 긍정일 때
    if origin_score >= 2.5:
        imput_score = origin_score * similarity

    # 부정일 때
    else:
        imput_score = 5 - (5-origin_score) * similarity

    return imput_score


# imputation rule에 따른 함수 만들기

User = list(user_item_df.index)
Item = user_item_df.columns[1:,]


def imputation(user_item_df, sim_df) :

    user_item_imput = user_item_df.copy()

    for u in range(len(User)):
        user = User[u]
        row = user_item_df.iloc[u,:] # user_item_matrix에서의 유저별 행

        user_rating = {col: row[col] for col in Item if row[col] != 0 and col} # 유저별 방문한 가게에 대한 rating
        item_list_per_user = list(user_rating.keys()) # 유저별 방문한 가게 리스트
        score_list_per_user = list(user_rating.values()) # 유저별 평점 리스트

        # 리뷰수 1개
        if len(item_list_per_user) == 1:
            for i in item_list_per_user:
                sim_dict = sim_df[i].to_dict()
                top_n_sim_dict = top_n_similar(sim_dict, 4)

                imput = list(top_n_sim_dict.keys()) # 새로 추가할 가게
                similarity = list(top_n_sim_dict.values()) # 해당 가게들의 유사도

                for j in range(len(imput)):
                    user_item_imput.loc[user, imput[j]] = calc_rating(score_list_per_user[0], similarity[j])


        # 리뷰수 2개
        elif len(item_list_per_user) == 2:

            k = 0

            for i in item_list_per_user:
                sim_dict = sim_df[i].to_dict()
                top_n_sim_dict = top_n_similar(sim_dict, 2)

                imput = list(top_n_sim_dict.keys())
                similarity = list(top_n_sim_dict.values())

                for j in range(len(imput)):
                    user_item_imput.loc[user, imput[j]] = calc_rating(score_list_per_user[k], similarity[j])

                k += 1


        # 리뷰수 3개, 4개
        elif 3<= len(item_list_per_user) <= 4:

            k = 0

            for i in item_list_per_user:
                sim_dict = sim_df[i].to_dict()
                top_n_sim_dict = top_n_similar(sim_dict, 1)

                imput = list(top_n_sim_dict.keys())
                similarity = list(top_n_sim_dict.values())

                for j in range(len(imput)):
                    user_item_imput.loc[user, imput[j]] = calc_rating(score_list_per_user[k], similarity[j])

                k += 1

    return user_item_imput



user_item_imput = imputation(user_item_df, sim_df)

output_path = local_output_path('user_item_matrix_with_imputation.xlsx')
user_item_imput.to_excel(output_path)

print(f"파일이 {output_path}에 저장되었습니다.")
