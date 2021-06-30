# Copyright (c) Facebook, Inc. and its affiliates.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# FROM pytorch/pytorch:1.8.1-cuda10.2-cudnn7-runtime

FROM pytorch/pytorch:latest

RUN apt-get update && apt-get install -y git

RUN groupadd -r user && useradd --no-log-init -rm -s /bin/bash -g user user

USER user

WORKDIR /home/user

ENV PATH="/home/user/.local/bin:${PATH}"

COPY --chown=user:user . .

RUN pip install --user -r requirements.txt

