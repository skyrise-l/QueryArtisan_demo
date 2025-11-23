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

# Step 6: Join "users" and "user_relations" on users.user_id = user_relations.from_userId
user_relations_with_users = users.merge(user_relations, left_on='user_id', right_on='from_userId', how='inner')

# Step 7: Filter Step 6 where user_name = 'Mike'
mike_user_relations = user_relations_with_users[user_relations_with_users['user_name'] == 'Mike']

# Step 8: Filter Step 7 where relation = 'like' OR relation = 'follow'
mike_follow_or_like = mike_user_relations[mike_user_relations['relation'].isin(['like', 'follow'])]

# Step 9: Join the filtered user_relations (Step 8) with "review_items" (Step 3) on to_userId = review_items.user_id
mike_reviews = mike_follow_or_like.merge(review_items, left_on='to_userId', right_on='user_id', how='inner')

# Step 10: Aggregation - Group Step 9 by book_reviews_id and compute COUNT(*) AS total_friend_reviews
total_friend_reviews = mike_reviews.groupby('book_reviews_id', as_index=False).agg(
    total_friend_reviews=('score', 'count')
)

# Step 11: Aggregation - Group Step 9 by book_reviews_id and compute AVG(score) AS avg_friend_rating
avg_friend_rating = mike_reviews.groupby('book_reviews_id', as_index=False).agg(
    avg_friend_rating=('score', 'mean')
)

# Step 12: Filter Step 3 where user_id = user_id (Mike's ratings for the books he reviewed)
mike_ratings = review_items[review_items['user_id'] == mike_user_relations['user_id'].values[0]]
mike_ratings = mike_ratings[['book_reviews_id', 'score']].rename(columns={'score': 'mike_rating'})

# Step 13: Join "books_reviews" with "books" on book_id
book_info = books_reviews.merge(books, left_on='book_id', right_on='book_id', how='left')

# Step 14: Join Step 10 and Step 11 on book_reviews_id
aggregated_data = total_friend_reviews.merge(avg_friend_rating, on='book_reviews_id', how='left')

# Step 15: Join Step 14 with Step 12 on book_reviews_id
aggregated_and_ratings = aggregated_data.merge(mike_ratings, on='book_reviews_id', how='left')

# Step 16: Join Step 15 with Step 13 on book_reviews_id
final_data = aggregated_and_ratings.merge(book_info, left_on='book_reviews_id', right_on='id', how='left')

# Step 17: Write the final results to '/data/dlbench/books_Analysis.csv'
output_columns = ['book_id', 'title', 'feedback', 'total_friend_reviews', 'avg_friend_rating', 'mike_rating']
final_data[output_columns].to_csv('./2222books_Analysis.csv', index=False)




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
