"""
 Copyright (c) 2022, salesforce.com, inc.
 All rights reserved.
 SPDX-License-Identifier: BSD-3-Clause
 For full license text, see the LICENSE_Lavis file in the repo root or https://opensource.org/licenses/BSD-3-Clause
"""

from video_llama.common.registry import registry
from video_llama.tasks.base_task import BaseTask

import torch.distributed as dist
from video_llama.common.logger import MetricLogger, SmoothedValue
from video_llama.datasets.data_utils import prepare_sample
from video_llama.common.dist_utils import (
    get_rank,
    get_world_size,
    is_main_process,
    is_dist_avail_and_initialized,
)


@registry.register_task("video_text_pretrain")
class VideoTextPretrainTask(BaseTask):
    def __init__(self):
        super().__init__()

    def evaluation(self, model, data_loader, cuda_enabled=True):
        metric_logger = MetricLogger(delimiter="  ")
        header = "Evaluation"
        # TODO make it configurable
        print_freq = 1

        results = []

        print("Data Loader : ", data_loader)
        print("Metric logger : ", metric_logger)
        i = 0
        for samples in metric_logger.log_every(data_loader, print_freq, header):
            samples = next(data_loader)
            samples = prepare_sample(samples, cuda_enabled=cuda_enabled)
            
            eval_output = self.valid_step(model=model, samples=samples)
            print(results)
            print(eval_output)
            try:
                results.extend(eval_output)
            except TypeError:
                results.append(eval_output)
                
            i += 1
            if i >= 2:
                break

        # if is_dist_avail_and_initialized():
        #     dist.barrier()

        return results
