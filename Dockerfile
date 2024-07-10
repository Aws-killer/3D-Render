# Builder stage
FROM python:3.10.0 as builder

RUN useradd -ms /bin/bash admin

WORKDIR /srv
RUN chown -R admin:admin /srv
RUN chmod 755 /srv



RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    aria2 ffmpeg     libgl1-mesa-dev \
    libgles2-mesa-dev \
    libglu1-mesa-dev \
    build-essential \
    cmake \
    freeglut3-dev \
    libglfw3-dev \
    libglew-dev \
    libsdl2-dev \
    libjpeg-dev \
    libpng-dev \
    libfreetype6-dev \
    && rm -rf /var/lib/apt/lists/*

#copy requirements    
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt




# Create necessary directories and set permissions
RUN mkdir -p /home/admin/.local/share/BrokenSource/Broken \
    && mkdir -p /home/admin/.local/share/BrokenSource/DepthFlow/Config \
    && mkdir -p /tmp/Video \
    && rm -rf /usr/local/lib/python3.10/site-packages/Workspace \
    && mkdir -p /usr/local/lib/python3.10/site-packages/Workspace \
    && ln -s /home/admin/.local/share/BrokenSource/Broken /usr/local/lib/python3.10/site-packages/Workspace/Broken \
    && ln -s /home/admin/.local/share/BrokenSource/DepthFlow /usr/local/lib/python3.10/site-packages/Workspace/DepthFlow \
    && chmod -R 777 /home/admin/.local /tmp/Video /usr/local/lib/python3.10/site-packages/Workspace



# Create a non-root user and give it sudo privileges
RUN useradd -m appuser \
    && mkdir -p /etc/sudoers.d \
    && echo "appuser ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/appuser \
    && chmod 0440 /etc/sudoers.d/appuser

# Switch to the non-root user
USER appuser



COPY --chown=appuser . /srv

# Run your shader application when the container launches
CMD ["python", "-c", "import os; os.makedirs('/usr/local/lib/python3.10/site-packages/Workspace', exist_ok=True); os.system('uvicorn app:app --host 0.0.0.0 --port 8000 --workers 1')"]

# Expose the server port
EXPOSE 7860