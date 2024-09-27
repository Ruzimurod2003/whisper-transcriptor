# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Install Supervisor
RUN apt-get update && apt-get install -y supervisor 

# Install Git
RUN apt-get update && apt-get install git -y

# Upgrade pip
RUN pip install --upgrade pip

# Install packages
RUN pip install -r requirements.txt

# Install Whisper from Git
RUN pip install git+https://github.com/openai/whisper.git

# Install ffmpeg
RUN apt-get update && apt-get install -y ffmpeg

# Install setuptools-rust
RUN pip install setuptools-rust

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

RUN pip install python-multipart

# Copy the Supervisor configuration file
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Expose the necessary ports
EXPOSE 80

# Run Supervisor
CMD ["/usr/bin/supervisord"]
