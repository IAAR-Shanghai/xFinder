import argparse
import importlib.resources as pkg_resources
import json

from tqdm import tqdm

from . import examples
from .helpers import DataProcessor
from .modules import Comparator, Extractor


class Evaluator:
    """
    Evaluator class for evaluating the performance of the xFinder model.

    Args:
        model_name (str, optional): The model name to be used for inference. Defaults to "xFinder-qwen1505".
        inference_mode (str, optional): The mode of inference, either 'local' or 'api'. Defaults to "local".
        model_path_or_url (str, optional): The path or URL of the model. Defaults to "IAAR-Shanghai/xFinder-qwen1505".
        temperature (float, optional): The temperature value for sampling. Defaults to 0.7.
        max_tokens (int, optional): The maximum number of tokens to generate. Defaults to 100.
    """

    MATH_STANDARD_ANSWER_RANGE = "a(n) number / set / vector / matrix / interval / expression / function / equation / inequality"
    VALID_KEY_ANSWER_TYPES = {"math", "short_text",
                              "categorical_label", "alphabet_option"}

    def __init__(self, model_name="xFinder-qwen1505", inference_mode="local", model_path_or_url="IAAR-Shanghai/xFinder-qwen1505", temperature=0.7, max_tokens=100):
        self.extractor = Extractor(
            model_name=model_name,
            inference_mode=inference_mode,
            model_path_or_url=model_path_or_url,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        self.comparator = Comparator()
        self.data_processor = DataProcessor()

    def evaluate_single_item(self, question, llm_output, answer_range, answer_type, correct_answer):
        if answer_type not in self.VALID_KEY_ANSWER_TYPES:
            raise ValueError(
                f"Invalid key_answer_type: {answer_type}. Must be one of {self.VALID_KEY_ANSWER_TYPES}")

        if answer_type == "math":
            answer_range = self.MATH_STANDARD_ANSWER_RANGE

        extracted_answer = self.extractor.generate_output(
            question, llm_output, answer_range)
        evaluation_result = self.comparator.compare(
            (answer_type, answer_range, extracted_answer, correct_answer)
        )
        return evaluation_result

    def evaluate(self, data_path):
        data = self.data_processor.read_data(data_path)
        results = [
            self.evaluate_single_item(
                item["question"],
                item["llm_output"],
                self.MATH_STANDARD_ANSWER_RANGE if item["key_answer_type"] == "math" else item["standard_answer_range"],
                item["key_answer_type"],
                item["correct_answer"]
            ) for item in tqdm(data, desc="Evaluating")
        ]
        correct_count = sum(result[-1] for result in results)
        accuracy = correct_count / max(1, len(results)) if results else 0
        return accuracy

    def evaluate_single_example(self, question, llm_output, standard_answer_range, key_answer_type, correct_answer):
        if key_answer_type not in self.VALID_KEY_ANSWER_TYPES:
            raise ValueError(
                f"Invalid key_answer_type: {key_answer_type}. Must be one of {self.VALID_KEY_ANSWER_TYPES}")

        evaluation_result = self.evaluate_single_item(
            question,
            llm_output,
            standard_answer_range,
            key_answer_type,
            correct_answer
        )
        judgement = "Correct" if evaluation_result[-1] else "Incorrect"
        return judgement

    def save_results(self, results, output_path):
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=4, ensure_ascii=False)


def run_example(model_name, inference_mode, model_path_or_url, temperature, max_tokens):
    evaluator = Evaluator(
        model_name=model_name,
        inference_mode=inference_mode,
        model_path_or_url=model_path_or_url,
        temperature=temperature,
        max_tokens=max_tokens
    )

    # example for batch evaluation
    example_path = pkg_resources.path(examples, "example.json")
    evaluator.evaluate(example_path)

    # example for single example evaluation
    question = "What is the capital of France?"
    llm_output = "The capital of France is Paris."
    standard_answer_range = "[\"Paris\", \"Lyon\", \"Marseille\"]"
    key_answer_type = "short_text"
    correct_answer = "Paris"

    # evaluate single example
    result = evaluator.evaluate_single_example(
        question,
        llm_output,
        standard_answer_range,
        key_answer_type,
        correct_answer
    )
    print(f"Single example evaluation result: {result}")


def main():
    parser = argparse.ArgumentParser(
        description="Run evaluation examples for the xFinder model.")
    parser.add_argument('--run-example', action='store_true',
                        help="Run the example evaluation.")
    parser.add_argument('--model-name', type=str, default="xFinder-qwen1505",
                        help="The model name to be used for inference.")
    parser.add_argument('--inference-mode', type=str, default="local",
                        help="The mode of inference, either 'local' or 'api'.")
    parser.add_argument('--model-path-or-url', type=str,
                        default="IAAR-Shanghai/xFinder-qwen1505", help="The path or URL of the model.")
    parser.add_argument('--temperature', type=float, default=0.7,
                        help="The temperature value for sampling.")
    parser.add_argument('--max-tokens', type=int, default=100,
                        help="The maximum number of tokens to generate.")
    args = parser.parse_args()

    if args.run_example:
        run_example(
            model_name=args.model_name,
            inference_mode=args.inference_mode,
            model_path_or_url=args.model_path_or_url,
            temperature=args.temperature,
            max_tokens=args.max_tokens
        )


if __name__ == '__main__':
    main()
