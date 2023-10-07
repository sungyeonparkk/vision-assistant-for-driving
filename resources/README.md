## SNU-ENG 환경에서 학습하기

### KubeCtl 설정
- https://gpu.snucse.org/kubectl.html

### 1. 설정 업데이트

```shell
python update_config.py {업데이트할_config_file_경로}
```

### 2. 실험 실행
```shell
python run_experiment.py
```

### 3. 실험 코드 수정사항 배포
```shell
docker login https://registry.ferrari.snucse.org:30443 
docker build --platform linux/amd64 -t registry.ferrari.snucse.org:30443/attention-x/drive-vision-assistant-experiment .
docker push registry.ferrari.snucse.org:30443/attention-x/drive-vision-assistant-experiment:latest
```
위 코드 실행 후 2번 실행