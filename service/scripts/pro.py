import json
import pandas as pd

# 输入 JSON 文件路径
json_file = "books_reviews.json"  # 请替换成你的 JSON 文件路径

# 初始化存储数据的列表
books_reviews_list = []
review_items_list = []

# 读取 JSON 文件并解析
with open(json_file, "r", encoding="utf-8") as f:
    book_review_id = 1  # 自增 ID
    
    for line in f:
        data = json.loads(line.strip())  # 解析 JSON 行
        
        # 添加到 books_reviews
        books_reviews_list.append({
            "id": book_review_id,
            "feedback": data["feedback"],
            "review_num": data["review_num"],
            "book_id": data["book_id"]
        })
        
        # 解析 review_items
        for review in data["review"]:
            if review["user_id"] is not None and not pd.isna(review["user_id"]):  # 过滤 user_id 为空的项
                review_items_list.append({
                    "id": review["id"],
                    "review_time": review["review_time"],
                    "book_reviews_id": book_review_id,  # 关联 books_reviews
                    "user_id": int(review["user_id"]),  # 转换 user_id 为 int 类型
                    "user_name": review["user_name"],
                    "score": review["score"]
                })
        
        book_review_id += 1  # 自增 ID

# 转换为 DataFrame
books_reviews_df = pd.DataFrame(books_reviews_list)
review_items_df = pd.DataFrame(review_items_list)

# 保存为 CSV
books_reviews_df.to_csv("books_reviews.csv", index=False, encoding="utf-8")
review_items_df.to_csv("review_items.csv", index=False, encoding="utf-8")


