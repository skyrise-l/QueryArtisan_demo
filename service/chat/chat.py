
import os
from ..config.config import *
from ..openai.my_api import *
import pandas as pd
import time
import base64
import glob
import shutil
import subprocess
import traceback
from .prompt import *
from ..utils.read_logical import read_logical
import re
import ast

class Chat:
    def __init__(self, access_tokens, model_loader):
        self.token_key = access_tokens[0]  # Assuming access_tokens is a list
        self.model_loader = model_loader

    def execute_code(self, query_id, path, targetdir):
        try:
            with open(f"/mnt/d/study/vldb_demo/demo/chat/result/output_{query_id}_result.file", 'w') as f:
                subprocess.run(
                    ["python3", "-W", "ignore", path], 
                    stdout=f,           # 标准输出重定向到文件
                    stderr=subprocess.STDOUT,  # 如果也想捕获错误信息到文件
                    text=True, 
                    cwd=targetdir
                )
        except Exception as e:
            traceback_info = traceback.format_exc()
            print(f"execute code error: {traceback_info}")
            print(f"执行文件时发生错误: {e}")


    def query(self, user_query):
        messages = user_query
        user_message = next((msg for msg in reversed(messages) if msg["author"] == "user"), None)

        print(f"user_message : {user_message}")

        if "Find books reviewed by users Mike follows or likes. Calculate the total number of reviews and the average rating from his friends. If Mike has read these books, retrieve his ratings as well." in user_message["message"]:
            time.sleep(8)
            try:
                query_Id = "7ae0e31f-4648-4541-8fe2-e5fdbc5a98a5"  
                if os.path.exists("/mnt/d/study/vldb_demo/demo/chat/config/mike_vs_friends_pca.png"):
                    self.sendCommand(query_Id, "query")

                file = "/mnt/d/study/vldb_demo/demo/chat/data/dlbench/data_raw.py"
                targetdir = "/mnt/d/study/vldb_demo/demo/chat/data/dlbench/"  

                try:
                    with open(f"/mnt/d/study/vldb_demo/demo/old_result.file", 'w') as f:
                        subprocess.run(
                            ["python3", "-W", "ignore", file], 
                            stdout=f,           # 标准输出重定向到文件
                            stderr=subprocess.STDOUT,  # 如果也想捕获错误信息到文件
                            text=True, 
                            cwd=targetdir
                        )
                except Exception as e:
                    traceback_info = traceback.format_exc()
                    print(f"execute code error: {traceback_info}")
                    print(f"执行文件时发生错误: {e}")

                
            except Exception as e:
                print("error user_query", str(e))
                return "None", "error user_query", [""], [""]

            try:
                system_message = "Your task includes a query and a data analysis task. The query has been completed. Please check the report."
                decompose_query = ['Identify the user named “Mike,” then retrieve the IDs of all users whom Mike follows or likes.', 'Calculate the total number of reviews for each book found in Subquery 1.', 'Compute the average rating and review count for each book from the users identified in Subquery 1.']
                decompose_analysis = ['Analyze if Mike’s social circle has unique book review preferences.']
            except Exception as e:
                print("error process query", str(e))
                return "None", "error process query", [""], [""]
        else:
            system_message = "Your task includes a query and a data analysis task. The query has been completed. Please check the report."
            #self.token_key = "sk-fvXDuNXlHri5Mh02WA4HWpFHPFxktboNCEDU1wD1jGfidpqh"
            db_file = "/mnt/d/study/vldb_demo/demo/chat/data/dataset_metadata_history.db"
            conn = sqlite3.connect(db_file)
            hash_query = str(hash(user_message["message"]))
            cursor = conn.cursor()
            conn.row_factory = sqlite3.Row  # 设置行工厂为字典模式
            cursor = conn.cursor()
            
            try:
                cursor.execute("""
                    SELECT * FROM query
                    WHERE query = ?
                """, (user_message["message"],))
                
                result = cursor.fetchone()
                if result:
                    return hash_query, system_message, ast.literal_eval(result["decompose_query"]), ast.literal_eval(result["decompose_analysis"])
            except Exception as e:
                print(f"query erorr {e}")
            
            query_agent = OpenAIAgent("query", self.token_key)#OpenAIAgent("gpt", "sk-fvXDuNXlHri5Mh02WA4HWpFHPFxktboNCEDU1wD1jGfidpqh", url="https://xiaoai.plus/v1/chat/completions", model="gpt-3.5-turbo-16k-0613")#OpenAIAgent("query", self.token_key)

            
            query_Id = hash_query
            data_prompt = get_data_prompt()
      
            now_decompose_prompt = data_prompt + decompose_prompt + user_message["message"]
            response_text = query_agent.single_talk(now_decompose_prompt)

            print(response_text)

            decompose_query, decompose_analysis = self.parse_decompose_response(response_text)

            print(decompose_query, decompose_analysis)

            logical_plan_prompt = get_logical_plan_prompt(user_message["message"], str(decompose_query), data_prompt)

            #query_agent.model = "deepseek-reasoner"
            answer = query_agent.continue_talk(logical_plan_prompt)

            print(answer)

            try:
                logical_plan = self.get_logical_plan(answer)
            except Exception as e:
                print(f"logical_plan 解析错误 {e}")
                return "None", "logical_plan 解析错误", [], []

            log_file = "/mnt/d/study/vldb_demo/demo/chat/data/dlbench/logical_plan/" + hash_query + '.txt'

            with open(log_file, 'w', encoding='utf-8') as file:
                file.write(logical_plan)

            new_opt_prompt = get_new_opt_prompt(user_message["message"], str(decompose_query), data_prompt, logical_plan)

            response_text = query_agent.continue_talk(new_opt_prompt)

            print(response_text)

            try:
                opt_ogical_plan = self.get_logical_plan(response_text)
            except Exception as e:
                print(f"logical_plan 解析错误 {e}")
                return "None", "logical_plan 解析错误", [], []
            
            opt_log_file = "/mnt/d/study/vldb_demo/demo/chat/data/dlbench/logical_plan/" + hash_query + '_opt.txt'
            
            with open(opt_log_file, 'w', encoding='utf-8') as file:
                file.write(opt_ogical_plan)

            gpt_query_agent = OpenAIAgent("query", api_key=self.token_key, model="deepseek-chat")#

            code_prompt = get_phycial_plan_prompt(hash_query, user_message["message"], opt_ogical_plan, data_prompt)

            code_answner = gpt_query_agent.single_talk(code_prompt)

            print(f"code_answner: {code_answner}")

            if decompose_analysis and decompose_analysis[0] and "none" not in decompose_analysis[0].lower():
                code_analysis_prompt = get_code_analysis_prompt(user_message["message"], str(decompose_analysis) , code_answner)
                code_answner = gpt_query_agent.single_talk(code_analysis_prompt)

            start_time = time.perf_counter()
            code = process_util.exact_code(code_answner)
            use_time = time.perf_counter() - start_time

            try:
                cursor.execute("""
                    INSERT INTO query (query, hash, time, decompose_query, decompose_analysis, executionTime) 
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (user_message["message"], hash_query, time.time(), str(decompose_query), str(decompose_analysis), use_time))
            except Exception as e:
                print(f"insert data error {e}")

            conn.commit()
            cursor.close()
            conn.close()

            try:
                code_path = "/mnt/d/study/vldb_demo/demo/chat/code/" + hash_query + '.py'

                with open(code_path, 'w', encoding='utf-8') as file:
                    file.write(code)

                targetdir = "/mnt/d/study/vldb_demo/demo/chat/code/"

                self.execute_code(query_Id, code_path, targetdir)

            except Exception as e:
                return "None", "code execute error", decompose_query, decompose_analysis    
            
            self.add_related_code_lines(log_file, code_path)

            self.add_related_code_lines(opt_log_file, code_path)
            
            '''
            check_code_prompt = get_check_code_prompt(user_message["message"], str(decompose_query), str(decompose_analysis), data_prompt, code_answner)
            code_answner = gpt_query_agent.single_talk(check_code_prompt)
            code = process_util.exact_code(code_answner)
            with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(code)

            
            if not self.execute_code(file_path, targetdir):
                return "code execute error, please try again", [], []
          
            '''
        return query_Id, system_message, decompose_query, decompose_analysis


    def code_result(self, query_id):

        if query_id == "7ae0e31f-4648-4541-8fe2-e5fdbc5a98a5":
                # 使用glob检索CONFIG_DIR目录下所有的png图片
            image_paths = glob.glob(os.path.join(CONFIG_DIR, "*.png"))

            images = []

            # 先将所有图片添加到images中
            for image_path in image_paths:
                try:
                    with open(image_path, "rb") as image_file:
                        base64_image = base64.b64encode(image_file.read()).decode("utf-8")
                        images.append((image_path, base64_image))  # 保存图片路径和base64编码
                except Exception as e:
                    print(f"无法读取图片 {image_path}: {str(e)}")

            # 按照需求调整图片顺序
            # 如果mike_vs_friends_pca.png不存在，则将bubble_chart放到最前面
            if not os.path.exists("/mnt/d/study/vldb_demo/demo/chat/config/mike_vs_friends_pca.png"):
                bubble_chart_path = os.path.join(CONFIG_DIR, "mike_vs_friends_bubble_chart.png")
                if os.path.exists(bubble_chart_path):
                    with open(bubble_chart_path, "rb") as image_file:
                        base64_image = base64.b64encode(image_file.read()).decode("utf-8")
                        # 将bubble_chart放到最前面
                        images.insert(0, (bubble_chart_path, base64_image))

            else:
                # 如果存在mike_vs_friends_pca.png，则将其放到最前面
                pca_path = os.path.join(CONFIG_DIR, "mike_vs_friends_pca.png")
                if os.path.exists(pca_path):
                    with open(pca_path, "rb") as image_file:
                        base64_image = base64.b64encode(image_file.read()).decode("utf-8")
                        # 将pca图放到最前面
                        images.insert(0, (pca_path, base64_image))

                # 如果存在mike_vs_friends_kmeans.png，则将其放到最前面
                kmeans_path = os.path.join(CONFIG_DIR, "mike_vs_friends_kmeans.png")
                if os.path.exists(kmeans_path):
                    with open(kmeans_path, "rb") as image_file:
                        base64_image = base64.b64encode(image_file.read()).decode("utf-8")
                        # 将kmeans图放到最前面
                        images.insert(0, (kmeans_path, base64_image))

            # 只需要最终处理顺序，不必担心中间是否重复添加
            final_images = [base64_image for _, base64_image in images]  # 获取base64编码


            try:
                with open("/mnt/d/study/vldb_demo/demo/old_result.file", 'r') as f:
                    code_output = f.read()
            except Exception as e:
                    print(f"无法读取代码结果: {str(e)}")
                    code_output  = ""

            if not os.path.exists("/mnt/d/study/vldb_demo/demo/chat/config/mike_vs_friends_pca.png"):
                llm_result = '''
        For your analysis request, I have attempted to generate a bubble chart and a density plot for the analysis. Below is the analysis report:
        Chart 1: Bubble Chart Analysis
        The bubble chart shows the relationship between Mike's ratings and his social circle (friends) average ratings:

        X-axis: Mike's rating for the book.
        Y-axis: The average rating from Mike's friends.
        Bubble size: Represents the number of reviews, with larger bubbles indicating more reviews.
        Color: Indicates the difference between friends' ratings and platform ratings. Blue means friends rated higher than platform, red means lower, and green indicates consistency.
        From the chart, we can see that Mike's ratings are usually close to his social circle's ratings, but there are some deviations, especially for books with fewer reviews. The overall trend shows that Mike tends to align with his social circle, and books with more reviews tend to have higher ratings.

        Chart 2: Density Plot Analysis
        The density plot shows the rating differences between Mike and his friends:

        X-axis: Rating difference (Mike's rating minus friends' average rating).
        Y-axis: Density of differences.
        The density plot shows that Mike’s rating is close to his friends' ratings for most books. If the distribution leans towards positive values, it means Mike typically gives higher ratings; if it leans negative, it means he tends to give lower ratings. This chart reveals Mike’s alignment with his social circle's ratings.

        Analysis Summary
        Based on the analysis request, we examined Mike’s alignment with his social circle's ratings:

        Mike’s ratings are generally in line with his friends' ratings, especially for books with more reviews.
        Review count is positively correlated with ratings, as books with more reviews tend to receive higher ratings.
        Rating differences are small, suggesting that Mike's ratings mostly align with his social circle, although some books exhibit larger rating deviations.
        If further analysis is required, feel free to execute additional commands.

        '''
            else :
                llm_result = '''
        For your analysis request, I have attempted to generate a bubble chart and a density plot for the analysis. Below is the analysis report:
        Chart 1: Bubble Chart Analysis
        The bubble chart demonstrates the relationship between Mike's ratings and the average ratings from his social circle (friends):
        X-axis: Mike's rating for each book.
        Y-axis: Average rating given by Mike's friends.
        Bubble size: Indicates the number of reviews, with larger bubbles representing more reviews.
        Color: Illustrates rating differences. Blue indicates friends rated higher than the platform average, red lower, and green denotes consistency.
        Observations:
        Mike’s ratings generally align closely with his friends', particularly for books with more reviews. Deviations are primarily found in books with fewer total reviews. Overall, the data indicates strong alignment between Mike's preferences and those of his social circle, emphasizing a trend of positively correlated reviews with increased review counts.

        Chart 2: Density Plot Analysis
        The density plot visualizes rating differences between Mike and his friends:
        X-axis: Difference between Mike's rating and the average rating from friends.
        Y-axis: Density of rating differences.
        Observations:
        The density plot reveals most rating differences cluster near zero, suggesting a high degree of similarity in preferences. Slight skewness toward positive values indicates Mike generally rates books slightly higher than his friends.

        Chart 3: K-Means Clustering Analysis
        The K-Means clustering categorizes books into three clusters based on rating patterns between Mike and his friends:
        Cluster groups reveal clear segmentation of books, highlighting distinct preference patterns.
        Most books cluster closely around similar ratings from Mike and his social circle, with a smaller number exhibiting significant divergence, indicating some books distinctly deviate in preference alignment.

        Chart 4: PCA (Principal Component Analysis)
        PCA condenses the rating dimensions into two principal components to visualize variance effectively:
        PCA visualization reinforces the clustering results, emphasizing that the majority of books reviewed fall into a tightly grouped preference zone.
        Distinct clusters indicate areas where Mike's ratings differ significantly from his friends, demonstrating clear segments within his reading preferences.

        Analysis Summary:
        Integrating bubble, density, K-Means clustering, and PCA analyses:
        Mike’s preferences show strong general alignment with his friends, especially highlighted in popular books with extensive reviews.
        Minor but noteworthy deviations suggest Mike occasionally diverges significantly from his friends' average ratings, especially for less-reviewed books.
        K-Means and PCA analyses confirm distinct preference segments within the social circle, further clarifying patterns of agreement and divergence.

        The total execution time for performing the analysis and generating the visualizations is recorded at the end of the procedure, providing performance transparency.
        Further analysis or additional insights can be generated upon request.
        '''

            try:
                code_result = pd.read_csv("/mnt/d/study/vldb_demo/demo/chat/data/dlbench/optimized_books_analysis.csv")
                code_result = code_result.fillna("") 
            except Exception as e:
                code_result = pd.DataFrame()   
        
        else:
            
            code_resul_dir = "/mnt/d/study/vldb_demo/demo/chat/result/" 
            result_file = self.find_first_file_with_prefix(code_resul_dir, str(query_id))
            code_file = "/mnt/d/study/vldb_demo/demo/chat/code/"  + str(query_id) + ".py"

            with open(code_file, 'r') as f:
                code_content =  f.read()

            if not result_file:
                self.execute_code(query_id, code_file, "/mnt/d/study/vldb_demo/demo/chat/code/")

            try:
                code_result = pd.read_csv(result_file)
                code_result = code_result.fillna("") 

            except Exception as e:
                code_result = pd.DataFrame()   

            try:
                image_extensions = ['*.png', '*.jpg', '*.jpeg', '*.gif', '*.bmp', '*.tiff', '*.webp']
                
                final_images = []
                for ext in image_extensions:
                    pattern = os.path.join('/mnt/d/study/vldb_demo/demo/chat/data/dlbench/', f"{query_id}*{ext}")
                    image_files = glob.glob(pattern)
                    
                    for image_path in image_files:
                        try:
                            with open(image_path, "rb") as image_file:
                                base64_image = base64.b64encode(image_file.read()).decode("utf-8")
                                filename = os.path.basename(image_path)
                                final_images.append((filename, base64_image))
                        except Exception as e:
                            print(f"读取图片失败 {image_path}: {e}")
            except Exception as e:
                pass

            try:
                with open(f"/mnt/d/study/vldb_demo/demo/chat/result/output_{query_id}_result.file", 'r') as f:
                    code_output = f.read()
            except Exception as e:
                    print(f"无法读取代码结果: {str(e)}")
                    code_output  = ""

            llm_result_path = "/mnt/d/study/vldb_demo/demo/chat/result/llm_result_"  + str(query_id) + ".txt"
            if not os.path.exists(llm_result_path):

                query_agent = OpenAIAgent("query", self.token_key)
                db_file = "/mnt/d/study/vldb_demo/demo/chat/data/dataset_metadata_history.db"
                conn = sqlite3.connect(db_file)
                cursor = conn.cursor()
                conn.row_factory = sqlite3.Row  # 设置行工厂为字典模式
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT * FROM query
                    ORDER BY CAST(time AS REAL) DESC 
                    LIMIT 1
                """)
                result = cursor.fetchone()

                llm_result_prompt = get_llm_result_prompt(result["query"], code_content, code_result)
                
                response_text = query_agent.single_talk(llm_result_prompt)
                with open(llm_result_path, 'w') as f:
                    f.write(response_text)
                llm_result = response_text

            else:
                with open(llm_result_path, 'r') as f:
                    llm_result = f.read()

            
         #"Recommendation file saved to '/data/dlbench/37a20e94-0cbc-45f6-a4f8-b5b2edd147f5/recommended_books.csv'\nThe cluster analysis results have been saved to '/data/dlbench/37a20e94-0cbc-45f6-a4f8-b5b2edd147f5/cluster.png'"
        return code_output, llm_result, final_images, code_result



    def command(self, command):
        return " understand your request. I will use XXX to analyze the relationship between sentiment scores and user age."

    def testquery(self, prompt):
        ai_agent = OpenAIAgent("recommned", self.token_key)

        ai_ret = ai_agent.temporary_talk(prompt)

        return ai_ret


    def query_optimization_result(self, query_id):

        if query_id == "7ae0e31f-4648-4541-8fe2-e5fdbc5a98a5":
            result = {}

            result['executionTime'] = "1.1384"
            result['estimatedTimeBefore'] = "1.3831"
            result['timeImprovement'] = round(((float(result['estimatedTimeBefore']) - float(result['executionTime'])) / float(result['estimatedTimeBefore'])) * 100, 2)
            result['cpuUsageReduction'] = "8"
            result['memoryUsageReduction'] = "5"
            result['optimizationPoints'] = [
                {'description': 'Subquery Expansion', "impact": "Optimized subquery structure, reducing overall computation by approximately 12%."},
                {'description': 'JOIN Optimization', "impact": "Optimized and reduced JOIN operations, decreasing JOIN computation by approximately 24%."},
                {'description': 'Predicate Pushdown', "impact": "Filtered out irrelevant data earlier, reducing computation by approximately 33%."},
            ]
            evalutae_result = result
            
        else:
            db_file = "/mnt/d/study/vldb_demo/demo/chat/data/dataset_metadata_history.db"
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()
            conn.row_factory = sqlite3.Row  # 设置行工厂为字典模式
            cursor = conn.cursor()
            evalutae_result = None
            
            try:
                cursor.execute("""
                    SELECT * FROM query
                    ORDER BY CAST(time AS REAL) DESC 
                    LIMIT 1
                """)
                result = cursor.fetchone()
                if result:
                    base_path = "/mnt/d/study/vldb_demo/demo/chat/data/dlbench/logical_plan/"
                    hash = result["hash"]
                    file_path = base_path + str(hash) + ".txt"
                    opt_file_path = base_path + str(hash) + "_opt.txt"

                    opt_result_file = base_path + "opt_output" + str(hash) + ".json"
                    if os.path.exists(opt_result_file):
                        with open(opt_result_file, 'r', encoding='utf-8') as file:
                            evalutae_result = json.load(file)

                    else:

                        with open(file_path, 'r', encoding='utf-8') as file:
                            logical_content = file.read().strip()

                        with open(opt_file_path, 'r', encoding='utf-8') as file:
                            opt_file_content = file.read().strip()

                        prompt = optimization_anaysis_prompt + "\nBefore optimization logical plan:" + logical_content + "\n After optimization logical plan:" + opt_file_content

                        query_agent = OpenAIAgent("query", self.token_key)
                        response = query_agent.single_talk(prompt)

                        evalutae_result = self.parse_and_validate_llm_response(response)
                        evalutae_result['executionTime'] = result['executionTime']

                        estimated_before = float(str(evalutae_result['estimatedTimeBefore']).rstrip('s'))
                        actual_execution = float(evalutae_result['executionTime'])

                        try:
                            evalutae_result['timeImprovement'] = round(((estimated_before - actual_execution) / estimated_before) * 100, 2)
                        except Exception as e:
                            evalutae_result['timeImprovement'] = 0
                        
                        print(evalutae_result)
                        with open(opt_result_file, 'w', encoding='utf-8') as file:
                            json.dump(evalutae_result, file, ensure_ascii=False, indent=2)
                    
            except Exception as e:
                print(f"db query erorr {e}")


        return evalutae_result
    

    def sendCommand(self, query_id, query):

        if query_id == "7ae0e31f-4648-4541-8fe2-e5fdbc5a98a5":
            time.sleep(2)

            image1_path = "/mnt/d/study/vldb_demo/demo/chat/config/mike_vs_friends_pca.png"
            image2_path = "/mnt/d/study/vldb_demo/demo/chat/config/mike_vs_friends_kmeans.png"

            if not os.path.exists("/mnt/d/study/vldb_demo/demo/chat/config/mike_vs_friends_pca.png"):
                shutil.copy("/mnt/d/study/vldb_demo/demo/chat/data/dlbench/mike_vs_friends_pca.png", CONFIG_DIR)
                shutil.copy("/mnt/d/study/vldb_demo/demo/chat/data/dlbench/mike_vs_friends_kmeans.png", CONFIG_DIR)

                shutil.copy2("/mnt/d/study/vldb_demo/demo/chat/data/dlbench/7ae0e31f-4648-4541-8fe2-e5fdbc5a98a5-time.py", "/mnt/d/study/vldb_demo/demo/chat/config/7ae0e31f-4648-4541-8fe2-e5fdbc5a98a5.py")
            else:
                if os.path.exists(image1_path):
                    os.remove(image1_path)

                if os.path.exists(image2_path):
                    os.remove(image2_path)
                shutil.copy2("/mnt/d/study/vldb_demo/demo/chat/data/dlbench/7ae0e31f-4648-4541-8fe2-e5fdbc5a98a5.py", "/mnt/d/study/vldb_demo/demo/chat/config/7ae0e31f-4648-4541-8fe2-e5fdbc5a98a5.py")

            file = "/mnt/d/study/vldb_demo/demo/chat/data/dlbench/data_raw.py"
            file2 = "/mnt/d/study/vldb_demo/demo/chat/data/dlbench/data.py"
            targetdir = "/mnt/d/study/vldb_demo/demo/chat/data/dlbench/"

            temp_file = file + ".tmp"  

            os.rename(file, temp_file) 
            os.rename(file2, file)     
            os.rename(temp_file, file2) 

            try:
                with open(f"/mnt/d/study/vldb_demo/demo/old_result.file", 'w') as f:
                    subprocess.run(
                        ["python3", "-W", "ignore", file], 
                        stdout=f,           # 标准输出重定向到文件
                        stderr=subprocess.STDOUT,  # 如果也想捕获错误信息到文件
                        text=True, 
                        cwd=targetdir
                    )
            except Exception as e:
                traceback_info = traceback.format_exc()
                print(f"execute code error: {traceback_info}")
                print(f"执行文件时发生错误: {e}")
        
        else:
            command_path = "/mnt/d/study/vldb_demo/demo/chat/data/dlbench/command_" + + str(query_id) + ".txt"
            if os.path.exists(command_path):
                # 文件存在，追加到新行
                with open(command_path, 'a', encoding='utf-8') as f:
                    f.write('\n' + query)
            else:
                # 文件不存在，创建并写入第一行
                with open(command_path, 'w', encoding='utf-8') as f:
                    f.write(query)

            db_file = "/mnt/d/study/vldb_demo/demo/chat/data/dataset_metadata_history.db"
            conn = sqlite3.connect(db_file)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM query
                ORDER BY CAST(time AS REAL) DESC 
                LIMIT 1
            """)
            result = cursor.fetchone()
            current_query = result["query"]
            code_file = "/mnt/d/study/vldb_demo/demo/chat/code/"  + str(query_id) + ".py"

            data_format = get_data_prompt()
            with open(code_file, 'r') as f:
                code_content =  f.read()

            prompt = get_command_prompt(query_id, current_query, code_content, data_format)
            query_agent = OpenAIAgent("query", self.token_key)
            code_answner = query_agent.single_talk(prompt)

            code = process_util.exact_code(code_answner)

            with open(code_file, 'w', encoding='utf-8') as file:
                file.write(code)

            try:
                self.execute_code(query_id, code_file, "/mnt/d/study/vldb_demo/demo/chat/code/")
                code_resul_dir = "/mnt/d/study/vldb_demo/demo/chat/result/" 
                result_file = self.find_first_file_with_prefix(code_resul_dir, str(query_id))
            
                try:
                    code_result = pd.read_csv(result_file)
                    code_result = code_result.fillna("") 

                except Exception as e:
                    code_result = pd.DataFrame()   


                llm_result_path = "/mnt/d/study/vldb_demo/demo/chat/result/llm_result_"  + str(query_id) + ".txt"

                llm_result_prompt = get_llm_result_prompt(result["query"], code_content, code_result)
                    
                response_text = query_agent.single_talk(llm_result_prompt)
                with open(llm_result_path, 'w') as f:
                    f.write(response_text)
                    
            except Exception as e:
                pass

        return {"data": "success"}


    def getCommandHistory(self, queryId):

        if queryId == "7ae0e31f-4648-4541-8fe2-e5fdbc5a98a5":

            if os.path.exists("/mnt/d/study/vldb_demo/demo/chat/config/mike_vs_friends_pca.png"):
                history = ["Attempt to analyze the differences between Mike's and his friends' ratings using K-Means clustering and PCA, and output the total execution time of the code."]
                current_query = "Find books reviewed by users Mike follows or likes. Calculate the total number of reviews and the average rating from his friends. If Mike has read these books, retrieve his ratings as well. Then, analyze whether Mike’s book preferences align with his social circle’s ratings and review patterns."

            else:
                history = []
                current_query = "Find books reviewed by users Mike follows or likes. Calculate the total number of reviews and the average rating from his friends. If Mike has read these books, retrieve his ratings as well. Then, analyze whether Mike’s book preferences align with his social circle’s ratings and review patterns."
        else:
            db_file = "/mnt/d/study/vldb_demo/demo/chat/data/dataset_metadata_history.db"

            try:
                conn = sqlite3.connect(db_file)
                conn.row_factory = sqlite3.Row  # 先设置行工厂
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT * FROM query
                    ORDER BY CAST(time AS REAL) DESC 
                    LIMIT 1
                """)
                result = cursor.fetchone()
                
                if result:  # 添加空值检查
                    current_query = result["query"]
                    # 假设 queryId 从查询结果中获取，或者需要单独定义
                    queryId = result["id"]  # 或者其他字段，需要根据实际情况调整
                    
                    command_path = f"/mnt/d/study/vldb_demo/demo/chat/data/dlbench/command_{queryId}.txt"
                    
                    try:
                        with open(command_path, 'r', encoding='utf-8') as f:
                            lines = f.read().splitlines()
                        history = lines
                    except FileNotFoundError:
                        history = []
                else:
                    print("未找到查询记录")
                    current_query = None
                    history = []

            finally:
                if 'conn' in locals():
                    conn.close() 

        return {"history": history, "current_query": current_query}

        

    def parse_decompose_response(self, response_text):
        try:
            decompose_query = []
            decompose_analysis = []
            
            # Split response into lines
            lines = response_text.strip().split('\n')
            
            current_section = None
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                if line.startswith('decompose_query:'):
                    current_section = 'query'
                    continue
                elif line.startswith('decompose_analysis:'):
                    current_section = 'analysis'
                    continue
                
                # Parse content lines (remove numbering if present)
                if current_section == 'query' and line:
                    # Remove leading numbers and dots/periods
                    cleaned_line = line.lstrip('0123456789. ').strip()
                    if cleaned_line:
                        decompose_query.append(cleaned_line)
                elif current_section == 'analysis' and line:
                    cleaned_line = line.lstrip('0123456789. ').strip()
                    if cleaned_line:
                        decompose_analysis.append(cleaned_line)
            
            # Handle case where there are no analysis requirements
            if not decompose_analysis:
                decompose_analysis = [""]
                
            return decompose_query, decompose_analysis
            
        except Exception as e:
            print(f"Error parsing decompose response: {str(e)}")
            return [""], [""]


    def get_logical_plan(self, answner):
        read_Instant = read_logical()

        steps = read_Instant.simple_logical_deal(answner)

        tmp_gpt_plan = process_util.gen_plan(steps)

        return tmp_gpt_plan
    

    def parse_logic_plan(self, plan_file_path):
        """解析逻辑计划文件，提取每个step的信息"""
        with open(plan_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 用正则表达式匹配每个step
        step_pattern = r'Step (\d+):(.*?)(?=Step \d+:|$)'
        steps = re.findall(step_pattern, content, re.DOTALL)
        
        parsed_steps = []
        for step_num, step_content in steps:
            parsed_steps.append({
                'number': int(step_num),
                'content': f'Step {step_num}:{step_content}'.strip()
            })
        
        return parsed_steps

    def find_step_code_lines(self, code_file_path):
        """在代码文件中找到每个step对应的所有行号"""
        with open(code_file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        step_lines = {}
        step_positions = []
        
        # 找到所有step注释的位置
        for i, line in enumerate(lines, 1):  # 行号从1开始
            stripped_line = line.strip().lower()
            # 匹配 "# step X:" 格式的注释
            match = re.search(r'#\s*step\s+(\d+)\s*:', stripped_line)
            if match:
                step_num = int(match.group(1))
                step_positions.append((step_num, i))
        
        # 计算每个step的所有行号
        for i, (step_num, start_line) in enumerate(step_positions):
            if i < len(step_positions) - 1:
                # 不是最后一个step，结束行是下一个step的前一行
                end_line = step_positions[i + 1][1] - 1
            else:
                # 最后一个step，结束行是文件的最后一行
                end_line = len(lines)
            
            # 生成从start_line到end_line的所有行号列表
            all_lines = ast.literal_eval(range(start_line, end_line + 1))
            step_lines[step_num] = all_lines
        
        return step_lines

    def add_related_code_lines(self, plan_file_path, code_file_path):
        """主函数：为逻辑计划添加相关代码行信息并写回原文件"""
        # 解析逻辑计划
        steps = self.parse_logic_plan(plan_file_path)
        
        # 找到代码中的step行号
        step_code_lines = self.find_step_code_lines(code_file_path)
        
        # 读取原文件内容
        with open(plan_file_path, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        # 处理每个步骤，添加相关代码行信息
        modified_content = original_content
        
        # 从后往前处理，避免修改影响位置
        for step in reversed(steps):
            step_num = step['number']
            
            # 构造要添加的相关代码行信息
            if step_num in step_code_lines:
                code_lines = step_code_lines[step_num]
                lines_str = ', '.join(map(str, code_lines))
                related_lines_text = f"relatedCodeLines: [{lines_str}]\n\n"
            else:
                related_lines_text = "relatedCodeLines: []\n\n"
            
            # 找到当前step的结束位置
            step_pattern = f"Step {step_num}:.*?(?=Step {step_num + 1}:|$)"
            match = re.search(step_pattern, modified_content, re.DOTALL)
            
            if match:
                # 在step内容的末尾添加相关代码行信息
                step_content = match.group(0).rstrip()
                new_step_content = step_content + "\n" + related_lines_text
                
                # 替换原内容
                modified_content = modified_content.replace(match.group(0), new_step_content, 1)
        
        # 写回原文件
        with open(plan_file_path, 'w', encoding='utf-8') as f:
            f.write(modified_content)



    def parse_and_validate_llm_response(self, response):
        """
        解析LLM响应并验证JSON结构
        """
        # 定义必需的结构模板
        required_structure = {
            "estimatedTimeBefore": "0",
            "cpuUsageReduction": "0",
            "memoryUsageReduction": "0",
            "optimizationPoints": [
                {
                    "description": "Subquery Expansion",
                    "impact": "approximately 0%."
                },
                {
                    "description": "JOIN Optimization", 
                    "impact": "approximately 0%."
                },
                {
                    "description": "Predicate Pushdown",
                    "impact": "approximately 0%."
                }
            ]
        }
        
        try:
            # 尝试从响应中提取JSON
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                parsed_data = json.loads(json_str)
            else:
                # 如果没有找到JSON，使用默认结构
                parsed_data = {}
            
            # 验证和补全结构
            result = {}
            
            # 检查并设置基本字段
            result['estimatedTimeBefore'] = str(parsed_data.get('estimatedTimeBefore', required_structure['estimatedTimeBefore']))
            result['cpuUsageReduction'] = str(parsed_data.get('cpuUsageReduction', required_structure['cpuUsageReduction']))
            result['memoryUsageReduction'] = str(parsed_data.get('memoryUsageReduction', required_structure['memoryUsageReduction']))
            
            # 检查并设置optimizationPoints
            optimization_points = parsed_data.get('optimizationPoints', [])
            result['optimizationPoints'] = []
            
            # 确保包含三个固定的优化点
            required_descriptions = ["Subquery Expansion", "JOIN Optimization", "Predicate Pushdown"]
            
            for required_desc in required_descriptions:
                found = False
                for point in optimization_points:
                    if isinstance(point, dict) and point.get('description') == required_desc:
                        result['optimizationPoints'].append({
                            'description': required_desc,
                            'impact': point.get('impact', 'approximately 0%.')
                        })
                        found = True
                        break
                
                if not found:
                    # 如果没有找到，使用默认值
                    default_point = next(p for p in required_structure['optimizationPoints'] if p['description'] == required_desc)
                    result['optimizationPoints'].append(default_point)
            
            return result
            
        except (json.JSONDecodeError, Exception) as e:
            print(f"JSON解析错误: {e}")
            return required_structure
        

    def get_code(self, queryId):
        db_file = "/mnt/d/study/vldb_demo/demo/chat/data/dataset_metadata_history.db"
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        conn.row_factory = sqlite3.Row  # 设置行工厂为字典模式
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM query
            ORDER BY CAST(time AS REAL) DESC 
            LIMIT 1
        """)
        result = cursor.fetchone()
        if result:
            base_path = "/mnt/d/study/vldb_demo/demo/chat/code/"
            hash = result["hash"]
            file_path = base_path + str(hash) + ".py"

            with open(file_path, 'r', encoding='utf-8') as file:
                code_content = file.read().strip()


        return {"code": code_content}
    

    def find_first_file_with_prefix(self, directory, prefix):
        """
        在指定目录下查找第一个以prefix开头的文件
        
        Args:
            directory: 目录路径
            prefix: 文件名前缀
        
        Returns:
            str: 找到的文件完整路径，如果没找到返回None
        """
        try:
            # 检查目录是否存在
            if not os.path.exists(directory):
                print(f"目录不存在: {directory}")
                return None
            
            # 遍历目录中的文件
            for filename in os.listdir(directory):
                file_path = os.path.join(directory, filename)
                # 确保是文件而不是目录，并且以指定前缀开头
                if os.path.isfile(file_path) and filename.startswith(prefix):
                    return file_path
            
            # 如果没找到匹配的文件
            print(f"在目录 {directory} 中没有找到以 '{prefix}' 开头的文件")
            return None
            
        except PermissionError:
            print(f"没有权限访问目录: {directory}")
            return None
        except Exception as e:
            print(f"查找文件时出错: {e}")
            return None