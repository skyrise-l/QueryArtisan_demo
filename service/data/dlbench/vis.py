import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA

# 读取现有的 books_analysis.csv 文件
file_path = "./optimized_books_analysis.csv"
books_analysis_df = pd.read_csv(file_path)

# 计算评分差异：Mike 评分 vs. 朋友评分
books_analysis_df["rating_diff"] = books_analysis_df["mike_rating"] - books_analysis_df["avg_friend_rating"]

# 颜色映射：蓝色代表朋友评分高于平台评分，红色代表朋友评分低于平台评分，绿色代表一致
colors = np.where(books_analysis_df["rating_diff"] > 0, "blue", 
                  np.where(books_analysis_df["rating_diff"] < 0, "red", "green"))

# 创建散点图（气泡图）
plt.figure(figsize=(10, 6))
scatter = plt.scatter(
    books_analysis_df["mike_rating"], 
    books_analysis_df["avg_friend_rating"], 
    s=books_analysis_df["total_friend_reviews"] * 10,  # 使气泡大小更明显
    c=colors, 
    alpha=0.6, 
    edgecolors="k"
)

# 标题和标签
plt.xlabel("Mike's Rating")
plt.ylabel("Friends' Average Rating")
plt.title("Mike's Ratings vs. Friends' Ratings (Bubble Size = Friend Reviews)")

# 显示均值参考线
plt.axhline(y=np.mean(books_analysis_df["avg_friend_rating"]), color="gray", linestyle="--", label="Avg Friend Rating")
plt.axvline(x=np.mean(books_analysis_df["mike_rating"]), color="gray", linestyle="--", label="Avg Mike Rating")
plt.legend()

# 保存并显示图表
bubble_chart_path = "./mike_vs_friends_bubble_chart.png"
plt.savefig(bubble_chart_path)
plt.show()


# 绘制密度图
plt.figure(figsize=(10, 6))
sns.kdeplot(books_analysis_df["rating_diff"], fill=True, color="blue", alpha=0.6)

# 添加标题和标签
plt.title("Density Plot of Rating Differences (Mike vs Friends)")
plt.xlabel("Rating Difference (Mike's Rating - Friends' Average Rating)")
plt.ylabel("Density")

# 保存并显示图表
density_chart_path = "./mike_rating_density_plot.png"
plt.savefig(density_chart_path)
plt.show()

# K-Means Clustering
clustering_data = books_analysis_df[['avg_friend_rating', 'mike_rating']].dropna()
kmeans = KMeans(n_clusters=3, random_state=42)
clustering_data['cluster'] = kmeans.fit_predict(clustering_data)

plt.figure(figsize=(10, 6))
sns.scatterplot(
    x=clustering_data['mike_rating'], 
    y=clustering_data['avg_friend_rating'], 
    hue=clustering_data['cluster'], 
    palette='viridis', 
    alpha=0.7, 
    edgecolor='black')
plt.xlabel("Mike's Rating")
plt.ylabel("Friends' Average Rating")
plt.title("K-Means Clustering of Book Ratings")
plt.legend(title="Cluster")
kmeans_chart_path = "./mike_vs_friends_kmeans.png"
plt.savefig(kmeans_chart_path)
plt.show()


# PCA Analysis
pca = PCA(n_components=2)
pca_result = pca.fit_transform(clustering_data[['avg_friend_rating', 'mike_rating']])
clustering_data['pca_x'] = pca_result[:, 0]
clustering_data['pca_y'] = pca_result[:, 1]

plt.figure(figsize=(10, 6))
sns.scatterplot(
    x=clustering_data['pca_x'], 
    y=clustering_data['pca_y'], 
    hue=clustering_data['cluster'], 
    palette='coolwarm', 
    alpha=0.7, 
    edgecolor='black')
plt.xlabel("PCA Component 1")
plt.ylabel("PCA Component 2")
plt.title("PCA Analysis of Book Ratings")
pca_chart_path = "./mike_vs_friends_pca.png"
plt.savefig(pca_chart_path)
plt.show()
