import os
import json
import logging
from typing import Any, Dict, Literal, Tuple

import requests
from tenacity import retry, stop_after_attempt, wait_fixed
from transformers import AutoModelForCausalLM, AutoTokenizer

from ..helpers import PROMPT_TEMPLATE

Instruction = """I will provide you with a question, output sentences along with an answer range. The output sentences are the response of the question provided. The answer range could either describe the type of answer expected or list all possible valid answers. Using the information provided, you must accurately and precisely determine and extract the intended key answer from the output sentences. Please don't have your subjective thoughts about the question.
First, you need to determine whether the content of the output sentences is relevant to the given question. If the entire output sentences are unrelated to the question (meaning the output sentences are not addressing the question), then output [No valid answer].
Otherwise, ignore the parts of the output sentences that have no relevance to the question and then extract the key answer that matches the answer range.
Below are some special cases you need to be aware of: 
    (1) If the output sentences present multiple different answers, carefully determine if the later provided answer is a correction or modification of a previous one. If so, extract this corrected or modified answer as the final response. Conversely, if the output sentences fluctuate between multiple answers without a clear final answer, you should output [No valid answer].
    (2) If the answer range is a list and the key answer in the output sentences is not explicitly listed among the candidate options in the answer range, also output [No valid answer].

"""

SYSTEM_PROMPT = "You are a help assistant tasked with extracting the precise key answer from given output sentences."


class Extractor:
    """
    Extractor class for extracting key answers from a given question and output sentences.

    Args:
        model_name (Literal["xFinder-qwen1505", "xFinder-llama38it"]): The model name to be used for inference.
        inference_mode (Literal["local", "api"]): The mode of inference, either 'local' or 'api'.
        model_path_or_url (str): The path or URL of the model.
        temperature (float, optional): The temperature value for sampling. Defaults to 0.
        max_tokens (int, optional): The maximum number of tokens to generate. Defaults to 3000.

    Raises:
        ValueError: If inference_mode is not 'local' or 'api'.
        ValueError: If temperature or max_tokens are out of the expected range.

    Attributes:
        STOP_TOKENS (List[str]): List of stop tokens to be used for inference.
    """
    STOP_TOKENS = ["<|endoftext|>", "<|im_end|>",
                   "<eoa>", "<||>", "<end_of_turn>", "<|eot_id|>"]

    def __init__(self,
                 model_name: Literal["xFinder-qwen1505", "xFinder-llama38it"],
                 inference_mode: Literal["local", "api"],
                 model_path_or_url: str,
                 temperature: float = 0,
                 max_tokens: int = 3000):

        if inference_mode not in ["local", "api"]:
            raise ValueError("inference_mode must be either 'local' or 'api'")

        if not (0 <= temperature <= 1):
            raise ValueError("temperature should be between 0 and 1")

        if max_tokens <= 0:
            raise ValueError("max_tokens should be greater than 0")

        self.model_name = model_name
        self.inference_mode = inference_mode
        self.model_path_or_url = model_path_or_url
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.system_prompt = SYSTEM_PROMPT

        if inference_mode == "local":
            self.tokenizer, self.model = self._initialize_local_model()
        elif inference_mode == "api":
            self.tokenizer = self.model = None

    def _initialize_local_model(self) -> Tuple[AutoTokenizer, AutoModelForCausalLM]:
        if not os.path.exists(self.model_path_or_url):
            logging.info(
                f"Model not found locally. Downloading model {self.model_name} from Huggingface.")
            os.system(
                f'huggingface-cli download --resume-download IAAR-Shanghai/{self.model_name} --local-dir {self.model_path_or_url}')
        tokenizer = AutoTokenizer.from_pretrained(
            self.model_path_or_url, use_fast=False, trust_remote_code=True)
        model = AutoModelForCausalLM.from_pretrained(
            self.model_path_or_url,
            torch_dtype="auto",
            device_map="auto",
            trust_remote_code=True
        )
        return tokenizer, model

    def create_formatted_prompt(self, query: Dict[str, Any]) -> str:
        if self.model_name not in PROMPT_TEMPLATE:
            raise ValueError(
                f"Model name '{self.model_name}' is not supported in PROMPT_TEMPLATE.")
        return PROMPT_TEMPLATE[self.model_name].format(system=self.system_prompt, input=query)

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    def _execute_api_inference(self, query: Dict[str, Any]) -> str:
        prompt = self.create_formatted_prompt(query)
        payload = json.dumps({
            "prompt": prompt,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "stop": self.STOP_TOKENS
        })
        headers = {'Content-Type': 'application/json'}
        try:
            logging.info(f"Attempting API request with prompt: {prompt[:50]}...")
            response = requests.post(
                self.model_path_or_url, headers=headers, data=payload, timeout=(5, 10))  # Add timeout here
            response.raise_for_status()
            res = response.json()['text'][0].replace(prompt, "").strip()
            return res
        except requests.exceptions.HTTPError as e:
            logging.error(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
            raise
        except requests.exceptions.ConnectionError as e:
            logging.error(f"Connection error occurred: {e}")
            raise
        except requests.RequestException as e:
            logging.error(f"Request error occurred: {e}")
            raise

    def _execute_local_inference(self, query: Dict[str, Any]) -> str:
        prompt = self.create_formatted_prompt(query)
        input_ids = self.tokenizer.encode(
            prompt, return_tensors="pt").to(self.model.device)
        output_ids = self.model.generate(
            input_ids, max_new_tokens=self.max_tokens, temperature=self.temperature)
        response = self.tokenizer.decode(
            output_ids[0][input_ids.shape[1]:], skip_special_tokens=True)
        return response.strip()

    def generate_output(self, question, llm_output, standard_answer_range) -> str:
        formatted_query = f'Question: """{question}"""\n\nOutput sentences: """{llm_output}"""\n\nAnswer range: {standard_answer_range}\n\nKey extracted answer: '
        try:
            if self.inference_mode == "api":
                return self._execute_api_inference(formatted_query)
            else:
                return self._execute_local_inference(formatted_query)
        except Exception as e:
            logging.error(f"Error during inference: {e}")
            return "[Error in inference]"
