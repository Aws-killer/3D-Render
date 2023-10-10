# Builder stage
FROM python:3.10.0 as builder

RUN useradd -ms /bin/bash admin

WORKDIR /srv
RUN chown -R admin:admin /srv
RUN chmod 755 /srv





COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
USER admin

COPY --chown=admin . /srv

# Command to run the application
CMD uvicorn App.app:app --host 0.0.0.0 --port 7860 --workers 1 
# Expose the server port
EXPOSE 7860