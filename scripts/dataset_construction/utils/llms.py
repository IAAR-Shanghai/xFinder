import json
import os
from abc import ABC

import requests
from loguru import logger

PROMPT_DIR = './prompts'


class LargeLanguageModels(ABC):
    def __init__(
        self,
        model_name: str = None,
        temperature: float = 0,
        max_new_tokens: int = 2048,
        top_p: float = 0.9,
        top_k: int = 5,
        url: str = None,
        **more_params
    ):
        self.params = {
            'model_name': model_name if model_name else self.__class__.__name__,
            'temperature': temperature,
            'max_new_tokens': max_new_tokens,
            'top_p': top_p,
            'top_k': top_k,
            'url': url,
            **more_params
        }

    def request(self, query):
        return ''

    @staticmethod
    def _read_prompt_template(filename: str) -> str:
        path = os.path.join(PROMPT_DIR, filename)
        if os.path.exists(path):
            with open(path) as f:
                return f.read()
        else:
            logger.error(f'Prompt template not found at {path}')
            return ''

    @staticmethod
    def _construct_examples(few_shot_data):
        if few_shot_data:
            return '***** Start In-Context Examples *****\n' + '\n'.join([
                f"Q: {shot['question']}\nA: The answer is {shot['correct_answer']}."
                for shot in few_shot_data
            ]) + '\n***** End In-Context Examples *****'
        return ''

    def generate(self, data_conf, test_data, few_shot_data, prompt_type):
        prompt_template = self._read_prompt_template(f'{prompt_type}.txt')
        examples = self._construct_examples(few_shot_data)

        prompt = prompt_template.format(
            task_type=data_conf['task_type'],
            task_description=data_conf['task_description'],
            examples=examples,
            question='Q: ' + test_data['question'] + '\nA: ',
        )

        res = self.request(prompt)

        return res


class VllmModel(LargeLanguageModels):
    def _base_prompt_template(self) -> str:
        return "{query}"

    def request(self, query: str) -> str:
        url = self.params['url']

        template = self._base_prompt_template()
        query = template.format(query=query)
        payload = json.dumps({
            "prompt": query,
            "temperature": self.params['temperature'],
            "max_tokens": self.params['max_new_tokens'],
            "n": 1,
            "top_p": self.params['top_p'],
            "top_k": self.params['top_k'],
        })
        headers = {
            'Content-Type': 'application/json'
        }
        res = requests.request("POST", url, headers=headers, data=payload)
        res = res.json()['text'][0].replace(query, '')
        res = self._post_process_response(res)
        return res

    def _post_process_response(self, response: str) -> str:
        return response


class Baichuan2_7B_Chat(VllmModel):
    def _base_prompt_template(self) -> str:
        return """<reserved_195>{query}<reserved_196>"""


class ChatGLM3_6B(VllmModel):
    ...


class LLaMA2_7B_Chat(VllmModel):
    def _base_prompt_template(self) -> str:
        template = """<s>[INST] <<SYS>>""" \
            """You are being tested. Follow the instruction below. """ \
            """<</SYS>> {query} [/INST] Sure, I'd be happy to help. Here is the answer:"""
        return template


class PHI2(VllmModel):
    def _base_prompt_template(self) -> str:
        return """Instruct: {query}\nOutput:"""


class Qwen_14B_Chat(VllmModel):
    def _base_prompt_template(self) -> str:
        template = """<|im_start|>system\nYou are a helpful assistant.<|im_end|>\n<|im_start|>user\n""" \
                   """{query}<|im_end|>\n<|im_start|>assistant\n"""
        return template


class Qwen_7B_Chat(VllmModel):
    def _base_prompt_template(self) -> str:
        template = """<|im_start|>system\nYou are a helpful assistant.<|im_end|>\n<|im_start|>user\n""" \
                   """{query}<|im_end|>\n<|im_start|>assistant\n"""
        return template


class Qwen1_5_4B_Chat(VllmModel):
    def _base_prompt_template(self) -> str:
        template = """<|im_start|>system\nYou are a helpful assistant.<|im_end|>\n<|im_start|>user\n""" \
                   """{query}<|im_end|>\n<|im_start|>assistant\n"""
        return template


class Qwen1_5_0_5B_Chat(VllmModel):
    def _base_prompt_template(self) -> str:
        template = """<|im_start|>system\nYou are a helpful assistant.<|im_end|>\n<|im_start|>user\n""" \
                   """{query}<|im_end|>\n<|im_start|>assistant\n"""
        return template


