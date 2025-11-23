import os
import sqlite3
import csv

# 用于判断数据格式的函数
def determine_data_format(value):
    try:
        # 尝试转换为整型
        int(value)
        return 'INTEGER'
    except ValueError:
        try:
            # 尝试转换为浮动类型
            float(value)
            return 'FLOAT'
        except ValueError:
            # 默认返回文本类型
            return 'TEXT'

# 创建数据库连接
def create_db_connection(db_file='dataset_metadata.db'):
    conn = sqlite3.connect(db_file)
    return conn

# 插入数据到数据库
def insert_metadata(conn, database_name, table_name, column_name, data_format, csv_path):
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO table_metadata (
            database_name, table_name, column_name, data_format, csv_path
        ) VALUES (?, ?, ?, ?, ?)
    ''', (database_name, table_name, column_name, data_format, csv_path))
    conn.commit()

# 读取并处理CSV文件
def process_csv_files(target_dir, conn):
    database_name = "dlbench"
    
    for file_name in os.listdir(target_dir):
        if file_name.endswith(".csv"):
            csv_path = os.path.join(target_dir, file_name)
            table_name = os.path.splitext(file_name)[0]  # 去掉扩展名，获取表名
            print(f"Processing file: {csv_path}")
            
            # 打开CSV文件，读取列信息
            with open(csv_path, mode='r', encoding='utf-8') as f:
                reader = csv.reader(f)
                headers = next(reader)  # 读取列名（表头）
                
                for column_name in headers:
                    # 读取每列的第一个数据值来判断格式
                    first_row = next(reader)
                    data_format = determine_data_format(first_row[headers.index(column_name)])
                    
                    # 插入元数据到数据库
                    insert_metadata(conn, database_name, table_name, column_name, data_format, csv_path)
                    
                    # 将文件指针重新定位到文件头，方便下次继续读取
                    f.seek(0)

# 主函数
def main():
    target_dir = './dlbench'  # 这里替换成目标目录的路径
    conn = create_db_connection()

    # 处理目标目录中的CSV文件
    process_csv_files(target_dir, conn)

    # 关闭数据库连接
    conn.close()

if __name__ == "__main__":
    main()
