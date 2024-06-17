import json
import os
import random
import re
import string

import pandas as pd
from sklearn.model_selection import train_test_split

RANDOM_SEED = 22
random.seed(RANDOM_SEED)

INPUT_DIR = 'raw_data'
OUTPUT_DIR = 'transformed_data'


def generate_random_text():
    """
    Generate random text of a specified length.
    """
    length = random.randint(5, 20)
    gen_text = ''.join(random.choices(string.printable, k=length))
    gen_text = gen_text.replace('\n', '')
    return gen_text


def process_row(row, dataset=None, answer_type=None):
    """
    Process a row of data based on the specified dataset.
    """
    if dataset is None:
        return None

    if dataset == "GSM8K":
        question_text = row.get('question', '')
        answer = row.get('answer', '')
        answer_detail, answer_text = '', ''
        key_answer_type = "math"
        standard_answer_range = "a(n) number / set / vector / matrix / interval / expression / function / equation / inequality"

        if '####' in answer:
            answer_detail, answer_text = map(
                str.strip, answer.split('####', 1))

        return {'question': question_text,
                'key_answer_type': key_answer_type,
                'standard_answer_range': standard_answer_range,
                'answer_detail': answer_detail,
                'correct_answer': answer_text}

    elif dataset == "MMLU":
        question = row.get(0, '')
        choice_text = [row.get(1, ''), row.get(
            2, ''), row.get(3, ''), row.get(4, '')]
        choice_alpha = ['A', 'B', 'C', 'D']
        answer_text = row.get(5, '')
        if answer_type == "alpha":
            question_text = f"{question} Answer Choices: (A) {choice_text[0]} (B) {choice_text[1]} (C) {choice_text[2]} (D) {choice_text[3]}"
            answer_text = f"{answer_text}"
            key_answer_type = "alphabet_option"
            standard_answer_range = list(zip(choice_alpha, choice_text))

            return {'question': question_text,
                    'key_answer_type': key_answer_type,
                    'standard_answer_range': standard_answer_range,
                    'correct_answer': answer_text}

        elif answer_type == "text":
            question_text = f"{question} Answer Choices: {choice_text[0]} / {choice_text[1]} / {choice_text[2]} / {choice_text[3]}"
            key_answer_type = "short_text"
            standard_answer_range = choice_text
            answer_text = choice_text[ord(answer_text)-65]

            return {'question': question_text,
                    'key_answer_type': key_answer_type,
                    'standard_answer_range': standard_answer_range,
                    'correct_answer': answer_text}

        # Randomly remove one of the choices, add a new choice or add two new choices
        elif answer_type == "enh":

            # Get the correct choice
            correct_text = choice_text[ord(answer_text)-65]
            correct_alpha = choice_alpha[ord(answer_text)-65]

            rand_num = random.choice([-1, 1, 2])
            if rand_num == -1:
                # Remove the correct choice
                choice_text = choice_text[:ord(
                    answer_text)-65] + choice_text[ord(answer_text)-65+1:]
                choice_alpha = choice_alpha[:ord(
                    answer_text)-65] + choice_alpha[ord(answer_text)-65+1:]

                # Randomly remove one of the choices
                rand_num = random.randint(0, len(choice_text)-1)
                choice_text.pop(rand_num)
                choice_alpha.pop(rand_num)

                # Add the correct choice back
                choice_text.append(correct_text)
                choice_alpha.append(correct_alpha)

                # Sort the choices
                sorted_choice = sorted(
                    enumerate(choice_alpha), key=lambda x: x[1])
                choice_alpha = [choice_alpha for _,
                                choice_alpha in sorted_choice]
                indices = [index for index, _ in sorted_choice]
                choice_text = [choice_text[i] for i in indices]
            elif rand_num == 1:
                choice_text.extend([generate_random_text()])
                choice_alpha.extend(['E'])
            elif rand_num == 2:
                choice_text.extend(
                    [generate_random_text(), generate_random_text()])
                choice_alpha.extend(['E', 'F'])

            # Shuffle the choices
            indices = list(range(len(choice_text)))
            random.shuffle(indices)
            choice_text = [choice_text[i] for i in indices]

            choice_alpha = [
                f"{chr(65 + i)}" for i in range(len(choice_text))]
            correct_alpha = choice_alpha[choice_text.index(correct_text)]

            answer_choices = [f"{alpha} {text}" for alpha,
                              text in zip(choice_alpha, choice_text)]

            question_text = f"{question} Answer Choices: {' '.join(answer_choices)}"

            key_answer_type = "alphabet_option"
            standard_answer_range = list(zip(choice_alpha, choice_text))

            return {'question': question_text,
                    'key_answer_type': key_answer_type,
                    'standard_answer_range': standard_answer_range,
                    'correct_answer': answer_text}

    elif "ARC" in dataset:
        question = row.get('question', '')['stem']
        choice_text = [choice["text"]
                       for choice in row.get('question', '')['choices']]
        choice_alpha = [f"{choice['label']}" for choice in row.get(
            'question', '')['choices']]
        answer_text = row.get('answerKey', '')
        if not answer_text.isalpha():
            return None
        if answer_type == "alpha":
            answer_choices = [f"{alpha} {text}" for alpha,
                              text in zip(choice_alpha, choice_text)]
            question_text = f"{question} Answer Choices: {' '.join(answer_choices)}"
            answer_text = f"{answer_text}"
            key_answer_type = "alphabet_option"
            standard_answer_range = list(zip(choice_alpha, choice_text))

            return {'question': question_text,
                    'key_answer_type': key_answer_type,
                    'standard_answer_range': standard_answer_range,
                    'correct_answer': answer_text}

        elif answer_type == "text":
            question_text = f"{question} Answer Choices: {' / '.join(choice_text)}"
            key_answer_type = "short_text"
            standard_answer_range = choice_text
            answer_text = choice_text[ord(answer_text)-65]

            return {'question': question_text,
                    'key_answer_type': key_answer_type,
                    'standard_answer_range': standard_answer_range,
                    'correct_answer': answer_text}

        elif answer_type == "enh":
            # Get the correct choice
            correct_text = choice_text[ord(answer_text)-65]
            correct_alpha = choice_alpha[ord(answer_text)-65]

            # Randomly remove one of the choices, add a new choice or add two new choices
            rand_num = random.choice([-1, 1, 2])
            if rand_num == -1:
                # Remove the correct choice
                choice_text = choice_text[:ord(
                    answer_text)-65] + choice_text[ord(answer_text)-65+1:]
                choice_alpha = choice_alpha[:ord(
                    answer_text)-65] + choice_alpha[ord(answer_text)-65+1:]

                # Randomly remove one of the choices
                rand_num = random.randint(0, len(choice_text)-1)
                choice_text.pop(rand_num)
                choice_alpha.pop(rand_num)

                # Add the correct choice back
                choice_text.append(correct_text)
                choice_alpha.append(correct_alpha)

                # Sort the choices
                sorted_choice = sorted(
                    enumerate(choice_alpha), key=lambda x: x[1])
                choice_alpha = [choice_alpha for _,
                                choice_alpha in sorted_choice]
                indices = [index for index, _ in sorted_choice]
                choice_text = [choice_text[i] for i in indices]
            elif rand_num == 1:  # Add a new choice
                choice_text.extend([generate_random_text()])
                choice_alpha.extend(['E'])
            elif rand_num == 2:  # Add two new choices
                choice_text.extend(
                    [generate_random_text(), generate_random_text()])
                choice_alpha.extend(['E', 'F'])

            # Shuffle the choices
            indices = list(range(len(choice_text)))
            random.shuffle(indices)
            choice_text = [choice_text[i] for i in indices]
            # Get the correct choice
            choice_alpha = [
                f"{chr(65 + i)}" for i in range(len(choice_text))]
            correct_alpha = choice_alpha[choice_text.index(correct_text)]

            answer_choices = [f"{alpha} {text}" for alpha,
                              text in zip(choice_alpha, choice_text)]

            question_text = f"{question} Answer Choices: {' '.join(answer_choices)}"
            key_answer_type = "alphabet_option"
            standard_answer_range = list(zip(choice_alpha, choice_text))

            return {'question': question_text,
                    'key_answer_type': key_answer_type,
                    'standard_answer_range': standard_answer_range,
                    'correct_answer': answer_text}

    elif "CommonsenseQA" in dataset:
        question = row.get('question', '')['stem']
        choice_text = [choice["text"]
                       for choice in row.get('question', '')['choices']]
        choice_alpha = [f"{choice['label']}" for choice in row.get(
            'question', '')['choices']]
        if answer_type == "alpha":
            question_text = f"{question} Answer Choices: (A) {choice_text[0]} (B) {choice_text[1]} (C) {choice_text[2]} (D) {choice_text[3]} (E) {choice_text[4]}"
            answer_text = f"{row.get('answerKey', '')}"
            key_answer_type = "alphabet_option"
            standard_answer_range = list(zip(choice_alpha, choice_text))

            return {'question': question_text,
                    'key_answer_type': key_answer_type,
                    'standard_answer_range': standard_answer_range,
                    'correct_answer': answer_text}

        elif answer_type == "text":
            # "Which is true about reproduction in both a euglena and a paramecium?  Answer Choices:  / They divide vertically.  / They produce gametes. / They conjugate. / They form spores."
            question_text = f"{question} Answer Choices: {choice_text[0]} / {choice_text[1]} / {choice_text[2]} / {choice_text[3]} / {choice_text[4]}"
            key_answer_type = "short_text"
            standard_answer_range = choice_text
            answer_key = row.get('answerKey', '')
            for choice in row.get('question', '')['choices']:
                if choice["label"] == answer_key:
                    answer_text = choice["text"]
                    break

            return {'question': question_text,
                    'key_answer_type': key_answer_type,
                    'standard_answer_range': standard_answer_range,
                    'correct_answer': answer_text}

    elif "OpenbookQA" in dataset:
        question = row.get('question', '')['stem']
        choice_text = [choice["text"]
                       for choice in row.get('question', '')['choices']]
        choice_alpha = [f"{choice['label']}" for choice in row.get(
            'question', '')['choices']]
        if answer_type == "alpha":
            question_text = f"{question} Answer Choices: (A) {choice_text[0]} (B) {choice_text[1]} (C) {choice_text[2]} (D) {choice_text[3]}"
            answer_text = f"{row.get('answerKey', '')}"
            key_answer_type = "alphabet_option"
            standard_answer_range = list(zip(choice_alpha, choice_text))

            return {'question': question_text,
                    'key_answer_type': key_answer_type,
                    'standard_answer_range': standard_answer_range,
                    'correct_answer': answer_text}

        elif answer_type == "text":
            question_text = f"{question} Answer Choices: {choice_text[0]} / {choice_text[1]} / {choice_text[2]} / {choice_text[3]}"
            key_answer_type = "short_text"
            standard_answer_range = choice_text
            answer_key = row.get('answerKey', '')
            for choice in row.get('question', '')['choices']:
                if choice["label"] == answer_key:
                    answer_text = choice["text"]
                    break

            return {'question': question_text,
                    'key_answer_type': key_answer_type,
                    'standard_answer_range': standard_answer_range,
                    'correct_answer': answer_text}

    elif "SIQA" in dataset:
        context = row.get('context', '')
        question = row.get('question', '')
        answer_a = row.get('answerA', '')
        answer_b = row.get('answerB', '')
        answer_c = row.get('answerC', '')
        choice_alpha = ['A', 'B', 'C']
        choice_text = [answer_a, answer_b, answer_c]
        if answer_type == "alpha":
            question_text = f"{context} {question} Answer Choices: (A) {answer_a} (B) {answer_b} (C) {answer_c}"
            answer_text = f"{choice_alpha[int(row.get('label_index', ''))-1]}"
            key_answer_type = "alphabet_option"
            standard_answer_range = list(zip(choice_alpha, choice_text))

            return {'question': question_text,
                    'key_answer_type': key_answer_type,
                    'standard_answer_range': standard_answer_range,
                    'correct_answer': answer_text}

        elif answer_type == "text":
            question_text = f"{context} {question} Answer Choices: {answer_a} / {answer_b} / {answer_c}"
            key_answer_type = "short_text"
            standard_answer_range = choice_text
            answer_key = row.get('label_index', '')
            answer_text = choice_text[int(answer_key)-1]

            return {'question': question_text,
                    'key_answer_type': key_answer_type,
                    'standard_answer_range': standard_answer_range,
                    'correct_answer': answer_text}

    elif "MetaMathQA" in dataset:
        question_text = row.get('query', '')
        response = row.get('response', '')
        key_answer_type = "math"
        standard_answer_range = "a(n) number / set / vector / matrix / interval / expression / function / equation / inequality"
        answer_detail = response.split('####')[0] if '####' in response else ''
        answer_text = response.split('The answer is:')[
            1].strip() if 'The answer is:' in response else ''

        return {'question': question_text,
                'key_answer_type': key_answer_type,
                'standard_answer_range': standard_answer_range,
                'answer_detail': answer_detail,
                'correct_answer': answer_text}

    elif "hellaswag" in dataset:
        context = row.get('ctx_a', '')
        choice_text = row.get('ending_options', '')
        choice_alpha = ['A', 'B', 'C', 'D']
        if answer_type == "alpha":
            question_text = f"{context} ...  Answer Choices: (A) {choice_text[0]} (B) {choice_text[1]} (C) {choice_text[2]} (D) {choice_text[3]}"
            answer_text = f"{choice_alpha[int(row.get('label_index', ''))]}"
            key_answer_type = "alphabet_option"
            standard_answer_range = list(zip(choice_alpha, choice_text))

            return {'question': question_text,
                    'key_answer_type': key_answer_type,
                    'standard_answer_range': standard_answer_range,
                    'correct_answer': answer_text}

    elif "BoolQ" in dataset:
        passage = row.get('passage', '')
        question = row.get('question', '')

        answer_text = 'Yes' if row.get('answer', '') == True else 'No'
        question_text = f"{question} passage: {passage} Yes or No?"
        key_answer_type = "categorical_label"
        standard_answer_range = ['Yes', 'No']

        return {'question': question_text,
                'key_answer_type': key_answer_type,
                'standard_answer_range': standard_answer_range,
                'correct_answer': answer_text}

    elif "WiC" in dataset:
        target = row.get('target', '')
        sentence1 = row.get('sentence1', '')
        sentence2 = row.get('sentence2', '')
        answer_text = 'True' if row.get('label', '') == 'T' else 'False'

        question_text = f"Please identify the target word: '{target}'.   whether it has the same meaning in the two sentences. Sentence 1: {sentence1} Sentence 2: {sentence2} True or False?"
        key_answer_type = "categorical_label"
        standard_answer_range = ['True', 'False']

        return {'question': question_text,
                'key_answer_type': key_answer_type,
                'standard_answer_range': standard_answer_range,
                'correct_answer': answer_text}

    elif "MATH" in dataset:
        question_text = row.get('problem', '')
        question_level = row.get('level', '')
        question_type = row.get('type', '')
        answer_detail = row.get('solution', '')
        key_answer_type = "math"
        standard_answer_range = "a(n) number / set / vector / matrix / interval / expression / function / equation / inequality"

        match = re.search(
            r'\\boxed\{([^{}]*(?:{[^{}]*}[^{}]*)*)\}', answer_detail, re.DOTALL)
        if match:
            answer_text = f"\\boxed{{{match.group(1)}}}"
        else:
            answer_text = ''
            return None

        return {'question': question_text,
                'question_level': question_level,
                'question_type': question_type,
                'key_answer_type': key_answer_type,
                'standard_answer_range': standard_answer_range,
                'answer_detail': answer_detail,
                'correct_answer': answer_text}

    elif "MultiArith" in dataset:
        question_text = row.get('question', '')
        answer_text = row.get('final_ans', '')
        key_answer_type = "math"
        standard_answer_range = "a(n) number / set / vector / matrix / interval / expression / function / equation / inequality"

        return {'question': question_text,
                'key_answer_type': key_answer_type,
                'standard_answer_range': standard_answer_range,
                'correct_answer': answer_text}

    return None


