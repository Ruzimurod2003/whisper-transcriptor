# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Add Forticlient certificate
COPY ./docker/certs/Fortinet_CA_SSL.cer /usr/share/ca-certificates/
RUN grep -qxF 'Fortinet_CA_SSL.cer' /etc/ca-certificates.conf || echo 'Fortinet_CA_SSL.cer' >> /etc/ca-certificates.conf && \
    update-ca-certificates

COPY ./requirements.txt /app/requirements.txt

COPY . /app

RUN apt-get update && apt-get install git -y

RUN pip install --upgrade pip

RUN pip install -r requirements.txt

RUN pip install python-multipart

RUN pip install --no-cache-dir -r requirements.txt

RUN pip install git+https://github.com/openai/whisper.git

RUN apt-get update && apt-get install -y ffmpeg

RUN pip install setuptools-rust

# Install Supervisor
RUN apt-get update && apt-get install -y supervisor dos2unix 

COPY ./docker/start_local_dev /usr/local/bin/start_local_dev
COPY ./docker/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Ensure the script has correct Unix line endings and execute permissions
RUN dos2unix /usr/local/bin/start_local_dev
RUN chmod +x /usr/local/bin/start_local_dev

ENV PYTHONPATH=/app

# Expose the necessary ports
EXPOSE 5000

# Start the main process
CMD ["/usr/bin/supervisord"]
# ENTRYPOINT ["tail", "-f", "/dev/null"]