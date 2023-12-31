FROM registry.ferrari.snucse.org:30443/attention-x/drive-vision-assistant:latest
WORKDIR /root
COPY . .
RUN apt-get update && apt-get -y install libgl1-mesa-glx ffmpeg libsm6 libxext6
RUN pip install -r requirements.txt