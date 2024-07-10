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
# Create necessary directories, remove existing symlinks, and set permissions
RUN mkdir -p /home/admin/.local/share/BrokenSource/Broken \
    && mkdir -p /home/admin/.local/share/BrokenSource/DepthFlow/Config \
    && mkdir -p /tmp/Video \
    && mkdir -p /usr/local/lib/python3.10/site-packages/Workspace \
    && rm -f /usr/local/lib/python3.10/site-packages/Workspace \
    && ln -s /home/admin/.local/share/BrokenSource/Broken /usr/local/lib/python3.10/site-packages/Workspace \
    && ln -s /home/admin/.local/share/BrokenSource/DepthFlow /usr/local/lib/python3.10/site-packages/Workspace \
    && chmod -R 777 /home/admin/.local /tmp/Video /usr/local/lib/python3.10/site-packages/Workspace


# Create a non-root user and give it sudo privileges
RUN useradd -m appuser \
    && mkdir -p /etc/sudoers.d \
    && echo "appuser ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/appuser \
    && chmod 0440 /etc/sudoers.d/appuser

# Switch to the non-root user
USER appuser



COPY --chown=appuser . /srv

# Command to run the application
CMD uvicorn App.app:app --host 0.0.0.0 --port 7860 --workers 1
# Expose the server port
EXPOSE 7860