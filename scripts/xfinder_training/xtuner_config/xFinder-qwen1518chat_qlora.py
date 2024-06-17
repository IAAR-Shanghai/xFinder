# Copyright (c) OpenMMLab. All rights reserved.
import torch
from datasets import load_dataset
from mmengine.dataset import DefaultSampler
from mmengine.hooks import (CheckpointHook, DistSamplerSeedHook, IterTimerHook,
                            LoggerHook, ParamSchedulerHook)
from mmengine.optim import AmpOptimWrapper, CosineAnnealingLR, LinearLR
from peft import LoraConfig
from torch.optim import AdamW
from transformers import (AutoModelForCausalLM, AutoTokenizer,
                          BitsAndBytesConfig)

from xtuner.dataset import process_hf_dataset
from xtuner.dataset.collate_fns import default_collate_fn
from xtuner.dataset.map_fns import alpaca_map_fn, template_map_fn_factory
from xtuner.engine.hooks import (DatasetInfoHook, EvaluateChatHook,
                                 VarlenAttnArgsToMessageHubHook)
from xtuner.engine.runner import TrainLoop
from xtuner.model import SupervisedFinetune
from xtuner.utils import PROMPT_TEMPLATE, SYSTEM_TEMPLATE

# import time
from mmengine.visualization.vis_backend import WandbVisBackend
from mmengine.visualization.visualizer import Visualizer
#######################################################################
#                          PART 1  Settings                           #
#######################################################################
# Model
pretrained_model_name_or_path = 'path/to/models/Qwen1.5-1.8B-Chat'
use_varlen_attn = False

# Data
data_path = 'path/to/dataset/ft_data/train_v1_xtuner.json'
prompt_template = PROMPT_TEMPLATE.qwen_chat
max_length = 2048
pack_to_max_length = True

# Scheduler & Optimizer
batch_size = 1  # per_device
accumulative_counts = 16
dataloader_num_workers = 0
max_epochs = 3
optim_type = AdamW
lr = 2e-4
betas = (0.9, 0.999)
weight_decay = 0
max_norm = 1  # grad clip
warmup_ratio = 0.03

# Save
save_steps = 500
save_total_limit = 1  # Maximum checkpoints to keep (-1 means unlimited)

# Evaluate the generation performance during the training
evaluation_freq = 500
# SYSTEM = SYSTEM_TEMPLATE.alpaca
SYSTEM = "You are a help assistant tasked with extracting the precise key answer from given output sentences. You must only provide the extracted key answer without including any additional text. The types of answers may vary; they can be numeric values, option letters, or short texts.\nEach time, the user will supply output sentences along with an answer range. The output sentences are the response to a certain question. The answer range could either describe the type of answer expected or list all possible valid answers. Using the information provided, you must accurately and precisely determine and extract the intended key answer from the output sentences.\nIf the output sentences present multiple different answers, carefully determine if the later provided answer is a correction or modification of a previous one. If so, extract this corrected or modified answer as the final response. Conversely, if the output sentences fluctuate between multiple answers without a clear final answer, you should output [No valid answer].\nAdditionally, if the answer range is a list and the answer given in the output sentences is not included in the answer range, also output [No valid answer]."

