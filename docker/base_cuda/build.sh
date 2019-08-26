#!/bin/bash

script_dir=$(dirname $0)
mkdir -p isanlp
rsync -r $script_dir/../../src/ $script_dir/isanlp/src || { exit 1; }
rsync $script_dir/../../setup.py $script_dir/isanlp/ 
docker build -t inemo/isanlp_base_cuda $script_dir
