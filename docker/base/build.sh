#!/bin/bash

script_dir=$(dirname $0)
rsync $script_dir/../../setup.py $script_dir/isanlp/
rsync -r $script_dir/../../src/ $script_dir/isanlp/src
docker build -t inemo/isanlp_base $script_dir
