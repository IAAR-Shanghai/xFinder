<div align="center"><h2>
<img src="./assets/xfinder_logo.png" alt="xFinder_logo" width=23px>xFinder: Robust and Pinpoint Answer Extraction for Large Language Models</h2></div>

## :sparkles: Overview
<div align="center">
    <img src="./assets/framework.jpg" alt="xFinder" width="93%">
</div>

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