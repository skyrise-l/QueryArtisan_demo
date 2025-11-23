

class query_deconstruct:
    def __init__(self, ):
        self.file_path = {}
        self.columns_type = {}
        self.table_key = {}
        self.may_trouble_column = {}
        return 

    def get_define(self, query, decompose_query, pre_define):
        prenl = pre_define

        prenl += self.get_logical_prompt(query, decompose_query)

        return prenl

    def get_logical_prompt(self, query, decompose_query):
        
        message = "\n\n## 3. Now, let's move on to the third step. Below, I will provide natural language query for this data analysis. Please analyze and generate a complete data analysis logical plan that includes reading data files, executing the corresponding queries, and saving the results to a file. The syntax and format of the logical plan should follow the information provided earlier.\n"
      

        message += "The specific query statement is: '(" + query + ")'. I have already attempted to extract the query-related requirements from it. You only need to execute the logical plan generation for this part of the content, temporarily ignore other analysis requirements. Need deal requirements:" + decompose_query
        

      #  message += "## Besides, here are some important points to keep in mind when generating a logical plan:\n"

      #  message += "(1) Please pay close attention to strings appearing in this format within the query: '\"value\"'. This format, enclosed by both double and single quotation marks, indicates that the double quotation marks are actually part of the value, while the single quotation marks signify a value reference. Therefore, the extracted condition value should be: column = '\"value\"'.\n"

        #message += "(2) Also, pay attention to phrases such as How many, How much, total number, average, earliest, latest, sum, and similar terms that appear in the query. This may indicate the need to perform aggregate functions, such as count, sum, avg.\n"


      #  message += "#(3) Exercise caution in using the 'distinct' to a specific column,  Make sure to use it only when the natural language query explicitly requires deduplication. And please do not distinct the query target results, as it can easily lead to incorrect results. \n"
        
       # message += "#(4) When using order_by operator, if the sorted column only contains the result of an aggregate function, you must add the columns used for grouping in the aggregate function into order column to avoid ambiguity. The order for this column should be clearly DESC.\n"
        
     # message += "For example, operation detailsin Step 2: 'group Step 1 by id' and operation details in Step 3: 'order Step 2 by count(*) > 1 DESC' can optimize the Step3 order operation details to 'order Step 2 by count(*) > 1 DESC, id DESC'.\n"

       # message += "#(5) When generating the operations detail for generating a logical plan, please pay special attention to the case sensitivity of column names. Columns with the same meaning in different tables might have different cases, such as 'Client_id' versus 'client_id'. Be sure to distinguish between them.\n"
       
      #  message += "#(4) Do not arbitrarily change the case of the condition values obtained in the query; string comparisons throughout the entire data analysis are case-sensitive.\n"

        #message += "#(5) A crucial point! When parsing queries, please make use of your understanding as much as possible rather than relying solely on literal word matching. This is because queries might employ different vocabulary or phrases to express the meaning of column names. It's essential to truly grasp the intent of the query before proceeding with logical plan generation.\n"
        
        #message += "#(6) group_bt operations are typically used when there are aggregate functions and aggregate function conditions. If you only need to query the result of a specific aggregate function and other columns simultaneously, grouping is usually not necessary. For example, select MAX(col) and col2 AS result.\n"

      #  message += "#(7) When generating a logical plan, all the tables I provided should be utilized. If I have specified relevant foreign key relationships, please use joins to connect them via the foreign keys as much as possible; otherwise, there is a high probability of error. Additionally, please note that each join step should only connect two tables.\n"
        

        #message += "#(2) When generating a logical plan, please ensure that the operation sequence follows the priority order: join > filter > select (with join having the highest priority, preferably executed first). This is to ensure that there are no issues with incorrect column usage. Perform the join operation first, followed by the filter operation, and finally execute the select operation as late as possible. This is a rational and safe execution order."
      #  "#此外，在进行自然语言查询语句解析时，注意只需要查询问题所指定的列，无需额外查询主键；同时注意对最后的结果进去去重(如果存在join等操作可能会有重复的元组)。注意：请使用英文回答："
        
        return message
    