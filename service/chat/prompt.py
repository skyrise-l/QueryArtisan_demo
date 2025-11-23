import sqlite3
import os
from ..utils.process_util import process_util
from .preprocessing import preprocessing
from .query_deconstruct import query_deconstruct


decompose_prompt = '''
Now start the target task:
Help me decompose the following user input into several query requirements and several analysis requirements, with one requirement per line (there may be no query requirements or analysis requirements; in very simple cases, there may be only one line of query requirements). Format as follows:
decompose_query:
XXXX
XXXX
decompose_analysis:
XXXX
Here's an example:
Input:
Find books reviewed by users Mike follows or likes. Calculate the total number of reviews and the average rating from his friends. If Mike has read these books, retrieve his ratings as well. Then, analyze whether Mike's book preferences align with his social circle's ratings and review patterns.
Response:
decompose_query:

Identify the user named "Mike," then retrieve the IDs of all users whom Mike follows or likes.
Calculate the total number of reviews for each book found in Subquery 1.
Compute the average rating and review count for each book from the users identified in Subquery 1.

decompose_analysis:

Analyze if Mike's social circle has unique book review preferences.

Note: "Subquery 1" refers to the result of the first line in decompose_query.
Now here's the current input:

'''

json_prompt = '''
This data structure is in JSON File, but JSONL format, each line is a separate JSON object, the book_reviews.json every line meta-structure example:
{"book_id": 10, "feedback": 4.7, "review_num": 87, "review": [{"id": 31, "review_time": "2018/12/25", "book_id": 10, "user_id": 26.0, "user_name": "hamor0121_fok8n1", "score": 5}, ....]}
"review" is a substructure

detail information follow:
'''

graph_prompt = '''
This data structure is a graph, but is actually stored in CSV format, no different from tables
'''


optimization_anaysis_prompt  = '''
I will provide you with two logical plans (before and after optimization), where the second one is the optimized version, a
nd the execution time for converting it to a specific execution plan is known. Please try to estimate the performance changes before and after this optimization. 
Output the following content in JSON format, where estimatedTimeBefore is the execution time before optimization, while timeImprovement, cpuUsageReduction, etc. are all percentages. 
The three points in optimizationPoints are fixed, but the impact can be 'approximately 0%':
{
  "estimatedTimeBefore": "Xs",
  "cpuUsageReduction": "X%",
  "memoryUsageReduction": "X%",
  "optimizationPoints": [
    {
      "point": "Pushdown of filters or projections",
      "impact": "approximately X%"
    },
    {
      "point": "Elimination of unnecessary data loading or transformation",
      "impact": "approximately X%"
    },
    {
      "point": "Reordering of operations to reduce intermediate data size",
      "impact": "approximately X%"
    }
  ]
}
'''



