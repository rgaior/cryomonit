# Dockerfile 
# Use an official Python runtime as a parent image
FROM python:3.8-slim

# Set the working directory to /app
# in the container
WORKDIR /app

# Install any needed packages specified in requirements.txt
COPY requirements.txt /app/requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt

# Copy the python script 
COPY rundb.py /app/rundb.py
# Copy utils function
COPY utils.py  /app/utils.py

# Run app.py when the container launches
# The -u flag specifies to use the unbuffered ouput.
# in this way, what's printed by the app is visible on the host
# while the container is running
#CMD ["bash",]
#CMD ["python", "-u", "testinotify.py", "influxdb", "8086", "/testdata/", "cryo1", "p", "--reset",]
