# 使用Python官方镜像作为基础镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    python3-tk \
    && rm -rf /var/lib/apt/lists/*

# 复制项目文件
COPY requirements.txt .
COPY src/ ./src/
COPY main.py .
COPY README.md .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 设置环境变量
ENV PYTHONPATH=/app
ENV DISPLAY=:0

# 设置容器启动命令
CMD ["python", "main.py"]

# 使用说明
# 1. 构建镜像：
#    docker build -t mailcast .
#
# 2. 在Linux上运行（需要X11转发）：
#    xhost +
#    docker run -it --rm \
#        -e DISPLAY=$DISPLAY \
#        -v /tmp/.X11-unix:/tmp/.X11-unix \
#        mailcast
#
# 3. 在Windows上运行（需要X Server，如VcXsrv）：
#    docker run -it --rm \
#        -e DISPLAY=host.docker.internal:0 \
#        mailcast
#
# 4. 挂载配置文件（可选）：
#    docker run -it --rm \
#        -e DISPLAY=$DISPLAY \
#        -v /tmp/.X11-unix:/tmp/.X11-unix \
#        -v $(pwd)/config:/app/config \
#        mailcast