# Copyright (c) 2019, NVIDIA CORPORATION. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

#!/usr/bin/env bash


python ./utils/convert_librispeech.py \
    --input_dir ./data/youtube-br/train \
    --dest_dir ./datasets/youtube-br/train-wav \
    --output_json ./datasets/youtube-br/train-wav.json \
    --speed 0.9 1.1
python ./utils/convert_librispeech.py \
    --input_dir ./data/youtube-br/val \
    --dest_dir ./datasets/youtube-br/val-wav \
    --output_json ./datasets/youtube-br/val-wav.json \
    --speed 0.9 1.1

