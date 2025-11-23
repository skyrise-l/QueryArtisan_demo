
import os
from ..config.config import *
from ..openai.my_api import *
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import torch
import sqlite3
from collections import defaultdict
from heapq import nlargest
import time

reinforce_recommend = False

class chatRecommend:
    def __init__(self, access_tokens, model_loader):
        self.token_key = access_tokens[0]  # Assuming access_tokens is a list
        self.model_loader = model_loader

    def fetch_table_columns_from_db(self, cursor):
        cursor.execute("""
        SELECT database_name, table_name, column_name
        FROM table_metadata
        """)
        result = cursor.fetchall()
        
        tables = {}
        for row in result:
            db_name, table_name, column_name = row
            if db_name not in tables:
                tables[db_name] = {}
            if table_name not in tables[db_name]:
                tables[db_name][table_name] = []
            tables[db_name][table_name].append(column_name)
        return tables

    def load_column_embeddings(self, file_path):
        """Load the column embeddings from a file"""
        if os.path.exists(file_path):
            embeddings = np.load(file_path, allow_pickle=True).item()  # Assuming embeddings are saved as a dictionary
            print(f"Embeddings loaded from {file_path}")
            return embeddings
        else:
            print(f"No embeddings found at {file_path}")
            return {}

    def get_query_embedding(self, query):
        """Generate the BERT embedding for the given query"""
        tokenizer = self.model_loader.get_tokenizer()
        model = self.model_loader.get_model()

        inputs = tokenizer(query, return_tensors='pt', truncation=True, padding=True)
        with torch.no_grad():
            outputs = model(**inputs)
        return outputs.last_hidden_state.mean(dim=1).squeeze().numpy()

    def extract_keywords_from_query(self, query):

        keywords = query.lower().split()
        return keywords

    def get_table_column_embeddings(self, tables):
        """Given tables and columns, load their embeddings"""
        embeddings = {}
        for (db_name, table_name), columns in tables.items():
            embeddings[(db_name, table_name)] = []
            for column_name, column_embedding in columns:
                embeddings[(db_name, table_name)].append((column_name, column_embedding))
        return embeddings

    def find_related_tables(self, query, tables):
        """Find related tables and columns based on the query"""
        table_column_embeddings = self.get_table_column_embeddings(tables)
        query_keywords = self.extract_keywords_from_query(query)

        query_keywords_embeddings = []
        for keywords in query_keywords:
            query_keywords_embeddings.append(self.get_query_embedding(keywords))

        # 用于存储表的相关分数
        table_scores = defaultdict(float)

        # 对每个关键词计算和所有列的相似度
        for keyword, keyword_embedding in zip(query_keywords, query_keywords_embeddings):
            column_similarity_scores = {}

            # 对每个表的列计算相似度
            for (db_name, table_name), columns in table_column_embeddings.items():
                for column_name, column_embedding in columns:
                    score = cosine_similarity([keyword_embedding], [column_embedding])[0][0]
                    if (db_name, table_name, column_name) not in column_similarity_scores:
                        column_similarity_scores[(db_name, table_name, column_name)] = []

                    column_similarity_scores[(db_name, table_name, column_name)].append(score)

            # 排序并取前5个相关列
            top_columns_per_keyword = {}
            for (db_name, table_name, column_name), scores in column_similarity_scores.items():
                avg_score = sum(scores) / len(scores)  # 计算平均相似度
                top_columns_per_keyword[(db_name, table_name, column_name)] = avg_score

            # 获取当前关键词前5个最相关列
            top_5_columns = nlargest(5, top_columns_per_keyword.items(), key=lambda item: item[1])

            # 累加相关列分数到每个表
            for (db_name, table_name, column_name), avg_score in top_5_columns:
                table_scores[(db_name, table_name)] += avg_score  # 将该列的分数加到对应表上

        # 排序表，得到与整个查询最相关的表
        sorted_tables = sorted(table_scores.items(), key=lambda item: item[1], reverse=True)

        return sorted_tables
    
    def find_related_queries(self, query, history_queries):
        related_queries = {}

        query_embeddings = self.get_query_embedding(query)

        for queries_id, query_data in history_queries.items():
            for db_id, query, embedding in query_data:

                # 计算余弦相似度
                score = cosine_similarity([query_embeddings], [embedding])[0][0]
                related_queries[query] = score

        sorted_related_queries = sorted(related_queries.items(), key=lambda x: x[1], reverse=True)[:3]

        # 提取并返回查询列表（不包括得分）
        return [query for query, score in sorted_related_queries]

    def recommend(self, query, column_file_path, query_file_path):
        # Load the column embeddings
        column_embeddings = self.load_column_embeddings(column_file_path)
        query_embeddings = self.load_column_embeddings(query_file_path)

        if not column_embeddings and not query_embeddings:
            return []

        try:
            db_path = DATA_SQLITE_PATH
            connection = sqlite3.connect(db_path)
            cursor = connection.cursor()
            # Fetch table columns from the database
            tables = self.fetch_table_columns_from_db(cursor)

            related_queries = self.find_related_queries(query, query_embeddings)

            if not related_queries:
                return ["No suggestions available"]

            if reinforce_recommend:
                all_related_data = {}
                related_tables = self.find_related_tables(query, column_embeddings)
                for (db_name, table_name), score in related_tables:
                    if db_name in tables and table_name in tables[db_name]:
                        # 获取表的完整数据
                        table_data = tables[db_name][table_name]
                        all_related_data[(db_name, table_name)] = table_data
                ai_agent = OpenAIAgent("recommned", self.token_key)

                prompt =  "I would like you to generate 5 user query suggestions based on the current query’s partial input, the relevant data I retrieved, and the potential historical related queries. The output format should be 5 queries, each on a new line."
                prompt += "Relevant data:"
                for (db_name, table_name), score in related_tables:
                    prompt += (db_name, table_name) 
                    prompt += all_related_data[(db_name, table_name)]

                prompt += "Possible historical queries:"
                for query in related_queries:
                    prompt += query

                ai_recmommend = ai_agent.temporary_talk(prompt)
                return ai_recmommend.splitlines()

            connection.close()

        except Exception as e:
            print(f"Error connecting to database: {e}")
            related_queries = ["No suggestions available"]

        return related_queries


    def taskRecommend(self, user_query):
        ai_agent = OpenAIAgent("recommned", self.token_key)

        prompt =  "I am providing usage recommendations for an AI data analysis and visualization Settings for a current data lake query and analysis system. The suggestions should be based on user input (which should include the user's task requirements and possibly some specified details)."

        prompt += "Currently, the basic tasks and tools for the data lake are as follows:"
        prompt += """
Setting	Value Limit Reason 

In addition, there are analytical tools that can be expanded at will, such as:
Setting	Value Limit Reason 
'Clustering Analysis tools'	'K-means Plotly' 'None' "Suitable for unsupervised learning, data visualization display"

Now, based on the user's input, you need to recommend the corresponding tasks and their attributes. The output should start with a judgment in the first line (for cases where the input is unclear). For example, if the user inputs: "I want to perform a normal query and clustering analysis," the output should be:
I understand your request. Here are my recommendations:
'Max tokens' 16384 'None' 'default'

Clustering Analysis, K-means, Plotly, "Suitable for unsupervised learning and data visualization"

If the input is unclear, the output should be:
I don't understand your request. Please try to clarify your needs. Below are the default settings:


Current user's input:
        """
        prompt += user_query

        default_tasks = [
            {"setting": "Model Select", "value": "GPT-3.5-turbo-16k", "reason": "System Default"},
            {"setting": "Task Mode", "value": "CombinedAnalysis", "reason": "System Default"},
            {"setting": "Max token", "value": 16384, "reason": "System Default"},
            {"setting": "Temperature", "value": 1, "reason": "System Default"},
            {"setting": "System Prompt", "value": "Default mode", "reason": "System Default"}
        ]
        analysis_tasks = [
            {"setting": "Clustering Analysis", "value": "K-means + Plotly", "reason": "Suitable for unsupervised learning and data visualization"},
        ]
        '''
        # Check if the model's response suggests clarification or default settings
        judgment = "Unclear input. Please clarify your needs. Below are the default settings:"  # Default fallback judgment
        task_recommendations = default_tasks  # Default tasks list
      
        ai_recmommend = ai_agent.temporary_talk(prompt)

        if "don’t understand" in ai_recmommend or "clarify" in ai_recmommend or "default settings" in ai_recmommend:
            # If the model indicates misunderstanding or needs clarification
            judgment = "I don't understand your request. Please clarify your needs. Below are the default settings:"
            task_recommendations = default_tasks
        elif "understand" in ai_recmommend:
            # If the model confirms it understands
            judgment = "I understand your request. Here are my recommendations:"
            
            # Extract the task recommendations (everything after the first line)
            task_lines = ai_recmommend.splitlines()[1:]  # Skip the first line (judgment)
            
            # Process tasks from the second line onwards
            task_recommendations = self.extract_task_recommendations(task_lines, default_tasks + analysis_tasks)
        else:
            # If the response is neither clear nor asking for clarification
            judgment = "Model did not provide a clear judgment. Please check the response."
            task_recommendations = default_tasks
        
        '''

        judgment = "I understand your request. Here are my recommendations:"  # Default fallback judgment
        task_recommendations = default_tasks  # Default tasks list

        time.sleep(1)
        # Return result as a dictionary
        result = {
            "judgment": judgment,
            "task_recommendations": task_recommendations #+ analysis_tasks,
        }
        
        return result
    
    def extract_task_recommendations(self, task_lines, all_tasks):
        """
        Extract and deduplicate task recommendations based on the lines returned by the model.
        """
        tasks_set = {}
        for line in task_lines:
            # Try to match each line to a task format
            for task in all_tasks:
                if task["task"] in line:
                    tasks_set[task["task"]] = task  # Deduplicate by task name
        
        # Return the list of tasks after deduplication
        return list(tasks_set.values())
    