evaluation_inputs = [
    "Question: \"\"\"Lindsay is doing the laundry, and thinks she has missed some socks. There are 50 socks that need washing. If she washes 10 pairs of socks and 15 loose socks, how many socks has Lindsay missed?\"\"\"\n\nOutput sentences: \"\"\"\n\nTo solve this problem, we need to determine the value of x, which represents the number of socks that Lindsay missed.\nLet's break down the information given:\nNumber of socks that need washing: 50\nNumber of pairs of socks washed: 10\nNumber of loose socks washed: 15\nWe can set up the equation as follows:\nNumber of socks washed + Number of socks missed = Total number of socks\n(10 * 2) + 15 + x = 50\nLet's simplify and solve for x:\n20 + 15 + x = 50\nTo isolate x, we subtract 35 from both sides of the equation:\n20 + 15 + x - 35 = 50 - 35\nx = 15\nThe value of x is 15.\n#### 15\nThe answer is 15\"\"\"\n\nAnswer range: a(n) number / set / vector / matrix / interval / expression / function / equation / inequality\n\nKey extracted answer: ",
    "Question: \"\"\"Rose went to the store on Monday and bought 4 cakes. Tuesday she went to a different store and bought three times that number of cakes. On Wednesday she went to another store and bought 5 times the number of cakes she did on Tuesday. How many cakes did she buy after all three days?\"\"\"\n\nOutput sentences: \"\"\" The answer is <answer>.\n\nQ: A family is going on a trip. They have two children and two parents. The parents want to take their children to a museum, an amusement park, and a zoo. The museum costs $15 per person, the amusement park costs $25 per person, and the zoo costs $10 per person. How much will it cost for the family to go on their trip?\nA: \n\nEnd your final answer with 'The answer is <answer>.'\nOutput: The answer is <answer>.\n\nQ: The price of a dozen apples is $5. The price of a dozen oranges is $7. The price of a dozen bananas is $3. The price of a dozen pears is $6. The price of a dozen grapes is $4. If you buy 3 apples, 2 oranges, 1 banana, and 2 pears, how much will you spend?\nA: \n\nEnd your final answer with 'The answer is <answer>.'\nOutput: The answer is <answer>.\n\nQ: The cost of one movie ticket is $7. The cost of one bag of popcorn is $3. The cost of one soda is $2. The cost of one candy is $1. If you buy 2 movie tickets, 2 bags of popcorn, 2 sodas, and 2 candies, how much will you spend?\nA: \n\nEnd your final answer with 'The answer is <answer>.'\nOutput: The answer is <answer>.\n\nQ: The cost of a shirt is $20. The cost of a pair of jeans is $30. The cost of a hat is $10. The cost of a pair of shoes is $50. How much will you spend if you buy one shirt, one pair of jeans, one hat, and one pair of shoes?\nA: \n\nEnd your final answer with 'The answer is <answer>.'\nOutput: The answer is <answer>.\n\nQ: The cost of a slice of pizza is $3. The cost of a slice of cake is $2. The cost of a scoop of ice cream is $4. The cost of a hot dog is $5. How much will you spend if you buy 2 slices of pizza, 1 slice of cake, 2 scoops of ice cream, and 1 hot dog?\nA: \n\nEnd your final answer with 'The answer is <answer>.'\nOutput: The answer is <answer>.\n\nQ: The cost of a hamburger is $3. The cost of a hot dog is $2. The cost of a french fry is $1. The cost of a soda is $2. How much will you spend if you buy 1 hamburger, 1 hot dog, 2 french fries, and 1 soda?\nA: \n\nEnd your final answer with 'The answer is <answer>.'\nOutput: The answer is <answer>.\n\nQ: The cost of a movie ticket is $10. The cost of a bag of popcorn is $4. The cost of a soda is $3. The cost of a candy is $2. How much will you spend if you buy 2 movie tickets, 1 bag of popcorn, 2 sodas, and 3 candies?\nA: \n\nEnd your final answer with 'The answer is <answer>.'\nOutput: The answer is <answer>.\n\nQ: The cost of a slice of pizza is $3. The cost of a slice of cake is $2. The cost of a scoop of ice cream is $4. The cost of a hot dog is $5. How much will you spend if you buy 3 slices of pizza, 1 slice of cake, 2 scoops of ice cream, and 2 hot dogs?\nA: \n\nEnd your final answer with 'The answer is <answer>.'\nOutput: The answer is <answer>.\n\nQ: The cost of a hamburger is $3. The cost of a hot dog is $2. The cost of a french fry is $1. The cost of a soda is $2. How much will you spend if you buy 4 hamburgers, 1 hot dog, 4 french fries, and 2 sodas?\nA: \n\nEnd your final answer with 'The answer is <answer>.'\nOutput: The answer is <answer>.\n\nQ: The cost of a slice of pizza is $3. The cost of a slice of cake is $2. The cost of a scoop of ice cream is $4. The cost of a hot dog is $5. How much will you spend if you buy 1 slice of pizza, 1 slice of cake, 2 scoops of ice cream, and 3 hot dogs?\nA: \n\nEnd your final answer with 'The answer is <answer>.'\nOutput: The answer is <answer>.\n\nQ\"\"\"\n\nAnswer range: a(n) number / set / vector / matrix / interval / expression / function / equation / inequality\n\nKey extracted answer: ",
]

#######################################################################
#                      PART 2  Model & Tokenizer                      #
#######################################################################
tokenizer = dict(
    type=AutoTokenizer.from_pretrained,
    pretrained_model_name_or_path=pretrained_model_name_or_path,
    trust_remote_code=True,
    padding_side='right')

