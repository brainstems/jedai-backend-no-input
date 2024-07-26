# Use a base image with Python 3.11
FROM python:3.11-slim

# Set the working directory to /app
WORKDIR /app

# Copy the requirements.txt file and install dependencies
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code to the container
COPY . .

# Expose the port the app will run on
EXPOSE 4000

# Set environment variables
ENV AKASH_ENDPOINT=$AKASH_ENDPOINT
ENV AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID
ENV AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY
ENV AWS_SESSION_TOKEN=$AWS_SESSION_TOKEN
ENV LAMBDA_FUNCTION_NAME=$LAMBDA_FUNCTION_NAME
ENV AWS_REGION=$AWS_REGION

# Command to run the application using Uvicorn
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port 4000"]
