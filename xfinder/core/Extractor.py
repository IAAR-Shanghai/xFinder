import json

import requests
from vllm import LLM, SamplingParams

from ..utils import PROMPT_TEMPLATE

Instruction = """I will provide you with a question, output sentences along with an answer range. The output sentences are the response of the question provided. The answer range could either describe the type of answer expected or list all possible valid answers. Using the information provided, you must accurately and precisely determine and extract the intended key answer from the output sentences. Please don't have your subjective thoughts about the question.
First, you need to determine whether the content of the output sentences is relevant to the given question. If the entire output sentences are unrelated to the question (meaning the output sentences are not addressing the question), then output [No valid answer].
Otherwise, ignore the parts of the output sentences that have no relevance to the question and then extract the key answer that matches the answer range.
Below are some special cases you need to be aware of: 
    (1) If the output sentences present multiple different answers, carefully determine if the later provided answer is a correction or modification of a previous one. If so, extract this corrected or modified answer as the final response. Conversely, if the output sentences fluctuate between multiple answers without a clear final answer, you should output [No valid answer].
    (2) If the answer range is a list and the key answer in the output sentences is not explicitly listed among the candidate options in the answer range, also output [No valid answer].

"""


class Extractor:

    def __init__(
        self,
        model_name,
        model_path=None,
        url=None,
        temperature=0,
        max_tokens=3000,
        SYSTEM="You are a help assistant tasked with extracting the precise key answer from given output sentences. You must only provide the extracted key answer without including any additional text."
    ):
        self.model_name = model_name
        self.PROMPT_TEMPLATE = PROMPT_TEMPLATE[model_name]
        self.SYSTEM = SYSTEM
        self.model_path = model_path
        self.url = url
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.mode = "API" if self.url is not None else "Local"  # priority: API > Local

        if self.mode == "Local":
            self.sampling_params = SamplingParams(
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                stop=[
                    "<|endoftext|>", "<|im_end|>", "<eoa>", "<||>",
                    "<end_of_turn>", "<|eot_id|>"
                ])
            self.llm = LLM(model=self.model_path, gpu_memory_utilization=0.5)

    @staticmethod
    def prepare_input(item):
        user_input = Instruction + \
                    "Question: \"\"\"" + item["question"] + "\"\"\"\n\n" + \
                    "Output sentences: \"\"\"" + item["llm_output"] + "\"\"\"\n\n" + \
                    "Answer range: " + item["standard_answer_range"] + "\n\n" + \
                    "Key extracted answer: "

        return user_input

    def gen_output(self, query):
        if self.mode == "API":
            return self.send_request(query)
        else:
            return self.offline_infer(query)

    def send_request(self, query: str) -> str:
        """Send a request to the model's API and return the response.
        
        Args:
            query (str): The input query.
        
        Returns:
            str: The extracted answer (xFinder's output).
        """
        prompt = self.PROMPT_TEMPLATE.format(system=self.SYSTEM, input=query)
        payload = json.dumps({
            "prompt":
                prompt,
            "temperature":
                self.temperature,
            "max_tokens":
                self.max_tokens,
            "stop": [
                "<|endoftext|>", "<|im_end|>", "<eoa>", "<||>", "<end_of_turn>",
                "<|eot_id|>"
            ],
        })
        headers = {'Content-Type': 'application/json'}
        res = requests.request("POST", self.url, headers=headers, data=payload)
        res = res.json()['text'][0]
        res = res.replace(prompt, "")
        # res = requests.post(self.url, json=payload)
        # res = res.json()['text']
        res = res.strip()
        return res

    def offline_infer(self, query: str) -> str:
        """Perform inference on the local xFinder model.
        
        Args:
            query (str): The input query.
        
        Returns:
            str: The extracted answer (xFinder's output).
        """
        prompt = self.PROMPT_TEMPLATE.format(system=self.SYSTEM, input=query)
        res = self.llm.generate(prompt, self.sampling_params)
        res = res[0]
        res = res.outputs[0].text.strip()
        return res
