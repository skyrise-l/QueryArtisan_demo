# -*- coding: utf-8 -*-

import json
from os import getenv
import requests
from certifi import where
from ..utils.utils import Console
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from requests.exceptions import ConnectionError, Timeout, ChunkedEncodingError


class OpenAIAgent:
    DEFAULT_SYSTEM_PROMPT = (
        "You are a code analyst specializing in text-to-code tasks within data analysis. "
        "Your role involves analyzing various data analysis tasks, assessing whether the generated "
        "data analysis code aligns with the intent of the natural language queries, identifying any errors, and correcting them as needed."
    )
    TITLE_PROMPT = "Generate a brief title for our conversation."

    def __init__(
        self,
        agent_name,
        api_key="sk-fa9c6c9c60ee4296ac9dbda8b86ad503",
        system_prompt=None,
        url="https://api.deepseek.com/chat/completions",
        model="deepseek-chat",
        proxy=None
    ):
        self.agent_name = agent_name
        self.api_key = api_key
        self.system_prompt = system_prompt if system_prompt else self.DEFAULT_SYSTEM_PROMPT
        self.messages = self.init_messages()
        self.model = model
        self.url = url
        self.proxy = proxy

        self.req_kwargs = {
            "proxies": {
                "http": proxy,
                "https": proxy,
            } if proxy else {},
            "verify": where(),
            "timeout": 60, 
            "allow_redirects": False,
        }

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        retry=retry_if_exception_type((ConnectionError, Timeout, ChunkedEncodingError))
    )
    def _make_request(self, url, headers, data):
        """内部请求方法，带有重试机制"""
        response = requests.post(
            url=url,
            headers=headers,
            data=json.dumps(data),  # 确保正确序列化为JSON
            **self.req_kwargs
        )
        response.raise_for_status()  # 如果状态码不是200，抛出异常
        return response

    def init_messages(self):
        return [{"role": "system", "content": self.system_prompt}]

    def __get_headers(self, api_key=None):
        """获取请求头，支持自定义api_key"""
        if api_key is None:
            api_key = self.api_key
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }

    def single_talk(self, prompt, model="deepseek-chat"):
        """
        单次独立对话（实例方法）
        每次都是全新的对话，不使用之前的上下文
        
        :param prompt: 用户输入
        :param role: 角色，默认为'user'
        :param custom_model: 可选的临时模型覆盖
        :param custom_system_prompt: 可选的临时系统提示覆盖
        :return: AI回复
        """
        # 构建全新的消息列表
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": prompt}
        ]

        data = {
            "model": model,
            "messages": messages,
        }

        try:
            response = self._make_request(
                url=self.url,
                headers=self.__get_headers(),
                data=data
            )
            reply = self.deal_reply(response.json())
            return reply
            
        except requests.exceptions.HTTPError as e:
            Console.error_bh(f"HTTP错误: {e}")
            if hasattr(e.response, 'text'):
                Console.error_bh(f"错误详情: {e.response.text}")
            return f"[错误] HTTP错误: {e}"
        except Exception as e:
            Console.error_bh(f"请求失败: {e}")
            return f"[错误] 请求失败: {e}"

    def continue_talk(self, prompt):
        """持续对话（保存上下文）"""
        user_message = {"role": "user", "content": prompt}
        self.messages.append(user_message)

        data = {
            "model": self.model,
            "messages": self.messages,
        }
        
        try:
            response = self._make_request(
                url=self.url,
                headers=self.__get_headers(),
                data=data
            )
            reply = self.deal_reply(response.json())
            
            # 保存助手回复到上下文
            self.messages.append({"role": "assistant", "content": reply})
            return reply
            
        except requests.exceptions.HTTPError as e:
            Console.error_bh(f"HTTP错误: {e}")
            if hasattr(e.response, 'text'):
                Console.error_bh(f"错误详情: {e.response.text}")
            return f"[错误] HTTP错误: {e}"
        except Exception as e:
            Console.error_bh(f"请求失败: {e}")
            return f"[错误] 请求失败: {e}"

    def temporary_talk(self, prompt):
        """临时对话（不保存上下文）"""
        user_message = {"role": "user", "content": prompt}
        temp_messages = self.messages.copy()
        temp_messages.append(user_message)

        data = {
            "model": self.model,
            "messages": temp_messages,
        }

        try:
            response = self._make_request(
                url=self.url,
                headers=self.__get_headers(),
                data=data
            )
            reply = self.deal_reply(response.json())
            return reply
            
        except requests.exceptions.HTTPError as e:
            Console.error_bh(f"HTTP错误: {e}")
            if hasattr(e.response, 'text'):
                Console.error_bh(f"错误详情: {e.response.text}")  # 显示详细错误信息
            return f"[错误] HTTP错误: {e}"
        except Exception as e:
            Console.error_bh(f"请求失败: {e}")
            return f"[错误] 请求失败: {e}"

    @staticmethod
    def deal_reply(response):
        """
        处理API的回复（简化版，不再需要status参数）
        """
        try:
            choice = response["choices"][0]
            message = choice.get("message", {})
            text = message.get("content", "")
            
            if not text:
                Console.error_bh(f"无法获取回复内容，响应格式: {response}")
                return "[错误] 无法获取回复内容"
                
            return text
            
        except (KeyError, IndexError) as e:
            Console.error_bh(f"解析API响应时出错: {e}")
            Console.error_bh(f"原始响应: {response}")
            return "[错误] 无法解析API响应。"