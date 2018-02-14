#!/bin/bash

script_dir=$(dirname $0)
rsync -r $script_dir/../../src/ $script_dir/isanlp/
docker build -t inemo/isanlp_base $script_dir
