# Use an official Python runtime as a parent image.
# We choose a lightweight image for smaller size.
FROM python:3.9-slim

# Set the working directory in the container to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
# This command first copies requirements.txt and then installs dependencies.
# This approach leverages Docker's layer caching.
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Define environment variable
ENV FLASK_APP=app.py

# Run app.py when the container launches
# The flask run command starts the development server
CMD ["flask", "run", "--host=0.0.0.0"]
