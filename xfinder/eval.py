import argparse
import json
import sys

import yaml
from tqdm import tqdm

from .core import Comparator, Extractor
from .utils import DataProcessor


def check_config(config):
    if 'data_path' not in config:
        raise ValueError(
            "Error: 'data_path' not found in the configuration file.")
    if 'xfinder_model' not in config:
        raise ValueError(
            "Error: 'xfinder_model' not found in the configuration file.")
    if 'model_name' not in config['xfinder_model']:
        raise ValueError(
            "Error: 'model_name' of xfinder not found in the configuration file."
        )
    if 'model_path' not in config['xfinder_model'] and 'url' not in config[
            'xfinder_model']:
        raise ValueError(
            "Error: 'model_path' or 'url' of xfinder not found in the configuration file."
        )


def calc_acc(config_path: str) -> None:
    """Calculate the accuracy given the file to be evaluated.
    
    Args:
        config_path (str): Path to the configuration file.
    """
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
    check_config(config)

    data_processor = DataProcessor()
    extractor = Extractor(
        model_name=config['xfinder_model']['model_name'],
        model_path=config['xfinder_model']['model_path']
        if 'model_path' in config['xfinder_model'] else None,
        url=config['xfinder_model']['url']
        if 'url' in config['xfinder_model'] else None,
    )
    comparator = Comparator()

    # Get extracted answers
    ori_data = data_processor.read_data(config['data_path'])
    ext_cor_pairs = []
    for item in tqdm(ori_data):
        user_input = extractor.prepare_input(item)
        extracted_answer = extractor.gen_output(user_input)
        ext_cor_pairs.append([
            item["key_answer_type"], item["standard_answer_range"],
            extracted_answer, item["correct_answer"]
        ])

    results = comparator.compare_all(ext_cor_pairs)

    correct = sum(1 for result in results if result[-1] == True)
    total = max(len(results), 1)
    accuracy = correct / total if total else 0
    print(f"Accuracy: {accuracy:.4f}")
    return


def main():
    parser = argparse.ArgumentParser(description='Run xFinder evaluation.')
    parser.add_argument(
        'config_path',
        nargs='?',
        default=None,
        help='Path to the configuration file')
    args = parser.parse_args()

    config_path = args.config_path
    if not config_path:
        print("Error: No configuration path provided.")
        parser.print_help()
        return

    return calc_acc(config_path)


if __name__ == "__main__":
    main()