class Qwen1_5_1_8B_Chat(VllmModel):
    def _base_prompt_template(self) -> str:
        template = """<|im_start|>system\nYou are a helpful assistant.<|im_end|>\n<|im_start|>user\n""" \
                   """{query}<|im_end|>\n<|im_start|>assistant\n"""
        return template


class Qwen1_5_4B(VllmModel):
    def _base_prompt_template(self) -> str:
        template = """<|im_start|>system\nYou are a helpful assistant.<|im_end|>\n<|im_start|>user\n""" \
                   """{query}<|im_end|>\n<|im_start|>assistant\n"""
        return template


class Qwen1_5_14B_Chat(VllmModel):
    def _base_prompt_template(self) -> str:
        template = """<|im_start|>system\nYou are a helpful assistant.<|im_end|>\n<|im_start|>user\n""" \
                   """{query}<|im_end|>\n<|im_start|>assistant\n"""
        return template


class Gemma_2B_it(VllmModel):
    def _base_prompt_template(self) -> str:
        template = """<bos><start_of_turn>user""" \
            """{query}<end_of_turn>""" \
            """<start_of_turn>model"""
        return template


class Gemma_7B_it(VllmModel):
    def _base_prompt_template(self) -> str:
        template = """<bos><start_of_turn>user""" \
            """{query}<end_of_turn>""" \
            """<start_of_turn>model"""
        return template


class InternLM2_7B_Chat(VllmModel):
    def _base_prompt_template(self) -> str:
        template = """<|im_start|>system""" \
            """You are a helpful assistant.<|im_end|>""" \
            """<|im_start|>user""" \
            """{query}<|im_end|>""" \
            """<|im_start|>assistant\n"""
        return template


class Gemma_7B(VllmModel):
    def _base_prompt_template(self) -> str:
        template = """<bos><start_of_turn>user""" \
            """{query}<end_of_turn>""" \
            """<start_of_turn>model"""
        return template


class LLaMA_7B(VllmModel):
    def _base_prompt_template(self) -> str:
        template = """<s>[INST] <<SYS>>""" \
            """You are being tested. Follow the instruction below. """ \
            """<</SYS>> {query} [/INST] Sure, I'd be happy to help. Here is the answer:"""
        return template


class Mistral_7B_v0_1(VllmModel):
    def _base_prompt_template(self) -> str:
        template = """[INST] You are a helpful assistant. [/INST]""" \
                   """[INST] {query} [/INST]\n"""
        return template


class Llama3_8B(VllmModel):
    def _base_prompt_template(self) -> str:
        template = """<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n""" \
            """You are being tested. Follow the instruction below.<|eot_id|><|start_header_id|>user<|end_header_id|>\n""" \
            """{query} <|eot_id|><|start_header_id|>assistant<|end_header_id|>\n"""
        return template


class Llama3_8B_Instruct(VllmModel):
    def _base_prompt_template(self) -> str:
        template = """<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n""" \
            """You are being tested. Follow the instruction below.<|eot_id|><|start_header_id|>user<|end_header_id|>\n""" \
            """{query} <|eot_id|><|start_header_id|>assistant<|end_header_id|>\n"""
        return template


class Qwen1_5_MoE_A2_7B_Chat(VllmModel):
    def _base_prompt_template(self) -> str:
        template = """<|im_start|>system\nYou are a helpful assistant.<|im_end|>\n<|im_start|>user\n""" \
                   """{query}<|im_end|>\n<|im_start|>assistant\n"""
        return template


class PHI3_Mini_128k_Instruct(VllmModel):
    def _base_prompt_template(self) -> str:
        template = """<|system|>\nYou are a helpful AI assistant.<|end|>\n<|user|>""" \
            """{query}<|end|>\n<|assistant|>\n"""
        return template


class InternLM2_1_8B_Chat(VllmModel):
    def _base_prompt_template(self) -> str:
        template = """<|im_start|>system""" \
            """You are a helpful assistant.<|im_end|>""" \
            """<|im_start|>user""" \
            """{query}<|im_end|>""" \
            """<|im_start|>assistant\n"""
        return template


if __name__ == '__main__':
    llm = LargeLanguageModels()
    llm.generate({'task_type': 'train_data',
                 'task_description': 'test_data'},
                 {'question': 'what'}, 5, 'few_shot')
