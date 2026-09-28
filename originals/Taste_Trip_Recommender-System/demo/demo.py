from taste_trip.paths import data_path, image_path as local_image_path, output_path as local_output_path
import streamlit as st
import pandas as pd
from PIL import Image, ImageOps
import torch
import torch.nn as nn
import numpy as np
import matplotlib.pyplot as plt
import altair as alt

##########################################
### input 받기
##########################################

st.title("Taste Trip · Research interface prototype")
st.info("이 데모는 학습하지 않은 MF 모델을 사용하는 인터페이스 프로토타입입니다. 표시 점수는 검증된 개인화 추천이나 추천 품질 지표가 아닙니다.")
from taste_trip.check_data import missing_files
missing = missing_files("demo")
if missing:
    st.warning("로컬 데이터가 필요합니다. README의 데이터 준비 절차를 확인하세요.")
    st.code("\n".join(str(path) for path in missing))
    st.stop()

# 가게 데이터 불러오기
user_item_matrix = pd.read_csv(data_path('final_user_item_matrix_with_imputation.csv'))

# item_data.xlsx에서 가게 이미지 데이터 불러오기
Place_data_path = data_path('Item_data.xlsx')
Place_df = pd.read_excel(Place_data_path)
if "nickname" not in user_item_matrix.columns or "DEMO_USER" not in user_item_matrix["nickname"].values:
    st.error("평점 CSV에는 nickname 열과 DEMO_USER 행이 필요합니다.")
    st.stop()
required_columns = {"Name", "Top5 Tags", "Category", "5열", "6열"}
if not required_columns.issubset(Place_df.columns) or len(Place_df.columns) < 6:
    st.error("Item_data.xlsx 열 구조가 README의 스키마와 일치하지 않습니다.")
    st.stop()
store_names = Place_df['Name']  # 가게 이름 데이터

# session_state 초기화
if "page" not in st.session_state:
    st.session_state.page = 0

if "user_responses" not in st.session_state:
    st.session_state.user_responses = {}

if "button_clicked" not in st.session_state:
    st.session_state.button_clicked = False

if "user_item_matrix" not in st.session_state:
    st.session_state.user_item_matrix = user_item_matrix.copy()

# 현재 페이지와 가게 이름 설정
store_names_list = ['서울객점', '강변서재', '스몰톡', '후무', '선유수제맥주', '브링미커피 브루어스']
current_page = st.session_state.page


# 현재 페이지가 가게 수를 벗어나는 경우 다음 단계로 이동
if current_page < len(store_names_list):
    store_name = store_names_list[current_page]

    # 현재 가게 이름 및 이미지 표시
    st.write("### 👍🏻 가게를 평가해 주세요")

    # JPEG 이미지를 불러와서 Streamlit에서 표시 (이미지 경로는 가게 이름 기준)
    image_path = local_image_path(f"{store_name}.png")
    try:
        image = Image.open(image_path)
        st.image(image, use_column_width=True)
    except FileNotFoundError:
        st.error(f"{store_name}에 해당하는 이미지 파일을 찾을 수 없습니다.")

    if 'button_clicked' not in st.session_state:
        st.session_state.button_clicked = False

    # 평가 점수 저장 및 다음 가게로 이동하는 함수
    def save_response_and_next(score):

        st.session_state.button_clicked = True

        # 사용자가 평가한 점수를 세션에 저장
        st.session_state.user_responses[store_name] = score

        # 'DEMO_USER'가 첫 번째 사용자인 경우, 해당 사용자의 평가 점수 업데이트
        st.session_state.user_item_matrix.loc[
            st.session_state.user_item_matrix['nickname'] == 'DEMO_USER', store_name
        ] = score

        # 다음 페이지로 이동, 마지막 페이지라면 평가 결과와 업데이트된 행렬 표시
        if current_page < len(store_names_list)-1:
            st.session_state.page += 1
            st.session_state.button_clicked = False  # 페이지 전환 후 버튼 플래그 초기화
        else:
            # 모든 가게 평가가 끝났을 때
            st.session_state.page = 7  # p. 7로 넘어가기 위해 페이지 값 설정
            st.write("모든 가게를 평가했습니다.")
            st.write("사용자 평가 결과:", st.session_state.user_responses)
            st.write("업데이트된 유저-아이템 매트릭스:")
            st.dataframe(st.session_state.user_item_matrix)

    # 평가 버튼 생성
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("별로예요"):
            save_response_and_next(2.0)
    with col2:
        if st.button("괜찮아요"):
            save_response_and_next(3.5)
    with col3:
        if st.button("꼭 가고 싶어요"):
            save_response_and_next(5.0)

# 데이터 로드
df = Place_df

first_row = df.iloc[:, 0]
second_row = df.iloc[:, 1]
third_row = df.iloc[:, 2]
fourth_row = df.iloc[:, 3]
fifth_row = df.iloc[:, 4]
sixth_row = df.iloc[:, 5]

# MF 모델 데이터 로드 및 처리
rating_data = user_item_matrix
rating_df = rating_data.melt(id_vars=['nickname'], var_name='store', value_name='rating')

