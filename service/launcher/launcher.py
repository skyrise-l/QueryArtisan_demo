
import json
from http.server import BaseHTTPRequestHandler, HTTPServer

from ..chat.recommend import chatRecommend
from ..chat.chat import  Chat
from ..utils.model_load import BertModelLoader
from ..config.config import *
from ..chat.backend_logical_read import backend_logical_read
from ..chat.dataSource import dataSource

model_loader = BertModelLoader()
model_loader.load_model()


# HTTP 请求处理类
class RequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # 获取请求内容长度
            content_length = int(self.headers['Content-Length'])
            # 读取请求体
            post_data = self.rfile.read(content_length)

            # 尝试解析 JSON 格式数据
            try:
                data = json.loads(post_data)
                path = self.path
                
                if path == '/data-discovery':
                    user_query = data.get('query', '')

                    access_tokens = ['sk-fa9c6c9c60ee4296ac9dbda8b86ad503']
                    recommender  =  chatRecommend(access_tokens, model_loader)
                    column_file_path = COLUMN_EMBEDDINGS_PATH
                    query_file_path = QUERY_EMBEDDINGS_PATH

                    queries = recommender.recommend(user_query, column_file_path, query_file_path)
                    # 设置响应状态码和头部信息
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()

                    # 返回处理后的结果
                    response = {
                        'input_query': user_query,
                        'recommended_queries': queries
                    }
                    self.wfile.write(json.dumps(response).encode())
                
                elif path == '/task-tool-recommend':
                    user_query = data.get('query', '')

                    access_tokens = ['sk-fa9c6c9c60ee4296ac9dbda8b86ad503']
                    recommender  =  chatRecommend(access_tokens, model_loader)

                    taskRecommend = recommender.taskRecommend(user_query)
                    # 设置响应状态码和头部信息
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()

                    # 返回处理后的结果
                    response = taskRecommend
                    self.wfile.write(json.dumps(response).encode())

                elif path == '/query':
           
                    # 步骤: 查询解析
                    access_tokens = ['sk-fa9c6c9c60ee4296ac9dbda8b86ad503']

                    chat = Chat(access_tokens, model_loader)
                    query_id, response_message, decompose_query, decompose_analysis = chat.query(data)


                    # 设置响应状态码和头部信息
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()

                    response = {
                        'response': response_message,
                        'decompose_query': decompose_query,
                        'decompose_analysis': decompose_analysis,
                        'query_Id': query_id
                    }
                    self.wfile.write(json.dumps(response).encode())
                
                elif path == '/command':
                    user_query = data.get('query', '')
                    # 步骤: 查询解析
                    access_tokens = ['sk-fa9c6c9c60ee4296ac9dbda8b86ad503']

                    chat = Chat(access_tokens, model_loader)
                    response_message = chat.query(user_query)

                    # 设置响应状态码和头部信息
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()

                    response = {
                        'input_query': user_query,
                        'response': response_message
                    }
                    self.wfile.write(json.dumps(response).encode())

                elif path == '/logical_read':
                    user_query = data.get('queryId', '')
                    flag = data.get('flag', '')
                    # 步骤: 查询解析
                    access_tokens = ['sk-fa9c6c9c60ee4296ac9dbda8b86ad503']

                    chat = backend_logical_read(access_tokens)
                    response_message = chat.generate_flow(user_query, flag)

                    # 设置响应状态码和头部信息
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()

                    self.wfile.write(json.dumps(response_message).encode())
                
                elif path == '/read_datasource':
                    # 步骤: 查询解析
                    access_tokens = ['sk-fa9c6c9c60ee4296ac9dbda8b86ad503']

                    chat = dataSource(access_tokens)
                    response_message = chat.read_datasource()

                    response = {
                        'response': response_message
                    }

                    # 设置响应状态码和头部信息
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()

                    self.wfile.write(json.dumps(response).encode())

                elif path == '/code_result':
                    user_query = data.get('queryId', '')
                    access_tokens = ['sk-fa9c6c9c60ee4296ac9dbda8b86ad503']

                    try:
                        chat = Chat(access_tokens, model_loader)
                        code_output, llm_result, images, code_result = chat.code_result(user_query)
                        response = {
                            'code_output': code_output,
                            'llm_result': llm_result,
                            'images': images,
                            'code_result': code_result.to_dict(orient="records")
                        }
                    except Exception as e:
                        print(f"err {str(e)}")

                    # 设置响应状态码和头部信息
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()

                    self.wfile.write(json.dumps(response).encode())

                elif path == '/find_data':
                    datasource = data.get('datasource', '')
                    access_tokens = ['sk-fa9c6c9c60ee4296ac9dbda8b86ad503']

                    try:
                        chat = dataSource(access_tokens)
                        
                        response = chat.generate_json(datasource)
                    except Exception as e:
                        print(f"err {str(e)}")

                    # 设置响应状态码和头部信息
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()

                    self.wfile.write(json.dumps(response).encode())

                elif path == '/GetDataSourceDeatils':
                    datasource = data.get('datasource', '')
                    access_tokens = ['sk-fa9c6c9c60ee4296ac9dbda8b86ad503']

                    try:
                        chat = dataSource(access_tokens)
                        
                        response = chat.GetDataSourceDeatils(datasource)
                    except Exception as e:
                        print(f"err {str(e)}")

                    # 设置响应状态码和头部信息
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()

                    self.wfile.write(json.dumps(response).encode())

                elif path == '/testquery':
                    datasource = data.get('prompt', '')
                    access_tokens = ['sk-fa9c6c9c60ee4296ac9dbda8b86ad503']

                    try:
                        chat = Chat(access_tokens,model_loader)
                        
                        response = chat.testquery(datasource)
                    except Exception as e:
                        print(f"err {str(e)}")

                    # 设置响应状态码和头部信息
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()

                    self.wfile.write(json.dumps(response).encode())
                
                elif path == '/get_code':
                    query_id = data.get('queryId', '')
                    access_tokens = ['sk-fa9c6c9c60ee4296ac9dbda8b86ad503']

                    try:
                        chat = Chat(access_tokens,model_loader)
                        
                        response = chat.get_code(query_id)
                    except Exception as e:
                        print(f"err {str(e)}")

                    # 设置响应状态码和头部信息
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()

                    self.wfile.write(json.dumps(response).encode())                         

                elif path == '/Query_optimization_result':
                    query_id = data.get('queryId', '')
                    access_tokens = ['sk-fa9c6c9c60ee4296ac9dbda8b86ad503']

                    try:
                        chat = Chat(access_tokens,model_loader)
                        
                        response = chat.query_optimization_result(query_id)
                    except Exception as e:
                        print(f"err {str(e)}")

                    # 设置响应状态码和头部信息
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()

                    self.wfile.write(json.dumps(response).encode())         

                elif path == '/getLineageData':
                    query_id = data.get('queryId', '')
                    column_name = data.get('columnName', '')
                    access_tokens = ['sk-fa9c6c9c60ee4296ac9dbda8b86ad503']

                    try:
                        chat = dataSource(access_tokens)
                        
                        LineageData, EdgeData = chat.getLineageData(query_id, column_name)
                        response = {
                            'LineageData': LineageData,
                            'EdgeData': EdgeData
                        }

                    except Exception as e:
                        print(f"err {str(e)}")

                    # 设置响应状态码和头部信息
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()

                    self.wfile.write(json.dumps(response).encode())

                elif path == '/getSourceData':
                    table_name = data.get('tableName', '')
                    access_tokens = ['sk-fa9c6c9c60ee4296ac9dbda8b86ad503']

                    try:
                        chat = dataSource(access_tokens)
                        
                        result_data = chat.getSourceData(table_name)
                        response = result_data

                    except Exception as e:
                        print(f"err {str(e)}")

                    # 设置响应状态码和头部信息
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()

                    self.wfile.write(json.dumps(response).encode())


                elif path == '/sendCommand':
                    query_id = data.get('queryId', '')
                    query = data.get('query', '')
                    access_tokens = ['sk-fa9c6c9c60ee4296ac9dbda8b86ad503']

                    try:
                        chat = Chat(access_tokens, model_loader)
                        
                        result_data = chat.sendCommand(query_id, query)
                        response = result_data

                    except Exception as e:
                        print(f"err {str(e)}")

                    # 设置响应状态码和头部信息
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()

                    self.wfile.write(json.dumps(response).encode())

                elif path == '/getCommandHistory':
                    query_id = data.get('queryId', '')
                    access_tokens = ['sk-fa9c6c9c60ee4296ac9dbda8b86ad503']

                    try:
                        chat = Chat(access_tokens, model_loader)
                        
                        result_data = chat.getCommandHistory(query_id)
                        response = result_data

                    except Exception as e:
                        print(f"err {str(e)}")

                    # 设置响应状态码和头部信息
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()

                    self.wfile.write(json.dumps(response).encode())                
                    
                else:
                    # 如果路径不匹配，返回404
                    self.send_response(404)
                    self.send_header('Content-type', 'text/plain')
                    self.end_headers()
                    self.wfile.write(b'Path not found')    

            except json.JSONDecodeError:
                self.send_response(400)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(b'Invalid JSON format')

        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(f'Internal Server Error: {str(e)}'.encode())

# 启动服务
def start_server():

    server_address = ('', 9000)
    httpd = HTTPServer(server_address, RequestHandler)
    print('Server started on port 9000')
    httpd.serve_forever()


def run():
    try:
       start_server()
    except Exception as e:
        import traceback
        exception_info = traceback.format_exception(type(e), e, e.__traceback__)
        exception_message = ''.join(exception_info)
        
        print("Exception occurred:")
        print(exception_message)

