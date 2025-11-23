import json
import os
import ast
import sqlite3

class LogicalNode:
    def __init__(self, id, label, operator, targetColumns, targetSteps, details, relatedCodeLines):
        self.id = id
        self.label = label
        self.operator = operator
        self.targetColumns = targetColumns
        self.targetSteps = targetSteps
        self.details = details
        self.relatedCodeLines = relatedCodeLines  # Correct initialization

    def to_dict(self):
        return {
            'id': self.id,
            'label': self.label,
            'operator': self.operator,
            'targetColumns': self.targetColumns,
            'targetSteps': self.targetSteps,
            'details': self.details,
            'relatedCodeLines': self.relatedCodeLines  # Corrected
        }

class LogicalEdge:
    def __init__(self, id, source, target):
        self.id = id
        self.source = source
        self.target = target

    def to_dict(self):
        return {
            'id': self.id,
            'source': self.source,
            'target': self.target
        }

import re

class backend_logical_read:
    def __init__(self, access_tokens):
        self.token_key = access_tokens[0]  # Assuming access_tokens is a list

    def parse_file(self, file_path):
        logical_nodes = []
        logical_edges = []

        with open(file_path, 'r') as file:
            steps = file.read().strip().split("\n\n")  # Split by double newlines (empty lines between steps)

        step_id = 1
        step_mapping = {}

        for step in steps:
            lines = step.strip().splitlines()
            if not lines:
                continue
            
            # Initialize values with None
            operator = target_columns = target_steps = operation_details = relatedCodeLines = None

            for line in lines:
                line = line.strip()

                if line.startswith("Operator:"):
                    operator = line.replace("Operator:", "").strip()
                elif line.startswith("Target columns:"):
                    target_columns = line.replace("Target columns:", "").strip()
                elif line.startswith("Target steps:"):
                    target_steps = line.replace("Target steps:", "").strip()
                elif line.startswith("Operation details:"):
                    operation_details = line.replace("Operation details:", "").strip()
                elif line.startswith("relatedCodeLines:"):
                    relatedCodeLines = line.replace("relatedCodeLines:", "").strip()
                    # Assuming that relatedCodeLines are line numbers, split by commas
                    relatedCodeLines = ast.literal_eval(relatedCodeLines)

            # In case some fields are missing, ensure the defaults
            if target_columns == 'None':
                target_columns = None
            if target_steps == 'None':
                target_steps = None

            node = LogicalNode(
                id=step_id,
                label=f"Step {step_id}",
                operator=operator,
                targetColumns=target_columns,
                targetSteps=target_steps,
                details=operation_details,
                relatedCodeLines=relatedCodeLines  # Corrected
            )

            logical_nodes.append(node)
            step_mapping[step_id] = node

            # If target_steps exist, create edges from the target steps to the current step
            if target_steps:
                target_steps_list = [int(x.strip().replace("Step", "")) for x in target_steps.split(",")]
                for target_step in target_steps_list:
                    logical_edges.append(LogicalEdge(id=len(logical_edges) + 1, source=target_step, target=step_id))

            step_id += 1

        return logical_nodes, logical_edges

    def generate_flow(self, query_id, flag):
        try:
            if query_id == "7ae0e31f-4648-4541-8fe2-e5fdbc5a98a5":
                base_path = "/mnt/d/study/vldb_demo/demo/chat/config/"

                if flag == "1":
                    file_path = base_path + str(query_id) + ".txt"
                else:
                    file_path = base_path + str(query_id) + "-no.txt"

                nodes, edges = self.parse_file(file_path)

                # Convert nodes and edges to dictionaries for easier serialization
                node_dicts = [node.to_dict() for node in nodes]
                edge_dicts = [edge.to_dict() for edge in edges]
            else:
                db_file = "/mnt/d/study/vldb_demo/demo/chat/data/dataset_metadata_history.db"
                conn = sqlite3.connect(db_file)
                cursor = conn.cursor()
                conn.row_factory = sqlite3.Row  # 设置行工厂为字典模式
                cursor = conn.cursor()
                
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
                        if flag == "1":
                            file_path = base_path + str(hash) + ".txt"
                        else:
                            file_path = base_path + str(hash) + "_opt.txt"

                        nodes, edges = self.parse_file2(file_path)
                        node_dicts = [node.to_dict() for node in nodes]
                        edge_dicts = [edge.to_dict() for edge in edges]
                    else:
                        print("search error")
                except Exception as e:
                    print(f"query erorr {e}")

        except Exception as e:
            print("error generate_flow", str(e))
            return {"error": str(e)}

        print({'logicalNodes': node_dicts, 'logicalEdges': edge_dicts})
        return {'logicalNodes': node_dicts, 'logicalEdges': edge_dicts}


    def parse_file2(self, file_path):
        logical_nodes = []
        logical_edges = []

        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read().strip()
        
        # 修正的正则表达式 - 匹配实际的数据格式
        step_pattern = re.compile(
            r"(?:\*\*)?Step\s+(\d+):(?:\*\*)?"  # 步骤号
            r"\s*Operator:\s*(.*?)(?:\.|$)"     # 操作符
            r".*?Target[_\s]+columns:\s*(.*?)(?:\.|$)"  # 目标列（支持下划线和空格）
            r".*?Target[_\s]+steps:\s*(.*?)(?:\.|$)"    # 目标步骤
            r".*?Details:\s*(.*?)(?=relatedCodeLines:|$)"  # 详细信息（匹配到relatedCodeLines或结尾）
            r".*?relatedCodeLines:\s*(\[.*?\])",  # 相关代码行（匹配完整的数组格式）
            re.IGNORECASE | re.DOTALL
        )
        
        matches = step_pattern.finditer(content)
        step_mapping = {}

        for match in matches:
            # 正确处理捕获组
            step_id = int(match.group(1))  # ✅ 转换为整数
            operation = match.group(2).strip().rstrip('.') if match.group(2) else "None"
            target_columns = match.group(3).strip().rstrip('.') if match.group(3) else "None"
            target_steps = match.group(4).strip().rstrip('.') if match.group(4) else "none"
            details = match.group(5).strip().rstrip('.') if match.group(5) else "None"
            related_code_lines_str = match.group(6).strip() if match.group(6) else "[]"
            
            # ✅ 正确处理 relatedCodeLines
            try:
                related_code_lines = ast.literal_eval(related_code_lines_str)
            except (ValueError, SyntaxError):
                related_code_lines = []
            
            # 处理 None 值
            if target_columns.lower() in ['none', 'null']:
                target_columns = None
            if target_steps.lower() in ['none', 'null']:
                target_steps = None

            node = LogicalNode(
                id=step_id,
                label=f"Step {step_id}",
                operator=operation,
                targetColumns=target_columns,
                targetSteps=target_steps,
                details=details,
                relatedCodeLines=related_code_lines
            )

            logical_nodes.append(node)
            step_mapping[step_id] = node

            # ✅ 修正边创建逻辑 - 只有在target_steps不是None且不是"none"时才创建边
            if target_steps and target_steps.lower() not in ['none', 'null']:
                target_steps_nums = self._parse_target_steps(target_steps)
                for target_step_num in target_steps_nums:
                    logical_edges.append(LogicalEdge(
                        id=len(logical_edges) + 1, 
                        source=target_step_num, 
                        target=step_id
                    ))

        return logical_nodes, logical_edges

    def _parse_target_steps(self, target_steps_str):
        """解析target_steps字符串，提取步骤号"""
        step_nums = []
        # 匹配 "step 1", "Step 2" 等格式
        step_matches = re.findall(r'step\s+(\d+)', target_steps_str, re.IGNORECASE)
        for match in step_matches:
            step_nums.append(int(match))
        return step_nums