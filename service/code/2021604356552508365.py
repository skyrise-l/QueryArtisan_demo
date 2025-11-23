import pandas as pd
import json

# Load books data to find the book_id for 'Five Silly Turkeys'
books_df = pd.read_csv('/mnt/d/study/vldb_demo/demo/chat/data/dlbench/books.csv')
target_book = books_df[books_df['title'] == 'Five Silly Turkeys']
if target_book.empty:
    print("Book 'Five Silly Turkeys' not found.")
    exit()
book_id = target_book['book_id'].iloc[0]

# Process JSONL file to extract reviews for the specific book
reviews_data = []
with open('/mnt/d/study/vldb_demo/demo/chat/data/dlbench/book_reviews.json', 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if line:
            item = json.loads(line)
            if item['book_id'] == book_id:
                for review in item['review']:
                    review_entry = {
                        'book_id': item['book_id'],
                        'feedback': item['feedback'],
                        'review_num': item['review_num'],
                        'review_id': review['id'],
                        'review_time': review['review_time'],
                        'score': review['score'],
                        'user_id': review['user_id'],
                        'user_name': review['user_name']
                    }
                    reviews_data.append(review_entry)

# Convert to DataFrame and save results
if reviews_data:
    reviews_df = pd.DataFrame(reviews_data)
    reviews_df.to_csv('/mnt/d/study/vldb_demo/demo/chat/result/2021604356552508365.txt', index=False, sep='\t')
    print(f"Found {len(reviews_df)} reviews for 'Five Silly Turkeys'. Results saved.")
else:
    print("No reviews found for the specified book.")