user_mapping = {user: idx for idx, user in enumerate(rating_df['nickname'].unique())}
item_mapping = {item: idx for idx, item in enumerate(rating_df['store'].unique())}
rating_df['userId'] = rating_df['nickname'].map(user_mapping)
rating_df['itemId'] = rating_df['store'].map(item_mapping)

class MF(nn.Module):
    def __init__(self, num_users, num_items, embedding_dim=10):
        super(MF, self).__init__()
        self.user_embedding = nn.Embedding(num_users, embedding_dim)
        self.item_embedding = nn.Embedding(num_items, embedding_dim)

    def forward(self, user, item):
        user_embedded = self.user_embedding(user)
        item_embedded = self.item_embedding(item)
        return (user_embedded * item_embedded).sum(1)

# 초기화
num_users = len(user_mapping)
num_items = len(item_mapping)
embedding_dim = 10
model = MF(num_users, num_items, embedding_dim)

# 추천 생성 함수
def recommend_for_user(user_id, model, top_n=337):
    if isinstance(user_id, str):
        user_id = user_mapping.get(user_id)
        user_id = torch.tensor(user_id)

    all_items = torch.arange(num_items)

    with torch.no_grad():
        predictions = model(user_id, all_items)

    top_values, top_items = torch.topk(predictions, min(top_n, num_items))
    recommended_items = [list(item_mapping.keys())[idx] for idx in top_items.cpu().numpy()]
    recommended_values = top_values.cpu().numpy().tolist()
    return recommended_items, recommended_values



# 세션 상태에 추천 결과 저장
if 'recommended_items' not in st.session_state:
    user_id = "DEMO_USER"
    recommended_items, recommended_values = recommend_for_user(user_id, model)
    st.session_state['recommended_values'] = recommended_values
    st.session_state['recommended_items'] = recommended_items
else:
    recommended_items = st.session_state['recommended_items']
    recommended_values = st.session_state['recommended_values']

# 페이지 세션 상태
if 'page' not in st.session_state:
    st.session_state['page'] = 1

def go_to_next_page():
    st.session_state['page'] += 1

# 식당 리스트 4개 추출
food_list = []
food_values = []
food_num = 0
food_dic = {}
for i in range(len(recommended_items)):
    for g in range(len(first_row)):
        if recommended_items[i] == first_row[g]:
            if str(fourth_row[g]) == "식사":
                food_list.append(recommended_items[i])
                food_values.append(recommended_values[i])
                food_num += 1
                if food_num == 4:
                    break
    if food_num == 4:
        break
food_dic = {a:b for a,b in zip(food_list, food_values)}

# 페이지 내용을 위한 placeholder 생성
page_placeholder = st.empty()

