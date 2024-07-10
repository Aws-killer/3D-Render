# Builder stage
FROM python:3.10.0 as builder

# Create non-root users
RUN useradd -ms /bin/bash admin && \
    useradd -ms /bin/bash appuser && \
    echo "appuser ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/appuser && \
    chmod 0440 /etc/sudoers.d/appuser

WORKDIR /srv
RUN chown -R admin:admin /srv && chmod 755 /srv

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    aria2 ffmpeg libgl1-mesa-dev \
    libgles2-mesa-dev libglu1-mesa-dev \
    build-essential cmake freeglut3-dev \
    libglfw3-dev libglew-dev libsdl2-dev \
    libjpeg-dev libpng-dev libfreetype6-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create necessary directories and set permissions
RUN mkdir -p /home/admin/.local/share/BrokenSource/Broken \
    /home/admin/.local/share/BrokenSource/DepthFlow/Config \
    /tmp/Video \
    /usr/local/lib/python3.10/site-packages/Workspace && \
    chown -R admin:admin /home/admin/.local && \
    chmod -R 755 /home/admin/.local /tmp/Video /usr/local/lib/python3.10/site-packages/Workspace

# Copy application files
COPY --chown=appuser . /srv

# Create startup script
RUN echo '#!/bin/bash\n\
    ln -sf /home/admin/.local/share/BrokenSource/Broken /usr/local/lib/python3.10/site-packages/Workspace/Broken\n\
    ln -sf /home/admin/.local/share/BrokenSource/DepthFlow /usr/local/lib/python3.10/site-packages/Workspace/DepthFlow\n\
    exec uvicorn app:app --host 0.0.0.0 --port 8000\n'\
    > /srv/start.sh && chmod +x /srv/start.sh

# Switch to the non-root user
USER appuser

# Expose the server port
EXPOSE 8000

# Run the startup script when the container launches
CMD ["/srv/start.sh"]