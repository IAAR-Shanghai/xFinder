# xFinder Scripts
This directory contains various scripts used in the xFinder project for robust and pinpoint answer extraction from LLMs.
## Machine Environment
- **Operating System:** Ubuntu
- **Package Manager:** Anaconda
- **GPU:** NVIDIA A100, 80GB

## XTuner Installation
- Prepare the Conda Environment
```
conda create --name xtuner-env python=3.10 -y
conda activate xtuner-env
```
- Install XTuner via pip
```
pip install -U 'xtuner[deepspeed]'
```
## Fine-tuning Dataset
The fine-tuning dataset for xFinder was derived by converting the training set of the KAF dataset into a format supported by xtuner. The final fine-tuning data is structured as follows:
```
{
    "system": "You are a help assistant tasked with extracting the precise key answer from given output sentences. You must only provide the extracted key answer without including any additional text.",
    "input": "I will provide you with a question, output sentences along with an answer range. The output sentences are the response of the question provided. The answer range could either describe the type of answer expected or list all possible valid answers. Using the information provided, you must accurately and precisely determine and extract the intended key answer from the output sentences. Please don't have your subjective thoughts about the question.\nFirst, you need to determine whether the content of the output sentences is relevant to the given question. If the entire output sentences are unrelated to the question (meaning the output sentences are not addressing the question), then output [No valid answer].\nOtherwise, ignore the parts of the output sentences that have no relevance to the question and then extract the key answer that matches the answer range.\nBelow are some special cases you need to be aware of: \n    (1) If the output sentences present multiple different answers, carefully determine if the later provided answer is a correction or modification of a previous one. If so, extract this corrected or modified answer as the final response. Conversely, if the output sentences fluctuate between multiple answers without a clear final answer, you should output [No valid answer].\n    (2) If the answer range is a list and the key answer in the output sentences is not explicitly listed among the candidate options in the answer range, also output [No valid answer].\n\nQuestion: \"\"\"Which statement correctly describes a physical characteristic of the Moon?  Answer Choices:  (A) The Moon is made of hot gases.  (B) The Moon is covered with many craters. (C) The Moon has many bodies of liquid water. (D) The Moon has the ability to give off its own light.\"\"\"\n\nOutput sentences: \"\"\"\n\nStep 1: Analyze the question and the given options.\nThe question is asking for a physical characteristic of the Moon.\n\nStep 2: Evaluate each option.\nOption (A) states that the Moon is made of hot gases, which is not a physical characteristic.\nOption (B) states that the Moon is covered with many craters, which is a physical characteristic.\nOption (C) states that the Moon has many bodies of liquid water, which is not a physical characteristic.\nOption (D) states that the Moon has the ability to give off its own light, which is not a physical characteristic.\n\nStep 3: Choose the correct option based on the evaluation.\nThe correct option is (B) The Moon is covered with many craters.\n\nFinal Answer: B. The Moon is covered with many craters.\"\"\"\n\nAnswer range: [['D', 'The Moon has the ability to give off its own light.'], ['C', 'The Moon has many bodies of liquid water.'], ['B', 'The Moon is covered with many craters.'], ['A', 'The Moon is made of hot gases.']]\n\nKey extracted answer: ",
    "output": "B"
}
```
## XTuner Fine-tuning Config
The configuration files used to fine-tune different models to obtain xFinder are shown in the table below:
<table>
  <tr>
    <th style="text-align:center;">xFinder</th>
    <th style="text-align:center;">foundation model</th>
    <th style="text-align:center;">configuration file</th>
  </tr>
  <tr>
    <td style="text-align:center;">xFinder-qwen1505</td>
    <td style="text-align:center;"><a href="https://huggingface.co/Qwen/Qwen1.5-0.5B">Qwen1.5-0.5B</a></td>
    <td style="text-align:center;"><a href="./xtuner_config/xFinder-qwen1505_qlora.py">xFinder-qwen1505_qlora.py</a></td>
  </tr>
  <tr>
    <td style="text-align:center;">xFinder-qwen1505chat</td>
    <td style="text-align:center;"><a href="https://huggingface.co/Qwen/Qwen1.5-0.5B-Chat">Qwen1.5-0.5B-Chat</a></td>
    <td style="text-align:center;"><a href="./xtuner_config/xFinder-qwen1505chat_qlora.py">xFinder-qwen1505chat_qlora.py</a></td>
  </tr>
  <tr>
    <td style="text-align:center;">xFinder-qwen1518</td>
    <td style="text-align:center;"><a href="https://huggingface.co/Qwen/Qwen1.5-1.8B">Qwen1.5-1.8B</a></td>
    <td style="text-align:center;"><a href="./xtuner_config/xFinder-qwen1518_qlora.py">xFinder-qwen1518_qlora.py</a></td>
  </tr>
  <tr>
    <td style="text-align:center;">xFinder-qwen1518chat</td>
    <td style="text-align:center;"><a href="https://huggingface.co/Qwen/Qwen1.5-1.8B-Chat">Qwen1.5-1.8B-Chat</a></td>
    <td style="text-align:center;"><a href="./xtuner_config/xFinder-qwen1518chat_qlora.py">xFinder-qwen1518chat_qlora.py</a></td>
  </tr>
  <tr>
    <td style="text-align:center;">xFinder-internlm218</td>
    <td style="text-align:center;"><a href="https://huggingface.co/internlm/internlm2-1_8b">InternLM2-1.8B</a></td>
    <td style="text-align:center;"><a href="./xtuner_config/xFinder-internlm218_qlora.py">xFinder-internlm218_qlora.py</a></td>
  </tr>
  <tr>
    <td style="text-align:center;">xFinder-gemma2</td>
    <td style="text-align:center;"><a href="https://huggingface.co/google/gemma-2b">Gemma-2B</a></td>
    <td style="text-align:center;"><a href="./xtuner_config/xFinder-gemma2_qlora.py">xFinder-gemma2_qlora.py</a></td>
  </tr>
  <tr>
    <td style="text-align:center;">xFinder-gemma2it</td>
    <td style="text-align:center;"><a href="https://huggingface.co/google/gemma-2b-it">Gemma-2B-it</a></td>
    <td style="text-align:center;"><a href="./xtuner_config/xFinder-gemma2it_qlora.py">xFinder-gemma2it_qlora.py</a></td>
  </tr>
  <tr>
    <td style="text-align:center;">xFinder-qwen154</td>
    <td style="text-align:center;"><a href="https://huggingface.co/Qwen/Qwen1.5-4B">Qwen1.5-4B</a></td>
    <td style="text-align:center;"><a href="./xtuner_config/xFinder-qwen154_qlora.py">xFinder-qwen154_qlora.py</a></td>
  </tr>
  <tr>
    <td style="text-align:center;">xFinder-qwen154chat</td>
    <td style="text-align:center;"><a href="https://huggingface.co/Qwen/Qwen1.5-4B-Chat">Qwen1.5-4B-Chat</a></td>
    <td style="text-align:center;"><a href="./xtuner_config/xFinder-qwen154chat_qlora.py">xFinder-qwen154chat_qlora.py</a></td>
  </tr>
  <tr>
    <td style="text-align:center;">xFinder-chatglm36base</td>
    <td style="text-align:center;"><a href="https://huggingface.co/THUDM/chatglm3-6b-base">ChatGLM3-6B-base</a></td>
    <td style="text-align:center;"><a href="./xtuner_config/xFinder-chatglm36base_qlora.py">xFinder-chatglm36base_qlora.py</a></td>
  </tr>
  <tr>
    <td style="text-align:center;">xFinder-chatglm36</td>
    <td style="text-align:center;"><a href="https://huggingface.co/THUDM/chatglm3-6b">ChatGLM3-6B</a></td>
    <td style="text-align:center;"><a href="./xtuner_config/xFinder-chatglm36_qlora.py">xFinder-chatglm36_qlora.py</a></td>
  </tr>
  <tr>
    <td style="text-align:center;">xFinder-qwen157</td>
    <td style="text-align:center;"><a href="https://huggingface.co/Qwen/Qwen1.5-7B">Qwen1.5-7B</a></td>
    <td style="text-align:center;"><a href="./xtuner_config/xFinder-qwen157_qlora.py">xFinder-qwen157_qlora.py</a></td>
  </tr>
  <tr>
    <td style="text-align:center;">xFinder-qwen157chat</td>
    <td style="text-align:center;"><a href="https://huggingface.co/Qwen/Qwen1.5-7B-Chat">Qwen1.5-7B-Chat</a></td>
    <td style="text-align:center;"><a href="./xtuner_config/xFinder-qwen157chat_qlora.py">xFinder-qwen157chat_qlora.py</a></td>
  </tr>
  <tr>
    <td style="text-align:center;">xFinder-internlm27</td>
    <td style="text-align:center;"><a href="https://huggingface.co/internlm/internlm2-7b">InternLM2-7B</a></td>
    <td style="text-align:center;"><a href="./xtuner_config/xFinder-internlm27_qlora.py">xFinder-internlm27_qlora.py</a></td>
  </tr>
  <tr>
    <td style="text-align:center;">xFinder-baichuan27chat</td>
    <td style="text-align:center;"><a href="https://huggingface.co/baichuan-inc/Baichuan2-7B-Chat">Baichuan2-7B-Chat</a></td>
    <td style="text-align:center;"><a href="./xtuner_config/xFinder-baichuan27chat_qlora.py">xFinder-baichuan27chat_qlora.py</a></td>
  </tr>
  <tr>
    <td style="text-align:center;">xFinder-gemma7</td>
    <td style="text-align:center;"><a href="https://huggingface.co/google/gemma-7b">Gemma-7B</a></td>
    <td style="text-align:center;"><a href="./xtuner_config/xFinder-gemma7_qlora.py">xFinder-gemma7_qlora.py</a></td>
  </tr>
  <tr>
    <td style="text-align:center;">xFinder-gemma7it</td>
    <td style="text-align:center;"><a href="https://huggingface.co/google/gemma-7b-it">Gemma-7B-it</a></td>
    <td style="text-align:center;"><a href="./xtuner_config/xFinder-gemma7it_qlora.py">xFinder-gemma7it_qlora.py</a></td>
  </tr>
  <tr>
    <td style="text-align:center;">xFinder-llama38</td>
    <td style="text-align:center;"><a href="https://huggingface.co/meta-llama/Meta-Llama-3-8B">Llama-3-8B</a></td>
    <td style="text-align:center;"><a href="./xtuner_config/xFinder-llama38_qlora.py">xFinder-llama38_qlora.py</a></td>
  </tr>
  <tr>
    <td style="text-align:center;">xFinder-llama38it</td>
    <td style="text-align:center;"><a href="https://huggingface.co/meta-llama/Meta-Llama-3-8B-Instruct">Llama3-8B-Instruct</a></td>
    <td style="text-align:center;"><a href="./xtuner_config/xFinder-llama38it_qlora.py">xFinder-llama38it_qlora.py</a></td>
  </tr>
</table>

## Fine-tuning
Use the `xtuner train` command to start training.
```
CUDA_VISIBLE_DEVICES=0 xtuner train path/to/scripts/xtuner_config/xFinder-qwen1518_qlora.py --deepspeed deepspeed_zero2
```
Parameter conversion and merging after fine-tuning.
```
./xtuner_merge.sh -l /path/to/llm -a /path/to/adapter -m /path/to/merge/save
```