with page_placeholder.container():
    # 첫 번째 페이지 (식당 정보)
    if st.session_state['page'] == 7:
        st.title("🍽️ 가고 싶은 식당을 골라주세요")
        st.write("각 가게에 대한 상세 정보를 확인할 수 있어요")

        food_desc = {}
        for item in food_list:
            food_name = item
            food_tag = df.loc[df['Name'] == food_name, 'Top5 Tags'].values[0]
            food_cate = df.loc[df['Name'] == food_name, 'Category'].values[0]
            food_place = df.loc[df['Name'] == food_name, '5열'].values[0]
            food_desc[food_name] = {
                'tags': food_tag.split(', '),
                'category': food_cate,
                'location': food_place
            }

        food_pick = None  # 선택한 식당을 저장할 변수

        for food_name in food_desc:
            desc = food_desc[food_name]
            col1, col2, col3 = st.columns([2, 2, 0.5])

            with col1:
                image_path = local_image_path(f"{food_name}.jpeg")
                try:
                    image = Image.open(image_path)
                    rounded_image = ImageOps.fit(image, (250, 250), method=0, bleed=0.0, centering=(0.5, 0.5))
                    rounded_image = rounded_image.convert("RGBA")
                    st.image(rounded_image, caption=food_name, use_column_width=True)
                except FileNotFoundError:
                    st.error(f"{food_name}.jpeg 이미지 파일을 찾을 수 없습니다.")

            with col2:
                st.write(f"**{desc['category']}** @ **{desc['location']}**")
                for tag in desc['tags']:
                    st.write(f"{tag}")

            with col3:
                checked = st.checkbox("선택", key=food_name)
                if checked:
                    food_pick = food_name

        col_left, col_right = st.columns([9, 1])
        with col_right:
            if st.button("다음", key="food_next"):
                st.session_state['food_pick'] = food_pick
                go_to_next_page()

    # 두 번째 페이지 (카페 정보)
    elif st.session_state['page'] == 8:
        st.title("☕ 가고 싶은 카페를 골라주세요")
        st.write("각 가게에 대한 상세 정보를 확인할 수 있어요")

        food_loc = df.loc[df['Name'] == st.session_state['food_pick'], '6열'].values[0]

        cafe_list = []
        cafe_num = 0

        for i in range(len(recommended_items)):
            for g in range(len(first_row)):
                if recommended_items[i] == first_row[g]:
                    if (str(fourth_row[g]) == "디저트") & (str(sixth_row[g]) == food_loc):
                        cafe_list.append(recommended_items[i])
                        cafe_num += 1
                        if cafe_num == 4:
                            break
            if cafe_num == 4:
                break

        cafe_desc = {}
        for item in cafe_list:
            cafe_name = item
            cafe_tag = df.loc[df['Name'] == cafe_name, 'Top5 Tags'].values[0]
            cafe_cate = df.loc[df['Name'] == cafe_name, 'Category'].values[0]
            cafe_place = df.loc[df['Name'] == cafe_name, '5열'].values[0]
            cafe_desc[cafe_name] = {
                'tags': cafe_tag.split(', '),
                'category': cafe_cate,
                'location': cafe_place
            }

        cafe_pick = None  # 선택한 카페를 저장할 변수

        for cafe_name in cafe_desc:
            desc = cafe_desc[cafe_name]
            col1, col2, col3 = st.columns([2, 2, 0.5])

            with col1:
                image_path = local_image_path(f"{cafe_name}.jpeg")
                try:
                    image = Image.open(image_path)
                    rounded_image = ImageOps.fit(image, (250, 250), method=0, bleed=0.0, centering=(0.5, 0.5))
                    rounded_image = rounded_image.convert("RGBA")
                    st.image(rounded_image, caption=cafe_name, use_column_width=True)
                except FileNotFoundError:
                    st.error(f"{cafe_name}.jpeg 이미지 파일을 찾을 수 없습니다.")

            with col2:
                st.write(f"**{desc['category']}** @ **{desc['location']}**")
                for tag in desc['tags']:
                    st.write(f"{tag}")

            with col3:
                checked = st.checkbox("선택", key=cafe_name)
                if checked:
                    cafe_pick = cafe_name

        col_left, col_right = st.columns([9, 1])
        with col_right:
            if st.button("다음", key="cafe_next"):
                st.session_state['cafe_pick'] = cafe_pick
                go_to_next_page()

    # 최종 선택한 식당과 카페 확인
    elif st.session_state['page'] == 9:
        st.write(f"선택한 식당: {st.session_state['food_pick']}")
        st.write(f"선택한 카페: {st.session_state['cafe_pick']}")

        go_to_next_page()
    # 가게 정보 화면

        st.title("가게 정보")

            # 가게 이름을 미리 설정합니다.
        store_list = [st.session_state['food_pick'], st.session_state['cafe_pick']]

            # Place_URL_original.xlsx 파일을 읽어옵니다.
        place_df = pd.read_excel(data_path('Place_URL_with address.xlsx'))

            # 가게 설명을 저장할 딕셔너리
        store_descriptions = {}

            # store_list의 값이 Place_URL_original.xlsx의 1열에 있는지 확인하고, 해당하는 2, 3, 4열 값을 저장
        for store in store_list:
            # store가 1열에 있는지 확인
            store_data = place_df[place_df.iloc[:, 0] == store]
            if not store_data.empty:
                # 2, 3, 4열 값을 가져와서 설명으로 저장
                col2_value = store_data.iloc[0, 1]
                col3_value = store_data.iloc[0, 2]
                col4_value = store_data.iloc[0, 3]
                store_descriptions[store] = f"카테고리: {col4_value}\n주소:{col3_value}\n링크: {col2_value}"
            else:
                store_descriptions[store] = "해당 가게에 대한 정보가 없습니다."

            # 각 가게에 대한 설명과 이미지를 Streamlit으로 출력
        for store in store_list:
            image_path = local_image_path(f"{store}.jpeg")  # 가게 이름에 해당하는 이미지 경로 설정
            try:
                image = Image.open(image_path)
                st.image(image, caption=store, use_column_width=True)

                    # 가게에 대한 설명 출력
                if store in store_descriptions:
                    st.text(store_descriptions[store])  # 줄바꿈을 위해 st.write 대신 st.text 사용
                else:
                    st.write(f"{store}에 대한 설명이 없습니다.")

            except FileNotFoundError:
                st.error(f"{store}.jpeg 이미지 파일을 찾을 수 없습니다.")
                if store in store_descriptions:
                    st.text(store_descriptions[store])  # 줄바꿈을 위해 st.write 대신 st.text 사용
                else:
                    st.write(f"{store}에 대한 설명이 없습니다.")

        st.title("Top4 식당 점수")

# 딕셔너리를 데이터프레임으로 변환
        food_df = pd.DataFrame(list(food_dic.items()), columns=['Food Items', 'Values'])

# 막대그래프 그리기
        bar_chart = alt.Chart(food_df).mark_bar().encode(
            x='Food Items',
            y='Values',
            color='Food Items',  # Food Items 별로 색상 구분
            tooltip=['Food Items', 'Values']  # 툴팁 표시
        ).properties(
            width=600,
            height=400,
            title="학습하지 않은 MF 모델의 예시 점수입니다"
        )

# 그래프를 Streamlit에 표시
        st.altair_chart(bar_chart, use_container_width=True)

            # 돌아가기 버튼
        #if st.button("돌아가기"):
        #    go_back()
