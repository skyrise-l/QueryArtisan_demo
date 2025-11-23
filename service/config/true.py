import pandas as pd
import time
import psutil

# 获取当前进程 ID
pid = psutil.Process().pid
process = psutil.Process(pid)

# 获取初始的 CPU 时间
cpu_time_before = process.cpu_times()

memory_info_before = process.memory_info()

start = time.time()

# Step 1: Read users.csv into table "user"
users = pd.read_csv('/mnt/d/study/vldb_demo/demo/chat/data/dlbench/users.csv')

# Step 2: Read user_relations.csv into table user_relations
user_relations = pd.read_csv('/mnt/d/study/vldb_demo/demo/chat/data/dlbench/user_relations.csv')

# Step 3: Read review_items from 'books_reviews.json' (extract "review" subfield)
review_items = pd.read_csv('/mnt/d/study/vldb_demo/demo/chat/data/dlbench/review_items.csv')

# Step 4: Read book_reviews from 'books_reviews.json' (main part, no subfield)
books_reviews = pd.read_csv('/mnt/d/study/vldb_demo/demo/chat/data/dlbench/books_reviews.csv')

# Step 5: Read books.csv into table books
books = pd.read_csv('/mnt/d/study/vldb_demo/demo/chat/data/dlbench/books.csv')

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

# Step 15: Write the final results to '/mnt/d/study/vldb_demo/demo/chat/data/dlbench/books_Analysis.csv'
output_columns = ['book_id', 'title', 'feedback','total_friend_reviews', 'avg_friend_rating', 'mike_rating']
final_joined_data[output_columns].to_csv('/mnt/d/study/vldb_demo/demo/chat/data/dlbench/books_Analysis.csv', index=False)



memory_info_after = process.memory_info()

end = time.time() - start

# 计算内存使用情况（单位：MB）
memory_usage_before = memory_info_before.rss / (1024 ** 2)  # 转换为MB
memory_usage_after = memory_info_after.rss / (1024 ** 2)    # 转换为MB
memory_used = memory_usage_after - memory_usage_before

print(f"Total execution time: {end:.2f} seconds")
print(f"Memory usage before execution: {memory_usage_before:.2f} MB")
print(f"Memory usage after execution: {memory_usage_after:.2f} MB")
print(f"Memory used during execution: {memory_used:.2f} MB")


