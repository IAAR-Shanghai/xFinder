import json
import os
import random

import pandas as pd


RANDOM_SEED = 22
random.seed(RANDOM_SEED)

INPUT_DIR = './benchmark/raw_data'
OUTPUT_DIR = './benchmark/transformed_data'


def process_row(row, dataset=None, answer_type=None):
    """
    Process a row of data based on the specified dataset.
    This is a template function. Customize it based on your dataset requirements.
    """
    if dataset is None:
        return None

    # Example processing logic for a custom dataset
    if dataset == "CustomDataset":
        question_text = row.get('question', '')
        answer = row.get('answer', '')
        # Customize the following variables based on your needs
        key_answer_type = "custom"
        standard_answer_range = "custom range"

        return {'question': question_text,
                'key_answer_type': key_answer_type,
                'standard_answer_range': standard_answer_range,
                'correct_answer': answer}

    return None


def read_jsonl(file_path):
    """
    Read data from a JSONL file and return as a list of dictionaries.
    """
    data = []
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            data.append(json.loads(line))
    return data


def save_as_json(data, output_path):
    """
    Save data in JSON format to the specified file.
    """
    with open(output_path, 'w') as file:
        json.dump(data, file, indent=2)


def process_data(input_dir, output_dir, dataset=None, answer_type=None,
                 train_sample_size=2000, test_sample_size=1000, random_seed=RANDOM_SEED):
    """
    Process data from the specified dataset, split it into training and testing sets, and save the results in JSON format.
    """
    input_path = os.path.join(input_dir, dataset)
    if answer_type is not None:
        output_path = os.path.join(output_dir, f"{dataset}_{answer_type}")
    else:
        output_path = os.path.join(output_dir, dataset)

    # Create output directory if it does not exist
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    # Example data loading logic for a custom dataset
    train_data = pd.DataFrame(read_jsonl(
        os.path.join(input_path, 'train.jsonl')))
    test_data = pd.DataFrame(read_jsonl(
        os.path.join(input_path, 'test.jsonl')))

    # Process and save data in JSON format
    train_json = [process_row(row, dataset=dataset, answer_type=answer_type)
                  for _, row in train_data.iterrows() if process_row(row, dataset=dataset, answer_type=answer_type) is not None]
    test_json = [process_row(row, dataset=dataset, answer_type=answer_type)
                 for _, row in test_data.iterrows() if process_row(row, dataset=dataset, answer_type=answer_type) is not None]

    # Sample data based on specified sizes
    train_json = train_json[:min(train_sample_size, len(train_json))]
    test_json = test_json[:min(test_sample_size, len(test_json))]
    print(
        f"The dataset: {dataset} contains {len(train_json)} samples for training and {len(test_json)} samples for testing.")

    save_as_json(train_json, os.path.join(output_path, 'train.json'))
    save_as_json(test_json, os.path.join(output_path, 'test.json'))


if __name__ == "__main__":
    # Example usage of the process_data function for a custom dataset
    process_data(input_dir=INPUT_DIR, output_dir=OUTPUT_DIR,
                 dataset="CustomDataset",  # Change this to your dataset name
                 answer_type="custom"  # Change this to your answer type if applicable
                 )
