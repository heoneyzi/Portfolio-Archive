import matplotlib.pyplot as plt

# 태그 유사도 분포
tag_data = tag_df.values.flatten()
cate_data = cate_df.values.flatten()

fig, axes = plt.subplots(1, 2, figsize=(14, 6))

axes[0].hist(tag_data, bins=30)
axes[0].set_title('Tag Similarity')
axes[0].set_xlim(0, 1.0)

axes[1].hist(cate_data, bins=30)
axes[1].set_title('Category Similarity')
axes[1].set_xlim(0, 1.0)


plt.show()
