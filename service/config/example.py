import pandas as pd
import time

start_time = time.time()

# Step 1: Read users.csv into table "user"
users = pd.read_csv('/data/dlbench/users.csv')

......Examples omit the intermediate processing steps

output_columns = ['book_id', 'title', 'feedback','total_friend_reviews', 'avg_friend_rating', 'mike_rating']
final_data = final_data[output_columns]

# Analyze if Mike’s social circle has unique book review preferences.
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA

# Load the books_analysis
books_analysis_df = final_data[output_columns]

# Calculate rating difference: Mike's rating vs. friends' average rating
books_analysis_df["rating_diff"] = books_analysis_df["mike_rating"] - books_analysis_df["avg_friend_rating"]

# Color mapping: Blue = Friends' rating > Platform rating, Red = Friends' rating < Platform rating, Green = Consistent
colors = np.where(books_analysis_df["rating_diff"] > 0, "blue", 
                  np.where(books_analysis_df["rating_diff"] < 0, "red", "green"))

# Create scatter plot (bubble chart)
plt.figure(figsize=(10, 6))
scatter = plt.scatter(
    books_analysis_df["mike_rating"], 
    books_analysis_df["avg_friend_rating"], 
    s=books_analysis_df["total_friend_reviews"] * 10,  # Make bubble size proportional to review count
    c=colors, 
    alpha=0.6, 
    edgecolors="k"
)

# Labels and title
plt.xlabel("Mike's Rating")
plt.ylabel("Friends' Average Rating")
plt.title("Mike's Ratings vs. Friends' Ratings (Bubble Size = Friend Reviews)")

# Show reference lines for average ratings
plt.axhline(y=np.mean(books_analysis_df["avg_friend_rating"]), color="gray", linestyle="--", label="Avg Friend Rating")
plt.axvline(x=np.mean(books_analysis_df["mike_rating"]), color="gray", linestyle="--", label="Avg Mike Rating")
plt.legend()

# Save and display the bubble chart
bubble_chart_path = "./mike_vs_friends_bubble_chart.png"
plt.savefig(bubble_chart_path)
print(f"Analysis image saved to {bubble_chart_path}")
plt.show()
