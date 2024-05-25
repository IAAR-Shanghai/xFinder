<div align="center"><h2>
<img src="./assets/xfinder_logo.png" alt="xFinder_logo" width=23px>xFinder: Robust and Pinpoint Answer Extraction for Large Language Models</h2></div>

<p align="center">
    <!-- arxiv badges -->
    <a href="https://arxiv.org/abs/2405.11874">
        <img src="https://img.shields.io/badge/Paper-red?style=flat&logo=arxiv">
    </a>
    <!-- Github -->
    <a href="https://github.com/IAAR-Shanghai/xFinder">
        <img src="https://img.shields.io/badge/Code-black?style=flat&logo=github">
    </a>
    <!-- hf collection -->
    <a href="https://huggingface.co/collections/IAAR-Shanghai/xfinder-664b7b21e94e9a93f25a8412"><img src="https://img.shields.io/badge/-%F0%9F%A4%97%20Collection-orange?style=flat"/></a>
    <!-- Model 0.5B -->
    <a href="https://huggingface.co/IAAR-Shanghai/xFinder-qwen1505">
        <img src="https://img.shields.io/badge/%F0%9F%A4%97%20Model%20(0.5B)-orange?style=flat">
    </a>
    <a href="https://huggingface.co/IAAR-Shanghai/xFinder-llama38it">
        <img src="https://img.shields.io/badge/%F0%9F%A4%97%20Model%20(8B)-orange?style=flat">
    </a>
</p>

<div align="center">
    <p>
        <a href="https://github.com/Duguce">Qingchen Yu</a><sup>1,*</sup>, 
        <a href="https://github.com/fan2goa1">Zifan Zheng</a><sup>1,*</sup>, 
        <a href="https://github.com/Ki-Seki">Shichao Song</a><sup>2,*</sup>, 
        <a>Zhiyu Li</a><sup>1,†</sup>, Feiyu Xiong<sup>1</sup>, Bo Tang<sup>1</sup>, <a href="https://github.com/hush-cd">Ding Chen</a><sup>1</sup>
    </p>
    <p>
        <sup>1</sup><a href="https://www.iaar.ac.cn/">Institute for Advanced Algorithms Research, Shanghai</a>, <sup>2</sup><a href="https://en.ruc.edu.cn/">Renmin University of China</a>
    </p>
</div>


<div align="center"><h5>For business inquiries, please contact us at <a href="mailto:lizy@iaar.ac.cn">lizy@iaar.ac.cn</a>.</h5></div>

## :sparkles: Overview
<div align="center">
    <img src="./assets/framework.jpg" alt="xFinder" width="93%">
</div>

## :zap: Quick Start
1. Ensure you have Python 3.10.0+.
2. Prepare the LLM outputs that you want to evaluate. 
   1. You need to provide a `.json` file including original question, key answer type (alphabet / short_text / categorical_label / math), LLM output, standard answer range.
   2. Refer to [`demo/example.json`](demo/example.json) for the detailed form.
3. Deploy xFinder model, you can choose either [xFinder-qwen1505]() or [xFinder-llama38it]().

Here's two methods to use xfinder: 
**1. Use with install:**
```bash
> git clone  git@github.com:IAAR-Shanghai/xFinder.git
> cd xFinder
> conda create -n xfinder_env python=3.11 -y
> conda activate xfinder_env
> pip install -e .
> xfinder $PATH_TO_CONFIG
```
**2. Use without install:**
```bash
> git clone  git@github.com:IAAR-Shanghai/xFinder.git
> cd xFinder
> pip install -r requirements.txt
> python
>>> from xfinder.eval import calc_acc
>>> calc_acc($PATH_TO_CONFIG)
```

## 

## :memo: Citation
```
@article{xFinder,
      title={xFinder: Robust and Pinpoint Answer Extraction for Large Language Models}, 
      author={Qingchen Yu and Zifan Zheng and Shichao Song and Zhiyu Li and Feiyu Xiong and Bo Tang and Ding Chen},
      journal={arXiv preprint arXiv:2405.11874},
      year={2024},
}
```

## :triangular_flag_on_post: TODOs
<details><summary>Click me to show all TODOs</summary>

- [ ] feat: customized configuration on attributes' names.
- [ ] feat: demo
- [ ] docs: add video tutorial

</details>