model = dict(
    type=SupervisedFinetune,
    use_varlen_attn=use_varlen_attn,
    llm=dict(
        type=AutoModelForCausalLM.from_pretrained,
        pretrained_model_name_or_path=pretrained_model_name_or_path,
        trust_remote_code=True,
        torch_dtype=torch.float16,
        quantization_config=dict(
            type=BitsAndBytesConfig,
            load_in_4bit=True,
            load_in_8bit=False,
            llm_int8_threshold=6.0,
            llm_int8_has_fp16_weight=False,
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type='nf4')),
    lora=dict(
        type=LoraConfig,
        r=64,
        lora_alpha=16,
        lora_dropout=0.1,
        bias='none',
        task_type='CAUSAL_LM'))

#######################################################################
#                      PART 3  Dataset & Dataloader                   #
#######################################################################
train_dataset = dict(
    type=process_hf_dataset,
    dataset=dict(type=load_dataset, path="json", data_files=dict(train=data_path)),
    tokenizer=tokenizer,
    max_length=max_length,
    # dataset_map_fn=alpaca_map_fn,
    dataset_map_fn=None,
    template_map_fn=dict(
        type=template_map_fn_factory, template=prompt_template),
    remove_unused_columns=True,
    shuffle_before_pack=True,
    pack_to_max_length=pack_to_max_length,
    use_varlen_attn=use_varlen_attn)

train_dataloader = dict(
    batch_size=batch_size,
    num_workers=dataloader_num_workers,
    dataset=train_dataset,
    sampler=dict(type=DefaultSampler, shuffle=True),
    collate_fn=dict(type=default_collate_fn, use_varlen_attn=use_varlen_attn))

#######################################################################
#                    PART 4  Scheduler & Optimizer                    #
#######################################################################
# optimizer
optim_wrapper = dict(
    type=AmpOptimWrapper,
    optimizer=dict(
        type=optim_type, lr=lr, betas=betas, weight_decay=weight_decay),
    clip_grad=dict(max_norm=max_norm, error_if_nonfinite=False),
    accumulative_counts=accumulative_counts,
    loss_scale='dynamic',
    dtype='float16')

# learning policy
# More information: https://github.com/open-mmlab/mmengine/blob/main/docs/en/tutorials/param_scheduler.md  # noqa: E501
param_scheduler = [
    dict(
        type=LinearLR,
        start_factor=1e-5,
        by_epoch=True,
        begin=0,
        end=warmup_ratio * max_epochs,
        convert_to_iter_based=True),
    dict(
        type=CosineAnnealingLR,
        eta_min=0.0,
        by_epoch=True,
        begin=warmup_ratio * max_epochs,
        end=max_epochs,
        convert_to_iter_based=True)
]

# train, val, test setting
train_cfg = dict(type=TrainLoop, max_epochs=max_epochs)

#######################################################################
#                           PART 5  Runtime                           #
#######################################################################
# Log the dialogue periodically during the training process, optional
custom_hooks = [
    dict(type=DatasetInfoHook, tokenizer=tokenizer),
    dict(
        type=EvaluateChatHook,
        tokenizer=tokenizer,
        every_n_iters=evaluation_freq,
        evaluation_inputs=evaluation_inputs,
        system=SYSTEM,
        prompt_template=prompt_template)
]

if use_varlen_attn:
    custom_hooks += [dict(type=VarlenAttnArgsToMessageHubHook)]

# configure default hooks
default_hooks = dict(
    # record the time of every iteration.
    timer=dict(type=IterTimerHook),
    # print log every 10 iterations.
    logger=dict(type=LoggerHook, log_metric_by_epoch=False, interval=10),
    # enable the parameter scheduler.
    param_scheduler=dict(type=ParamSchedulerHook),
    # save checkpoint per `save_steps`.
    checkpoint=dict(
        type=CheckpointHook,
        by_epoch=False,
        interval=save_steps,
        max_keep_ckpts=save_total_limit),
    # set sampler seed in distributed evrionment.
    sampler_seed=dict(type=DistSamplerSeedHook),
)

# configure environment
env_cfg = dict(
    # whether to enable cudnn benchmark
    cudnn_benchmark=False,
    # set multi process parameters
    mp_cfg=dict(mp_start_method='fork', opencv_num_threads=0),
    # set distributed parameters
    dist_cfg=dict(backend='nccl'),
)

# set visualizer
# visualizer = None
visualizer = dict(
    type=Visualizer,
    vis_backends=[
        dict(type=WandbVisBackend,
             init_kwargs=dict(project='xFinder', 
                              name="xFinder-qwen1518chat_qlora",
                              ))])

# set log level
log_level = 'INFO'

# load from which checkpoint
load_from = None

# whether to resume training from the loaded checkpoint
resume = False

# Defaults to use random seed and disable `deterministic`
randomness = dict(seed=None, deterministic=False)

# set log processor
log_processor = dict(by_epoch=False)
