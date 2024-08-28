# Use a base image with Python 3.11
FROM python:3.11-slim

RUN apt update && apt install -y git

# Set the working directory to /app
WORKDIR /app

# Copy the requirements.txt file and install dependencies
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code to the container
RUN git clone -b v0.1.9 https://github.com/brainstems/jedai-backend-no-input.git

WORKDIR /app/jedai-backend-no-input


# Expose the port the app will run on
EXPOSE 4000

ARG AKASH_ENDPOINT
ARG AWS_ACCESS_KEY_ID
ARG AWS_SECRET_ACCESS_KEY
ARG AWS_REGION
ARG SECRET_KEY
ARG ACCESS_TOKEN_EXPIRE_MINUTES
ARG RETRY_TIME

# Set environment variables
ENV AKASH_ENDPOINT=${AKASH_ENDPOINT}
ENV AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
ENV AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
ENV AWS_REGION=${AWS_REGION}
ENV SECRET_KEY=${SECRET_KEY}
ENV ACCESS_TOKEN_EXPIRE_MINUTES=${ACCESS_TOKEN_EXPIRE_MINUTES}
ENV RETRY_TIME=${RETRY_TIME}

# Command to run the application using Uvicorn
CMD ["uvicorn", "app.main:app", "--host=0.0.0.0" , "--reload" , "--port", "4000"]