def read_jsonl(file_path):
    data = []
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            data.append(json.loads(line))
    return data


def find_json_files_with_content(dir):
    json_contents = []
    for root, _, files in os.walk(dir):
        for file in files:
            if file.endswith('.json'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r') as f:
                    json_content = json.load(f)
                    json_contents.append(json_content)
    return json_contents


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

    train_data, test_data = None, None
    if dataset == "GSM8K":
        files = os.listdir(input_path)
        for file in files:
            file_path = os.path.join(input_path, file)
            if "train" in file:
                train_data = pd.read_parquet(file_path)
            elif "test" in file:
                test_data = pd.read_parquet(file_path)
    if dataset == "MMLU":
        train_concat, test_concat = pd.DataFrame(), pd.DataFrame()
        file_paths = [item for item in os.listdir(
            input_path) if os.path.isdir(os.path.join(input_path, item))]
        for item in file_paths:
            if ('train' in item) or ('dev' in item):
                train_files = [file for file in os.listdir(
                    os.path.join(input_path, item)) if file.endswith('.csv')]
                for train_file in train_files:
                    file_path = os.path.join(input_path, item, train_file)
                    data = pd.read_csv(file_path, header=None)
                    train_concat = pd.concat(
                        [train_concat, data], ignore_index=True)
                    train_data = train_concat
            if ('test' in item) or ('val' in item):
                test_files = [file for file in os.listdir(
                    os.path.join(input_path, item)) if file.endswith('.csv')]
                for test_file in test_files:
                    file_path = os.path.join(input_path, item, test_file)
                    data = pd.read_csv(file_path, header=None)
                    test_concat = pd.concat(
                        [test_concat, data], ignore_index=True)
                    test_data = test_concat
    if "ARC" in dataset:
        # Find relevant files containing 'Train', 'Test', and 'Dev' in their filenames
        train_data = pd.DataFrame(read_jsonl(
            os.path.join(input_path, next(file for file in os.listdir(
                input_path) if 'Train' in file and file.endswith('.jsonl')))
        ))

        test_data = pd.DataFrame(read_jsonl(
            os.path.join(input_path, next(file for file in os.listdir(
                input_path) if 'Test' in file and file.endswith('.jsonl')))
        ))
        dev_data = pd.DataFrame(read_jsonl(
            os.path.join(input_path, next(file for file in os.listdir(
                input_path) if 'Dev' in file and file.endswith('.jsonl')))
        ))

        # Concatenate train and dev data
        train_data = pd.concat([train_data, dev_data], ignore_index=True)

    if "CommonsenseQA" in dataset:
        train_data = pd.DataFrame(read_jsonl(
            os.path.join(input_path, 'train_rand_split.jsonl')))
        test_data = pd.DataFrame(read_jsonl(
            os.path.join(input_path, 'dev_rand_split.jsonl')))

    if "OpenbookQA" in dataset:
        train_data = pd.DataFrame(read_jsonl(
            os.path.join(input_path, 'train.jsonl')))
        test_data = pd.DataFrame(read_jsonl(
            os.path.join(input_path, 'test.jsonl')))
        dev_data = pd.DataFrame(read_jsonl(
            os.path.join(input_path, 'dev.jsonl')))
        # Concatenate train and dev data
        train_data = pd.concat([train_data, dev_data], ignore_index=True)

    if "SIQA" in dataset:
        train_data = pd.DataFrame(read_jsonl(
            os.path.join(input_path, 'train.jsonl')))
        test_data = pd.DataFrame(read_jsonl(
            os.path.join(input_path, 'dev.jsonl')))
        train_label = pd.DataFrame(read_jsonl(
            os.path.join(input_path, 'train-labels.lst')))
        test_label = pd.DataFrame(read_jsonl(
            os.path.join(input_path, 'dev-labels.lst')))

        train_data['label_index'] = train_label
        test_data['label_index'] = test_label

    if "MetaMathQA" in dataset:
        # read data
        with open(os.path.join(input_path, 'MetaMathQA-395K.json'), 'r') as f:
            meta_data = json.load(f)
        # split data
        train_data, test_data = train_test_split(
            meta_data, test_size=0.2, random_state=random_seed)

        train_data = pd.DataFrame(train_data)
        test_data = pd.DataFrame(test_data)

    if "hellaswag" in dataset:
        train_data = pd.DataFrame(read_jsonl(
            os.path.join(input_path, 'train.jsonl')))
        test_data = pd.DataFrame(read_jsonl(
            os.path.join(input_path, 'valid.jsonl')))

        train_label = pd.DataFrame(read_jsonl(
            os.path.join(input_path, 'train-labels.lst')))
        test_label = pd.DataFrame(read_jsonl(
            os.path.join(input_path, 'valid-labels.lst')))

        train_data['label_index'] = train_label
        test_data['label_index'] = test_label

    if "BoolQ" in dataset:
        train_data = pd.DataFrame(read_jsonl(
            os.path.join(input_path, 'train.jsonl')))
        test_data = pd.DataFrame(read_jsonl(
            os.path.join(input_path, 'dev.jsonl')))

    if "WiC" in dataset:
        train_data = []

        with open(os.path.join(input_path, 'train/train.data.txt'), 'r') as f:
            for line in f:
                columns = line.strip().split('\t')
                if len(columns) >= 5:
                    train_data.append((columns[0], columns[3], columns[4]))

        with open(os.path.join(input_path, 'train/train.gold.txt'), 'r') as f:
            train_label = f.readlines()

        train_data = pd.DataFrame(
            train_data, columns=['target', 'sentence1', 'sentence2'])
        train_data['label'] = [item.strip("\n") for item in train_label]

        test_data = []
        with open(os.path.join(input_path, 'dev/dev.data.txt'), 'r') as f:
            for line in f:
                columns = line.strip().split('\t')
                if len(columns) >= 5:
                    test_data.append((columns[0], columns[3], columns[4]))

        with open(os.path.join(input_path, 'dev/dev.gold.txt'), 'r') as f:
            test_label = f.readlines()

        test_data = pd.DataFrame(
            test_data, columns=['target', 'sentence1', 'sentence2'])
        test_data['label'] = [item.strip("\n") for item in test_label]

    if "MATH" in dataset:

        train_data = find_json_files_with_content(
            os.path.join(input_path, 'train'))
        train_data = pd.DataFrame(train_data)

        test_data = find_json_files_with_content(
            os.path.join(input_path, 'test'))
        test_data = pd.DataFrame(test_data)

    if "MultiArith" in dataset:
        with open(os.path.join(input_path, 'train.json'), 'r') as f:
            train_data = json.load(f)
        with open(os.path.join(input_path, 'test.json'), 'r') as f:
            test_data = json.load(f)

        train_data = pd.DataFrame(train_data)
        test_data = pd.DataFrame(test_data)

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

    process_data(input_dir=INPUT_DIR, output_dir=OUTPUT_DIR,
                 dataset="GSM8K")

    process_data(input_dir=INPUT_DIR, output_dir=OUTPUT_DIR,
                 dataset="MMLU", answer_type="alpha")
    process_data(input_dir=INPUT_DIR, output_dir=OUTPUT_DIR,
                 dataset="MMLU", answer_type="text")
    process_data(input_dir=INPUT_DIR, output_dir=OUTPUT_DIR,
                 dataset="MMLU", answer_type="enh")

    process_data(input_dir=INPUT_DIR, output_dir=OUTPUT_DIR,
                 dataset="ARC-c", answer_type="alpha")
    process_data(input_dir=INPUT_DIR, output_dir=OUTPUT_DIR,
                 dataset="ARC-c", answer_type="text")
    process_data(input_dir=INPUT_DIR, output_dir=OUTPUT_DIR,
                 dataset="ARC-c", answer_type="enh")

    process_data(input_dir=INPUT_DIR, output_dir=OUTPUT_DIR,
                 dataset="ARC-e", answer_type="alpha")
    process_data(input_dir=INPUT_DIR, output_dir=OUTPUT_DIR,
                 dataset="ARC-e", answer_type="text")
    process_data(input_dir=INPUT_DIR, output_dir=OUTPUT_DIR,
                 dataset="ARC-e", answer_type="enh")

    process_data(input_dir=INPUT_DIR, output_dir=OUTPUT_DIR,
                 dataset="CommonsenseQA", answer_type="alpha")
    process_data(input_dir=INPUT_DIR, output_dir=OUTPUT_DIR,
                 dataset="CommonsenseQA", answer_type="text")

    process_data(input_dir=INPUT_DIR, output_dir=OUTPUT_DIR,
                 dataset="OpenbookQA", answer_type="alpha")
    process_data(input_dir=INPUT_DIR, output_dir=OUTPUT_DIR,
                 dataset="OpenbookQA", answer_type="text")

    process_data(input_dir=INPUT_DIR, output_dir=OUTPUT_DIR,
                 dataset="SIQA", answer_type="alpha")
    process_data(input_dir=INPUT_DIR, output_dir=OUTPUT_DIR,
                 dataset="SIQA", answer_type="text")

    process_data(input_dir=INPUT_DIR, output_dir=OUTPUT_DIR,
                 dataset="MetaMathQA")

    process_data(input_dir=INPUT_DIR, output_dir=OUTPUT_DIR,
                 dataset="hellaswag", answer_type="alpha")

    process_data(input_dir=INPUT_DIR, output_dir=OUTPUT_DIR,
                 dataset="BoolQ")

    process_data(input_dir=INPUT_DIR, output_dir=OUTPUT_DIR,
                 dataset="WiC")

    process_data(input_dir=INPUT_DIR, output_dir=OUTPUT_DIR,
                 dataset="MATH")

    process_data(input_dir=INPUT_DIR, output_dir=OUTPUT_DIR,
                 dataset="MultiArith")
