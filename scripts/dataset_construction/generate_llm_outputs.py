import argparse
import copy
import datetime
import json
import os
from multiprocessing import Pool

import yaml
from loguru import logger
from tqdm import tqdm
from utils.dataset_loader import DatasetLoader
from utils.llms import LargeLanguageModels

DATA_DIR = "./benchmark/transformed_data"
DATA_CONF_PATH = "./utils/data_conf.yaml"
OUTPUT_DIR = "./llm_outputs"
SEED = 22


def load_conf(conf_path):
    with open(conf_path, 'r') as f:
        conf = yaml.safe_load(f)
    return conf


class GenLLMOutputs:
    """Generate outputs from large language models for a given dataset."""

    def __init__(self,
                 model: LargeLanguageModels,
                 data_name: str,
                 data_size: int,
                 num_samples: int,
                 prompt_type: str,
                 process_num: int = 1,
                 output_dir: str = OUTPUT_DIR,
                 seed: int = SEED):

        self.model = copy.deepcopy(model)
        self.model_name = model.params['model_name']
        self.data_name = data_name
        self.data_conf = data_conf = load_conf(DATA_CONF_PATH)[data_name]
        self.data_size = data_size
        self.num_samples = num_samples
        self.prompt_type = prompt_type
        self.setting_name = prompt_type.replace('few', f"{self.num_samples}")
        data_name = data_conf['data_name']
        model_name = model.params['model_name']
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        output_name = f'{self.setting_name}_{data_name}_{model_name}_{timestamp}.json'
        self.output_path = os.path.join(output_dir, output_name)
        self.process_num = process_num
        self.seed = seed

    def evaluator_info(self):
        return {
            'setting': self.setting_name,
            'llm': self.model.params,
            'dataset': self.data_conf,
            'datetime': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        }

    def gen(self, data_point):
        try:
            result = self.model.generate(
                self.data_conf, data_point, self.fewshot_data, self.prompt_type)
        except Exception as e:
            result = ''
            logger.warning(repr(e))

        return {
            "question": data_point['question'],
            "key_answer_type": data_point['key_answer_type'],
            "standard_answer_range": data_point['standard_answer_range'],
            "correct_answer": data_point['correct_answer'],
            "llm_output": result
        }

    def batch_gen(self, dataset):
        with Pool(self.process_num) as pool:
            results = list(tqdm(
                pool.imap(self.gen, dataset),
                total=len(dataset),
                desc=self.model.params['model_name']
            ))
        return results

    def save_output(self, output: dict):
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
        with open(self.output_path, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=4)

    def run(self):
        info = self.evaluator_info()

        data_path = os.path.join(
            DATA_DIR, self.data_conf['data_name'], 'test.json')
        sample_path = os.path.join(
            DATA_DIR, self.data_conf['data_name'], 'train.json')

        dataset = DatasetLoader.load(data_path, self.data_size, self.seed)
        self.fewshot_data = DatasetLoader.load(
            sample_path, self.num_samples, self.seed)

        results = self.batch_gen(dataset)
        self.save_output({'info': info, 'results': results})


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--model', type=str, default=None)
    parser.add_argument('--model_url', type=str, default=None)
    parser.add_argument('--data_size', type=int, default=10)
    parser.add_argument('--num_samples', type=int, default=5)
    parser.add_argument('--prompt_type', type=str, default='few_shot')
    parser.add_argument('--process_num', type=int, default=1)
    args = parser.parse_args()

    model = getattr(__import__(
        'utils.llms', fromlist=[args.model]), args.model)(url=args.model_url)

    GenLLMOutputs(
        model=model,
        data_name=args.data_name,
        data_size=args.data_size,
        num_samples=args.num_samples,
        prompt_type=args.prompt_type,
        process_num=args.process_num
    ).run()
