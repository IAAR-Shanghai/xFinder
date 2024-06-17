#!/bin/bash

# Parse input arguments
while getopts c:p:s:l:a:m: flag
do
    case "${flag}" in
        c) CONFIG_NAME_OR_PATH=${OPTARG};;
        p) PTH=${OPTARG};;
        s) SAVE_PATH=${OPTARG};;
        l) NAME_OR_PATH_TO_LLM=${OPTARG};;
        a) NAME_OR_PATH_TO_ADAPTER=${OPTARG};;
        m) MERGE_SAVE_PATH=${OPTARG};;
    esac
done

# Create a directory to store Hugging Face format parameters
mkdir -p ${SAVE_PATH}

# Set MKL environment variable
export MKL_SERVICE_FORCE_INTEL=1

# Execute parameter conversion
CUDA_VISIBLE_DEVICES=1 xtuner convert pth_to_hf ${CONFIG_NAME_OR_PATH} ${PTH} ${SAVE_PATH}

# Set MKL threading layer environment variable
export MKL_THREADING_LAYER='GNU'

# Create a directory to store the final merged parameters
mkdir -p ${MERGE_SAVE_PATH}

# Execute parameter merging
CUDA_VISIBLE_DEVICES=1 xtuner convert merge \
    ${NAME_OR_PATH_TO_LLM} \
    ${NAME_OR_PATH_TO_ADAPTER} \
    ${MERGE_SAVE_PATH} \
    --max-shard-size 2GB
