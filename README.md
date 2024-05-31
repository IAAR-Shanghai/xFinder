<div align="center"><h2>
<img src="./assets/xfinder_logo.png" alt="xFinder_logo" width=23px>xFinder: Robust and Pinpoint Answer Extraction for Large Language Models</h2></div>

## :sparkles: Overview
<div align="center">
    <img src="./assets/framework.jpg" alt="xFinder" width="93%">
</div>

<details><summary>Abstract</summary>
The continuous advancement of large language models (LLMs) has brought increasing attention to the critical issue of developing fair and reliable methods for evaluating their performance. Particularly, the emergence of subjective or non-subjective cheating phenomena, such as test set leakage and prompt format overfitting, poses significant challenges to the reliable evaluation of LLMs. Since evaluation frameworks often utilize Regular Expression (RegEx) for answer extraction, some models may adjust their responses to comply with specific formats that are easily extractable by RegEx. Nevertheless, the key answer extraction module based on RegEx frequently suffers from extraction errors. This paper conducts a comprehensive analysis of the entire LLM evaluation chain, demonstrating that optimizing the key answer extraction module can improve extraction accuracy, reduce LLMs' reliance on specific answer formats, and enhance the reliability of LLM evaluation. To address these issues, we propose xFinder, a model specifically designed for key answer extraction. As part of this process, we create a specialized dataset, the Key Answer Finder (KAF) dataset, to ensure effective model training and evaluation. Through generalization testing and evaluation in real-world scenarios, the results demonstrate that the smallest xFinder model with only 500 million parameters achieves an average answer extraction accuracy of 93.42%. In contrast, RegEx accuracy in the best evaluation framework is 74.38%. xFinder exhibits stronger robustness and higher accuracy compared to existing evaluation frameworks.
</details>

We summarize our primary contributions as follows:

- We provide a comprehensive review of LLM evaluation processes in the industry, identifying critical factors that can lead to unreliable evaluation results.
- We introduce xFinder, a model specifically designed for key answer extraction. The KAF dataset supports its effective training and evaluation.
- In our extensive experiments, we demonstrate that RegEx-based evaluation methods are unreliable, while our xFinder model significantly improves reliability.

<div align="center">
    <img src="./assets/example.jpg" alt="xFinder" width="93%">
</div>

> As shown in the figure, instances where evaluation frameworks such as LM Eval Harness and OpenCompass failed to extract key answers are illustrated. Specifically, A/T/C/M represent tasks with alphabet / short text / categorical label / math options, respectively.

## :zap: Quick Start
1. **Ensure Compatibility**: Ensure you have Python 3.10.0+.
2. **Prepare QA pairs & LLM Outputs**: Prepare the LLM outputs that you want to evaluate. 
   - provide a `.json` file including original question, key answer type (alphabet / short_text / categorical_label / math), LLM output, standard answer range.
   - For a detailed example of the expected format, refer to [`demo/example.json`](demo/example.json).
3. **Deploy the xFinder Model**: Choose between two models for deployment, [xFinder-qwen1505]() or [xFinder-llama38it]().
4. **Finish Configuration**: Compile the above details into a configuration file. For configuration details, see [`demo\xfinder_config.yaml`](demo/xfinder_config.yaml).

After setting up the configuration file, you have two methods to proceed with the evaluation:

**1. Use with install:**
```bash
> cd xFinder
> conda create -n xfinder_env python=3.11 -y
> conda activate xfinder_env
> pip install -e .
> xfinder $PATH_TO_CONFIG
```
**2. Use without install:**
```bash
> cd xFinder
> pip install -r requirements.txt
> python
>>> from xfinder.eval import calc_acc
>>> calc_acc($PATH_TO_CONFIG)
```

## :sun_with_face: Examples
We demonstrate instances across four types of questions where RegEx fails to extract or frequently extracts incorrect answers, whereas xFinder accurately extracts the key answers.
```
{
    "key_answer_type": "alphabet option",
    "question": "A man is seen playing guitar on a stage with others playing instruments behind him. The man grabs a guitar from the audience and begins playing both one after the other ...",
    "llm_output": "Option A is the correct choice as it describes ...",
    "standard_answer_range": "[['A', 'strums the guitar in the end, continues playing the guitar with the crowd following him as well as lining up next to him.'], ['B', 'continues playing the instruments and ends by waving to the crowd and walking off stage.'], ['C', 'then turns to the audience and gives a stuffed toy to the audience and continues playing.'], ['D', 'finally stops playing and moves his hands for the crowd to see.']]",
    "gold_label": "A",
    "xFinder_output": "A",
},
{
    "key_answer_type": "short text",
    "question": "If you really wanted a grape, where would you go to get it? Answer Choices: winery / fruit stand / field / kitchen / food",
    "llm_output": "The answer is winery / fruit stand / field / kitchen / food ...",
    "standard_answer_range": "[\"winery\", \"fruit stand\", \"field\", \"kitchen\", \"food\"]",
    "gold_label": "[No valid answer]",
    "xFinder_output": "[No valid answer]",
},
{
    "key_answer_type": "categorical label",
    "question": "How tall is the Sears Building ?",
    "llm_output": "The Sears Building is a specific structure, so the answer would be a Location ...",
    "standard_answer_range": "['Abbreviation', 'Entity', 'Description', 'Person', 'Location', 'Number']",
    "gold_label": "Location",
    "xFinder_output": "Location",
},
{
    "key_answer_type": "math",
    "question": " Mike made 69 dollars mowing lawns over the summer. If he spent 24 dollars buying new mower blades, how many 5 dollar games could he buy with the money he had left? ",
    "llm_output": "To find out how many 5 dollar ... Let's calculate that:\n\n$45 / $5 = 9\n\nSo, Mike could buy 9 5 dollar games with the money he had left.",
    "standard_answer_range": "a(n) number / set / vector / matrix / interval / expression / function / equation / inequality",
    "gold_label": "9",
    "xFinder_output": "9",
}
```
## :trophy: Results of Extraction Accuracy
We evaluated their accuracy in extracting key answers from both the KAF test set and generalization sets. The results were compared against mainstream evaluation frameworks that utilize RegEx methods.
<div align="center">
    <img src="./assets/test-result.png" alt="xFinder" width="93%">
</div>
<div align="center">
    <img src="./assets/generalization-result.png" alt="xFinder" width="93%">
</div>