def get_data_prompt():
    db_file = "/mnt/d/study/vldb_demo/demo/chat/data/dataset_metadata_query_use.db"
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    # 修正SQL查询，添加引号和ORDER BY
    cursor.execute("SELECT * FROM table_metadata WHERE database_name = 'dlbench' ORDER BY table_name, column_name")
    
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        return "No data found for dlbench database."
    
    # 获取列名（用于索引）
    column_names = [desc[0] for desc in cursor.description]
    
    # 按表名分组
    tables_data = {}
    table_type = {}
    for row in rows:
        row_dict = dict(zip(column_names, row))
        table_name = row_dict['table_name']
        
        if table_name not in tables_data:
            tables_data[table_name] = []
        
        table_type[table_name] = row_dict['table_type']
        # 忽略ret_pks和ret_fks，构建列信息
        column_info = {
            'column_name': row_dict['column_name'],
            'data_format': row_dict['data_format'],
            'primary_key': row_dict['primary_key'],
            'foreign_key': row_dict['foreign_key'],
            'csv_path': row_dict['csv_path'],
            'des': row_dict['des']
        }
        tables_data[table_name].append(column_info)
    
    # 构建prompt
    prompt_parts = ["Here is the schema information for the target database, data type may:table;json;graph :"]
    
    for table_name, columns in tables_data.items():
        prompt_parts.append(f"\ndata: {table_name}")
        prompt_parts.append("Columns:")

        if columns[0]['csv_path']:
            prompt_parts.append(f" (Data source path: {columns[0]['csv_path']})")

        if table_type[table_name] == "json":
            prompt_parts.append("Type: json")
            prompt_parts.append(json_prompt)

        elif table_name == "graph":
            prompt_parts.append("Type: graph")
            prompt_parts.append(graph_prompt)
        else:
            prompt_parts.append("Type:table")
        
        for col in columns:
            column_desc = f"  - {col['column_name']}"
            
            # 添加数据类型信息
            if col['data_format']:
                column_desc += f", Format: {col['data_format']}"
            
            # 添加主键信息
            if col['primary_key'] and col['primary_key'].strip():
                column_desc += f" [Primary Key: {col['primary_key']}]"
            
            # 添加外键信息
            if col['foreign_key'] and col['foreign_key'].strip():
                column_desc += f" [Foreign Key: {col['foreign_key']}]"
            
            # 添加描述信息
            if col['des'] and col['des'].strip():
                column_desc += f" - {col['des']}"
            
            prompt_parts.append(column_desc)
    
    return "\n".join(prompt_parts)


def get_logical_plan_prompt(query, decompose_query, data_prompt):

    example = process_util.get_example()
    
    preprocessing_Instant = preprocessing(1, False)
        
    project_define = preprocessing_Instant.get_define(example)

    prompt = project_define + "## 2. Now for the second step, I will provide you with all the data information that you may need for this data analysis.\n" + data_prompt
    
    query_deconstruct_Instant = query_deconstruct()

    query_deconstruct_define = query_deconstruct_Instant.get_define(query, decompose_query, prompt)

    return query_deconstruct_define


def get_phycial_plan_prompt(hash_query, query, opt_logical_plan, data_prompt):

    message = "Now, please generate corresponding Python code based on the logical plan\n"

    message += "user query:" + query + "the logical plan:" + opt_logical_plan + "The data format" + data_prompt + "\n And along with specific requirements:"

    message += "(1) Ensure that all code is within the same context.\n"

    message += "(2) Note that for JSON/JSONL data files, parsing is usually required. Choose the appropriate method based on your file format:"

    message += '''
        # For JSONL files (each line is a separate JSON object):
        # Alternative: Direct processing for JSONL (more memory efficient for large files):
        books_data = []
        reviews_data = []

        with open('data.jsonl', 'r', encoding='utf-8') as f:
            for idx, line in enumerate(f, 1):
                line = line.strip()
                if line:
                    item = json.loads(line)
                    
                    # Extract book review info
                    books_data.append({
                        'id': idx,
                        'book_id': item['book_id'], 
                        'feedback': item['feedback'], 
                        'review_num': item['review_num']
                    })
                    
                    # Extract individual reviews
                    for review in item['review']:
                        reviews_data.append({
                            **review, 
                            'book_review_id': idx
                        })

        books_review_df = pd.DataFrame(books_data)
        reviews_items_df = pd.DataFrame(reviews_data)
    '''

    message += "(3) When generating code, please consider that some steps may can be combined. For example, the 'group' operation is often combined with the 'having' operation for conditional filtering on aggregate functions. An example code is as follows:\n"

    message += "Step2 = Step1.groupby('group_column').filter(lambda x: x['value_column'].mean() > value) \n"

    message += "(4) When performing column value comparisons, please pay attention to the types of the relevant columns as indicated in the logical plan. Different comparison code should be employed based on the varying types of columns.\n"

    path = "/mnt/d/study/vldb_demo/demo/chat/result/"+ str(hash_query) + ".txt"
    
    message += "(5) The logical plan's write Operator result path is: '" + path + "'."

    message += "(6) Please generate the Python code using '```python' at the beginning and using '```' at the end for better identification."
    
    message += "(7) \nDon't forget to import the pandas and json library.\n"

    return message

