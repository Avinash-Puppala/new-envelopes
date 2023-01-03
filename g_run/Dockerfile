# Use Python37
FROM python:3.7
# Copy requirements.txt to the docker image and install packages
COPY requirements.txt /
RUN pip install -r requirements.txt
# Set the WORKDIR to be the folder
COPY . /app
# Expose Port 8080
EXPOSE 8080
ENV PORT 8080

WORKDIR /app
# Use gunicorn as the entrypoint
CMD gunicorn --bind :$PORT main_v1:app --workers 1 --threads 1 --timeout 60