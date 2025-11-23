

import sqlite3
import json
import re

class dataSource:
    def __init__(self, access_tokens):
        self.token_key = access_tokens[0]  

    def read_datasource(self):
        db_file = "/mnt/d/study/vldb_demo/demo/chat/data/dataset_metadata.db"
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT database_name FROM table_metadata")

        database_names = cursor.fetchall()

        # 关闭连接
        conn.close()

        return [name[0] for name in database_names]

    def parse_primary_key(self, pk_str):
        """
        解析形如：
        PRIMARY KEY : ("wedding_church_id", "male_id", "female_id")
        的字符串，提取主键列名列表。
        """
        if not pk_str:
            return []
        return re.findall(r'"(.*?)"', pk_str)

    # 解析外键关系的辅助函数
    def parse_foreign_key(self, fk_str):
        foreign_keys = []
        fk_list = re.findall(r'FOREIGN KEY: "(.*?)" REFERENCES "(.*?)\.(.*?)"', fk_str)
        for src_col, target_table, target_col in fk_list:
            foreign_keys.append({
                'source_col': src_col,
                'target_table': target_table,
                'target_col': target_col
            })
        return foreign_keys

    # 主函数，用于构建JSON数据结构
    def generate_json(self, datasource):

        try:
            db_path = '/mnt/d/study/vldb_demo/demo/chat/data/dataset_metadata.db'
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT table_name, column_name, table_type, data_format, foreign_key
                FROM table_metadata
                WHERE database_name = ?
            """, (datasource,))

            records = cursor.fetchall()
            conn.close()

            tables = {}
            columns = []
            dataLinks = []

            id_seq = 1
            table_name_to_id = {}

            # 首先构建tables
            for record in records:
                table_name, column_name, table_type, data_format, foreign_key = record

                if table_name not in tables:
                    table_entry = {
                        'id': id_seq,
                        'name': table_name,
                        'nodeType': 'Data Type',
                        'dataType': table_type if table_type else 'table',
                        'fks': ''
                    }
                    tables[table_name] = table_entry
                    table_name_to_id[table_name] = id_seq
                    id_seq += 1

            # 接下来构建columns
            for record in records:
                table_name, column_name, table_type, data_format, foreign_key = record
                column_entry = {
                    'id': id_seq,
                    'name': column_name,
                    'nodeType': 'Column Type',
                    'dataType': data_format,
                    'source': table_name_to_id[table_name],
                    'sourceName': table_name
                }
                columns.append(column_entry)
                id_seq += 1

            # 最后解析并构建datalinks
            processed_fk_tables = set()
            link_set = {}
            for record in records:
                table_name, column_name, table_type, data_format, foreign_key = record
                if foreign_key and table_name not in processed_fk_tables:
           
                    fks = self.parse_foreign_key(foreign_key)
           
                    for fk in fks:
                        target_table = fk['target_table']

                        src_id = table_name_to_id[table_name]
                        target_id = table_name_to_id[fk['target_table']]
                        
                 
                        fk_desc = f"{table_name}.{fk['source_col']} Foreign({target_table}.{fk['target_col']})"
                        target_table_fk_desc = f"{target_table}.{fk['target_col']} Foreign({table_name}.{fk['source_col']})"

                        tables[table_name]['fks'] += fk_desc + ".\n"
                        tables[target_table]['fks'] += target_table_fk_desc + ".\n"

                        if (src_id, target_id) in link_set:
                            link_set[(src_id, target_id)]['Condition'] += fk_desc + ".\n"
                        elif (target_id, src_id) in link_set:
                            link_set[(target_id, src_id)]['Condition'] += target_table_fk_desc + ".\n"
                        else:
                            link_set[(src_id, target_id)] = {
                                'id': id_seq,
                                'source': src_id,
                                'target': target_id,
                                'Condition': fk_desc
                            }

                        id_seq += 1
                    processed_fk_tables.add(table_name)
     
            dataLinks = list(link_set.values())

            # 转换成最终需要的结构
            result = {
                'tables': list(tables.values()),
                'columns': columns,
                'dataLinks': dataLinks
            }
        except Exception as e:
            print(f"response err : {str(e)}")
            result = {
                'tables': [],
                'columns': [],
                'dataLinks': []
            }

        return result
        

    def GetDataSourceDeatils(self, datasource):
        try:
            db_path = '/mnt/d/study/vldb_demo/demo/chat/data/dataset_metadata.db'
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT table_name, column_name, table_type, data_format, primary_key, foreign_key
                FROM table_metadata
                WHERE database_name = ?
            """, (datasource,))

            records = cursor.fetchall()
            records_dict = [dict(row) for row in records]

            # 用来存储每个表的主键列集合，以及外键的映射关系
            # table_pk_cols[表名] = {pk_col1, pk_col2, ...}
            table_pk_cols = {}
            # table_fk_map[表名] = {
            #     源列1: [对方表.对方列1, 对方表.对方列2, ...],
            #     源列2: [...],
            #     ...
            # }
            table_fk_map = {}

            # 1) 先把所有表的主键、外键信息收集起来
            for row in records_dict:
                tname = row['table_name']
                # 初始化该表在两个字典里的存储
                if tname not in table_pk_cols:
                    table_pk_cols[tname] = set()
                if tname not in table_fk_map:
                    table_fk_map[tname] = {}

                pk_str = row['primary_key']
                fk_str = row['foreign_key']

                # 解析并存储主键列
                if pk_str:
                    pk_cols = self.parse_primary_key(pk_str)
                    for col in pk_cols:
                        table_pk_cols[tname].add(col)

                # 解析并存储外键信息
                if fk_str:
                    fks = self.parse_foreign_key(fk_str)
                    for fk in fks:
                        src_col = fk['source_col']
                        ref = f"{fk['target_table']}.{fk['target_col']}"
                        if src_col not in table_fk_map[tname]:
                            table_fk_map[tname][src_col] = []
                        table_fk_map[tname][src_col].append(ref)

            # 2) 再对每条记录进行处理，把主外键信息分配到对应列
            for row in records_dict:
                tname = row['table_name']
                col_name = row['column_name']

                # 判断是否是主键列
                if col_name in table_pk_cols[tname]:
                    # 或者你也可以给字符串 "true"/"false"
                    row['primary_key'] = "True"
                else:
                    row['primary_key'] = "False"  # 或者留空字符串

                # 判断是否是外键列
                if col_name in table_fk_map[tname]:
                    # 如果一个列对应多个外键引用，用逗号分隔
                    row['foreign_key'] = ', '.join(table_fk_map[tname][col_name])
                else:
                    row['foreign_key'] = 'None'  # 或者 None

                # 如果没有 table_type，就默认赋值为 "table"
                if not row['table_type']:
                    row['table_type'] = "table"

            conn.close()

            result = {
                'details': records_dict
            }
        except Exception as e:
            print(f"response err : {str(e)}")
            result = {
                'details': []
            }

        return result
    
    def getLineageData(self, query_id, column_name):
        if column_name == "book_id":
            LineageData = [
                {
                    "id": "1",
                    "type": "table",
                    "dataname": "books",
                    "targetData": "None",
                    "operator": "Read books.csv into table books",
                    "code": "books = table_deal.read('/data/dlbench/books.csv')",
                },
                {
                    "id": "2",
                    "type": "json",
                    "dataname": "books_reviews",
                    "targetData": "None",
                    "operator": "Read book_reviews from 'books_reviews.json' (main part, no subfield)",
                    "code": "books_reviews = json_deal.read('/data/dlbench/books_reviews.json', 0, None)",
                },
                {
                    "id": "3",
                    "type": "table",
                    "dataname": "book_info_extended",
                    "targetData": "books_reviews, books",
                    "operator": "Join books and books_reviews on book_id",
                    "code": "book_info_extended = books_reviews.merge(books,left_on='book_id',right_on='book_id',how='left')",
                },
                {
                    "id": "4",
                    "type": "column",
                    "dataname": "book_id",
                    "targetData": "book_info_extended",
                    "operator": "get",
                    "code": "",
                }
            ]
            
            EdgeData = [
                {
                    "from": "1",
                    "to": "3",
                    "label": "join"
                },
                {
                    "from": "2",
                    "to": "3",
                    "label": "join" 
                },
                {
                    "from": "3",
                    "to": "4",
                    "label": "get" 
                }
            ]

        elif column_name == "title":
            LineageData = [
                {
                    "id": "1",
                    "type": "table",
                    "dataname": "books",
                    "targetData": "None",
                    "operator": "Read books.csv into table books",
                    "code": "books = table_deal.read('/data/dlbench/books.csv')",
                },
                {
                    "id": "2",
                    "type": "json",
                    "dataname": "books_reviews",
                    "targetData": "None",
                    "operator": "Read book_reviews from 'books_reviews.json' (main part, no subfield)",
                    "code": "books_reviews = json_deal.read('/data/dlbench/books_reviews.json', 0, None)",
                },
                {
                    "id": "3",
                    "type": "table",
                    "dataname": "book_info_extended",
                    "targetData": "books_reviews, books",
                    "operator": "Join books and books_reviews on book_id",
                    "code": "book_info_extended = books_reviews.merge(books,left_on='book_id',right_on='book_id',how='left')",
                },
                {
                    "id": "4",
                    "type": "column",
                    "dataname": "title",
                    "targetData": "book_info_extended",
                    "operator": "get",
                    "code": "",
                }
            ]
            
            EdgeData = [
                {
                    "from": "1",
                    "to": "3",
                    "label": "join"
                },
                {
                    "from": "2",
                    "to": "3",
                    "label": "join" 
                },
                {
                    "from": "3",
                    "to": "4",
                    "label": "get" 
                }
            ]
            
            EdgeData = [
                {
                    "from": "1",
                    "to": "3",
                    "label": "join"
                },
                {
                    "from": "2",
                    "to": "3",
                    "label": "join" 
                },
                {
                    "from": "3",
                    "to": "4",
                    "label": "get" 
                }
            ]
        elif column_name == "feedback":
            LineageData = [
                {
                    "id": "1",
                    "type": "json",
                    "dataname": "books_reviews",
                    "targetData": "None",
                    "operator": "Read book_reviews from 'books_reviews.json' (main part, no subfield)",
                    "code": "books_reviews = json_deal.read('/data/dlbench/books_reviews.json', 0, None)",
                },
                {
                    "id": "2",
                    "type": "column",
                    "dataname": "feedback",
                    "targetData": "books_reviews",
                    "operator": "get",
                    "code": "",
                }
            ]
            
            EdgeData = [
                {
                    "from": "1",
                    "to": "2",
                    "label": "join"
                }
            ]

        elif column_name == "total_friend_reviews":
            LineageData = [
                {
                    "id": "1",
                    "type": "graph",
                    "dataname": "users",
                    "targetData": "None",
                    "operator": "Read users.csv into table user",
                    "code": "users = table_deal.read('/data/dlbench/users.csv')",
                },
                {
                    "id": "2",
                    "type": "table",
                    "dataname": "mike_user",
                    "targetData": "users",
                    "operator": "Filter out Mike from the 'users' table",
                    "code": "mike_user = users[users['user_name'] == 'Mike']",
                },
                {
                    "id": "3",
                    "type": "graph",
                    "dataname": "user_relations",
                    "targetData": "None",
                    "operator": "Read user_relations.csv into table user_relations",
                    "code": "user_relations = table_deal.read('/data/dlbench/user_relations.csv')",
                },
                {
                    "id": "4",
                    "type": "table",
                    "dataname": "relations_filtered",
                    "targetData": "user_relations",
                    "operator": "Filter user_relations to keep only rows where relation is 'like' or 'follow'",
                    "code": "relations_filtered = user_relations[user_relations['relation'].isin(['like', 'follow'])]",
                },

                {
                    "id": "5",
                    "type": "table",
                    "dataname": "mike_user_relations",
                    "targetData": "mike_user, relations_filtered",
                    "operator": "Join the filtered 'user' (Mike) with filtered user_relations on user_id = from_userId",
                    "code": "mike_user_relations = mike_user.merge(relations_filtered,left_on='user_id',right_on='from_userId',how='inner')",
                },
                {
                    "id": "6",
                    "type": "json",
                    "dataname": "review_items",
                    "targetData": "None",
                    "operator": "Read review_items from 'books_reviews.json' (extract 'review' subfield)",
                    "code": "review_items = json_deal.read('/data/dlbench/books_reviews.json', 1, 'review')",
                },
                {
                    "id": "7",
                    "type": "table",
                    "dataname": "mike_reviews",
                    "targetData": "mike_user_relations, review_items",
                    "operator": "Join mike_user_relations with review_items on to_userId = review_item.user_id",
                    "code": "mike_reviews = mike_user_relations.merge(review_items,left_on='to_userId',right_on='user_id',how='inner')",
                },
                {
                    "id": "8",
                    "type": "table",
                    "dataname": "book_review_aggregates",
                    "targetData": "mike_reviews",
                    "operator": " Aggregate - group by book_reviews_id to compute avg_friend_rating (AVG) and total_reviews per friend.",
                    "code": "book_review_aggregates = (mike_reviews.groupby('book_reviews_id', as_index=False).agg(total_friend_reviews=('score', 'count'),avg_friend_rating=('score', 'mean')))",
                },
                {
                    "id": "9",
                    "type": "column",
                    "dataname": "total_friend_reviews",
                    "targetData": "book_review_aggregates",
                    "operator": "get",
                    "code": "",
                }
            ]
            
            EdgeData = [
                {
                    "from": "1",
                    "to": "2",
                    "label": "filter"
                },
                {
                    "from": "2",
                    "to": "5",
                    "label": "join"
                },
                {
                    "from": "3",
                    "to": "4",
                    "label": "filter"
                },
                {
                    "from": "4",
                    "to": "5",
                    "label": "join"
                },
                {
                    "from": "5",
                    "to": "7",
                    "label": "join"
                },
                {
                    "from": "6",
                    "to": "7",
                    "label": "join"
                },
                {
                    "from": "7",
                    "to": "8",
                    "label": "aggregation"
                },
                {
                    "from": "8",
                    "to": "9",
                    "label": "get"
                }
            ]


        elif column_name == "avg_friend_rating":
            LineageData = [
                {
                    "id": "1",
                    "type": "graph",
                    "dataname": "users",
                    "targetData": "None",
                    "operator": "Read users.csv into table user",
                    "code": "users = table_deal.read('/data/dlbench/users.csv')",
                },
                {
                    "id": "2",
                    "type": "table",
                    "dataname": "mike_user",
                    "targetData": "users",
                    "operator": "Filter out Mike from the 'users' table",
                    "code": "mike_user = users[users['user_name'] == 'Mike']",
                },
                {
                    "id": "3",
                    "type": "graph",
                    "dataname": "user_relations",
                    "targetData": "None",
                    "operator": "Read user_relations.csv into table user_relations",
                    "code": "user_relations = table_deal.read('/data/dlbench/user_relations.csv')",
                },
                {
                    "id": "4",
                    "type": "table",
                    "dataname": "relations_filtered",
                    "targetData": "user_relations",
                    "operator": "Filter user_relations to keep only rows where relation is 'like' or 'follow'",
                    "code": "relations_filtered = user_relations[user_relations['relation'].isin(['like', 'follow'])]",
                },

                {
                    "id": "5",
                    "type": "table",
                    "dataname": "mike_user_relations",
                    "targetData": "mike_user, relations_filtered",
                    "operator": "Join the filtered 'user' (Mike) with filtered user_relations on user_id = from_userId",
                    "code": "mike_user_relations = mike_user.merge(relations_filtered,left_on='user_id',right_on='from_userId',how='inner')",
                },
                {
                    "id": "6",
                    "type": "json",
                    "dataname": "review_items",
                    "targetData": "None",
                    "operator": "Read review_items from 'books_reviews.json' (extract 'review' subfield)",
                    "code": "review_items = json_deal.read('/data/dlbench/books_reviews.json', 1, 'review')",
                },
                {
                    "id": "7",
                    "type": "table",
                    "dataname": "mike_reviews",
                    "targetData": "mike_user_relations, review_items",
                    "operator": "Join mike_user_relations with review_items on to_userId = review_item.user_id",
                    "code": "mike_reviews = mike_user_relations.merge(review_items,left_on='to_userId',right_on='user_id',how='inner')",
                },
                {
                    "id": "8",
                    "type": "table",
                    "dataname": "book_review_aggregates",
                    "targetData": "mike_reviews",
                    "operator": " Aggregate - group by book_reviews_id to compute avg_friend_rating (AVG) and total_reviews per friend.",
                    "code": "book_review_aggregates = (mike_reviews.groupby('book_reviews_id', as_index=False).agg(total_friend_reviews=('score', 'count'),avg_friend_rating=('score', 'mean')))",
                },
                {
                    "id": "9",
                    "type": "column",
                    "dataname": "avg_friend_rating",
                    "targetData": "book_review_aggregates",
                    "operator": "get",
                    "code": "",
                }
            ]
            
            EdgeData = [
                {
                    "from": "1",
                    "to": "2",
                    "label": "filter"
                },
                {
                    "from": "2",
                    "to": "5",
                    "label": "join"
                },
                {
                    "from": "3",
                    "to": "4",
                    "label": "filter"
                },
                {
                    "from": "4",
                    "to": "5",
                    "label": "join"
                },
                {
                    "from": "5",
                    "to": "7",
                    "label": "join"
                },
                {
                    "from": "6",
                    "to": "7",
                    "label": "join"
                },
                {
                    "from": "7",
                    "to": "8",
                    "label": "aggregation"
                },
                {
                    "from": "8",
                    "to": "9",
                    "label": "get"
                }
            ]

        elif column_name == "mike_rating":
            LineageData = [
                {
                    "id": "1",
                    "type": "json",
                    "dataname": "review_item",
                    "targetData": "None",
                    "operator": "Load books_reviews into table review_item",
                    "code": "review_item = json_deal.read('/data/dlbench/books_reviews.json', 0, 'review')",
                },             
                {
                    "id": "2",
                    "type": "graph",
                    "dataname": "user",
                    "targetData": "None",
                    "operator": "Load users.csv into table user",
                    "code": "user = table_deal.read('/data/dlbench/users.csv')",
                },
                {
                    "id": "3",
                    "type": "table",
                    "dataname": "mike_ratings",
                    "targetData": "review_item, user",
                    "operator": "Add Mike's own ratings for the books he reviewed, if available",
                    "code": "mike_ratings = review_items[review_items['user_id'] == mike_user['user_id'].values[0]]\n mike_ratings = mike_ratings[['book_reviews_id', 'score']].rename(columns={'score': 'mike_rating'})",
                },
                {
                    "id": "4",
                    "type": "table",
                    "dataname": "mike_rating",
                    "targetData": "mike_ratings",
                    "operator": "get",
                    "code": "",
                }
            ]
            
            EdgeData = [
                {
                    "from": "1",
                    "to": "3",
                    "label": "filter"
                },
                {
                    "from": "2",
                    "to": "3",
                    "label": "filter" 
                },
                {
                    "from": "3",
                    "to": "4",
                    "label": "get"
                }
            ]
        else:
            LineageData = []
            EdgeData = []
    
        return LineageData, EdgeData
    

    def getSourceData(self, table_name):
   
        import pandas as pd 
        if table_name == "review_items" or table_name == "books_reviews":
            path = "/mnt/d/study/vldb_demo/demo/chat/data/dlbench/book_reviews.json"
            try:
                result_data = []
                t = 1

                with open(path, 'r') as file:
                    for line in file:
                        try:
                            # 每行是一个独立的 JSON 对象
                            result_data.append(json.loads(line))  # 解析每一行的 JSON 数据
                            t += 1
                            if t > 1000:
                                break
                        except json.JSONDecodeError as e:
                            print(f"JSON Decode Error in line: {line}, error: {e}")
                
                return result_data  # 返回包含所有 JSON 对象的列表

            except Exception as e:
                print(f"Error reading JSON file: {str(e)}")
                return {"error": "Unable to read data"}


        elif table_name == "users" or table_name == "user_relations":
            USER_CSV_PATH = "/mnt/d/study/vldb_demo/demo/chat/data/dlbench/users.csv"
            RELATION_CSV_PATH = "/mnt/d/study/vldb_demo/demo/chat/data/dlbench/user_relations.csv"

            users_df = pd.read_csv(USER_CSV_PATH)
    
            # 读取关系数据
            relations_df = pd.read_csv(RELATION_CSV_PATH)

            # 构建节点列表
            nodes = []
            for _, row in users_df.iterrows():
                nodes.append({
                    "id": int(row["user_id"]), 
                    "label": row["user_name"],
                    "attributes": {
                        "user_id": row["user_id"],
                        "user_name": row["user_name"],
                        "age": row["age"],
                        "gender": row["gender"]
                    }
                })

            # 构建边列表
            edges = []
            for _, row in relations_df.iterrows():
                edges.append({
                    "from": int(row["from_userId"]),
                    "to": int(row["to_userId"]),
                    "relation": row["relation"]
                })

            return {"nodes": nodes, "edges": edges}

        else :
            path = "/mnt/d/study/vldb_demo/demo/chat/data/dlbench/" + table_name + ".csv"

            try :
                result = pd.read_csv(path)
                result = result.fillna("") 
                result = result.to_dict(orient="records")
            except Exception as e:
                result = pd.DataFrame()   
                print(f"error : {str(e)}")


        return result
