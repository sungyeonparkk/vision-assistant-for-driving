## SNU-ENG 환경에서 학습하기

### 1. config 파일 지정 (갱신하는 경우에만)

```shell
python update_config.py {업데이트할_config_file_경로}
# python update_config.py ../train_configs/drive_finetune.yaml
```

### 2. 실험 코드 수정사항 배포 (갱신하는 경우에만)
```shell
docker login https://registry.ferrari.snucse.org:30443 
docker build --platform linux/amd64 -t registry.ferrari.snucse.org:30443/attention-x/drive-vision-assistant-experiment .
docker push registry.ferrari.snucse.org:30443/attention-x/drive-vision-assistant-experiment:latest
```

### 3. 실험 실행
```shell
python run_experiment.py
```

### 4. 실험 결과 모니터링
```shell
python monitor.py
# shows all pods 
$ vision-assistant-experiment-1696684995.894788 | Failed
$ vision-assistant-experiment-1696685411.304984 | Running
$ Enter pod name to stream logs: vision-assistant-experiment-1696685411.304984
# shows logs of the pod (following)
$ Downloading (…)solve/main/vocab.txt: 100%|██████████| 232k/232k [00:00<00:00, 10.8MB/s]
$ Downloading (…)okenizer_config.json: 100%|██████████| 28.0/28.0 [00:00<00:00, 29.1kB/s]
$ Downloading (…)lve/main/config.json: 100%|██████████| 570/570 [00:00<00:00, 882kB/s]
$ Loading VIT
$ 2023-10-07 13:30:33,040 [INFO] Downloading: "https://storage.googleapis.com/sfr-vision-language-research/LAVIS/models/BLIP2/eva_vit_g.pth" to /root/.cache/torch/hub/checkpoints/eva_vit_g.pth
```

### KubeCtl 설정
- 아래 1~3번만 실행할 수 있으면 상관 없으나 실행 후 pod 삭제 등을 위해 그냥 설치하면 좋음
- https://gpu.snucse.org/kubectl.html