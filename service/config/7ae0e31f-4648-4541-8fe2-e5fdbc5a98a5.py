import pandas as pd
import table_deal, json_deal, graph_deal

# Step 1: Read users.csv into table "user"
users = table_deal.read('/data/dlbench/users.csv')

# Step 2: Read user_relations.csv into table user_relations
user_relations = graph_deal.read('/data/dlbench/user_relations.csv')

# Step 3: Read review_items from 'books_reviews.json' (extract "review" subfield)
review_items = json_deal.read('/data/dlbench/books_reviews.json', 1, 'review')

# Step 4: Read book_reviews from 'books_reviews.json' (main part, no subfield)
books_reviews = json_deal.read('/data/dlbench/books_reviews.json', 0, None)

# Step 5: Read books.csv into table books
books = table_deal.read('/data/dlbench/books.csv')

# Step 6: Filter out Mike from the "users" table
mike_user = users[users['user_name'] == 'Mike']

# Step 7: Filter user_relations to keep only rows where relation is "like" or "follow"
relations_filtered = user_relations[user_relations['relation'].isin(['like', 'follow'])]

# Step 8: Join the filtered "user" (Mike) with filtered user_relations on user_id = from_userId
mike_user_relations = mike_user.merge(relations_filtered,left_on='user_id',right_on='from_userId',how='inner')

# Step 9: Join mike_user_relations with review_items on to_userId = review_item.user_id
mike_reviews = mike_user_relations.merge(review_items,left_on='to_userId',right_on='user_id',how='inner')

# Step 10: Aggregate - group by book_reviews_id to compute avg_friend_rating (AVG) and total_reviews per friend.
book_review_aggregates = (mike_reviews.groupby('book_reviews_id', as_index=False).agg(
        total_friend_reviews=('score', 'count'),
        avg_friend_rating=('score', 'mean')
    )
)

# Step 11: Join book_reviews with books on book_id
book_info_extended = books_reviews.merge(books,left_on='book_id',right_on='book_id',how='left')

# Step 12: Join book_review_aggregates with book_info_extended on book_reviews_id
combined_aggregates_result = book_review_aggregates.merge(book_info_extended,left_on='book_reviews_id',right_on='id',how='left')

# Step 13: Add Mike's own ratings for the books he reviewed, if available
mike_ratings = review_items[review_items['user_id'] == mike_user['user_id'].values[0]]
mike_ratings = mike_ratings[['book_reviews_id', 'score']].rename(columns={'score': 'mike_rating'})

# Step 14: Join combined_aggregates with mike_ratings on book_reviews_id
final_joined_data = combined_aggregates_result.merge(mike_ratings,on='book_reviews_id', how='left')

# Step 15: Write the final results to '/data/dlbench/books_Analysis.csv'
output_columns = ['book_id', 'title', 'feedback','total_friend_reviews', 'avg_friend_rating', 'mike_rating']
result_path = '/data/dlbench/books_Analysis.csv'
final_joined_data[output_columns].to_csv(result_path, index=False)
print(f"Query Result file saved to {result_path}")

# Analyze if Mike’s social circle has unique book review preferences.
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA

# Load the books_analysis
books_analysis_df = final_joined_data[output_columns]

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
bubble_chart_path = "/data/dlbench/mike_vs_friends_bubble_chart.png"
plt.savefig(bubble_chart_path)
print(f"Analysis image saved to {bubble_chart_path}")
plt.show()

# Create density plot
plt.figure(figsize=(10, 6))
sns.kdeplot(books_analysis_df["rating_diff"], fill=True, color="purple", alpha=0.6)

# Labels and title
plt.title("Density Plot of Rating Differences (Mike vs Friends)")
plt.xlabel("Rating Difference (Mike's Rating - Friends' Average Rating)")
plt.ylabel("Density")

# Save and display the density plot
density_chart_path = "/data/dlbench/mike_rating_density_plot.png"
plt.savefig(density_chart_path)
print(f"Analysis image saved to {density_chart_path}")
plt.show()