def get_code_analysis_prompt(query, decompose_analysis, code_answner):

    prompt = "I need you to generate query processing code based on the complete user input I provide, the extracted analysis requirements, and the existing query processing code, to implement the analysis requirements, If the requirements do not specify a visualization algorithm, you can freely choose an algorithm for analysis, but be sure to save the visualization images."

    prompt += "For example, similar to the following code:"

    code_example_flle = "/mnt/d/study/vldb_demo/demo/chat/config/example.py"

    with open(code_example_flle, 'r') as file:
        file_content = file.read()

    prompt += file_content

    prompt += "### Now complete user input: " + str(query) + ". The extracted analysis requirements: " + str(decompose_analysis) + ". The existing query processing code" + str(code_answner)

def get_new_opt_prompt(query, decompose_analysis, data_prompt, logical_plan):
    prompt = "For the current user input and parsed query requirements (only need to handle query requirements) below, along with the corresponding generated logical plan, I hope you can optimize it. Specifically, the optimization focus should be on adjusting operation order and merging operations to improve efficiency, Of course, do not change the plan is allowed. For example, you might need to execute filter before join to accelerate queries, or multiple filter operations might be merged, etc. Please provide a new logical plan with the same format. However, please note that the format of each step should remain unchanged, and there are also relevant data structures available for reference"

    prompt += "### Complete user input: " + query + ". The extracted analysis requirements: " + decompose_analysis + ". The data structures" + data_prompt + "\n logical_plan:" + logical_plan

    return prompt


def get_check_code_prompt(query, decompose_query, decompose_analysis, data_prompt, code_answner):
    prompt =  "Please help me check the code for errors based on the query-user requirements-data structure below, and return the complete corrected code."
    prompt += "### Complete user input: " + query + ". The extracted requirements: " + decompose_query  +  decompose_analysis + ". The data structures" + data_prompt + "\n ##check code:" + code_answner

    return prompt   


def get_llm_result_prompt(query, code_content, code_result):

    prompt = "I hope you can provide a report based on the user input, executed code, and code execution results that I give you. If the code involves visualization content, please also provide explanations. The format can follow the example below."

    prompt += '''
        For your query requesy, All the results have been given.
        For your analysis request(if the code include), I have attempted to generate a bubble chart and a density plot for the analysis. Below is the analysis report:
        Chart 1: Bubble Chart Analysis
        The bubble chart shows the relationship between Mike's ratings and his social circle (friends) average ratings:

        X-axis: Mike's rating for the book.
        Y-axis: The average rating from Mike's friends.
        Bubble size: Represents the number of reviews, with larger bubbles indicating more reviews.
        Color: Indicates the difference between friends' ratings and platform ratings. Blue means friends rated higher than platform, red means lower, and green indicates consistency.
        From the chart, we can see that Mike's ratings are usually close to his social circle's ratings, but there are some deviations, especially for books with fewer reviews. The overall trend shows that Mike tends to align with his social circle, and books with more reviews tend to have higher ratings.
    '''

    prompt += "user input" + str(query) + "\n code_content: "+ str(code_content) + "\n code_result: " + str(code_result)

    return prompt


def get_command_prompt(query_id, current_query, code_content, data_format):
    prompt = "First, there is already an existing user input and corresponding executed code. Now the user has a follow-up input, " \
    "and you are required to generate new code based on the data structure and existing code. " \
    "If it's a visualization command input, you may need to continue writing based on the previous code to form new complete code, " \
    f"or you may need to generate entirely new code. In any case, you are required to output executable and complete code. You should save all visualization images to the specified directory '/mnt/d/study/vldb_demo/demo/chat/data/dlbench/' and prefix the filenames with {query_id}" \
    
    prompt += "existing  user input:" + current_query + "\n data structure" + data_format + "\n existing code:" + code_content

    return prompt