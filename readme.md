# Jedai Backend No Input

This application is designed to be run within a Docker container. It is a Python-based backend application that uses FastAPI for handling WebSocket connections and RESTful endpoints. The app integrates with external WebSocket services and AWS DynamoDB.

## Table of Contents

- [Requirements](#requirements)
- [Installation](#installation)
- [Environment Variables](#environment-variables)
- [Running the Application](#running-the-application)
- [Docker Usage](#docker-usage)
- [WebSocket Communication](#websocket-communication)

## Requirements

- Python 3.11
- Docker
- Git

## Installation

1. Clone the repository:

    ```sh
    git clone https://github.com/brainstems/jedai-backend-no-input.git
    cd jedai-backend-no-input
    ```

2. Create a virtual environment and activate it:

    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. Install the dependencies:

    ```sh
    pip install -r requirements.txt
    ```

## Environment Variables

Copy the `.env.example` file to `.env` in the root directory of the project and update the variables as needed:

```sh
cp .env.example .env
```

## Running the Application

To run the application locally:

```sh
uvicorn app.main:app --host 0.0.0.0 --port 4000 --reload
```

## Docker Usage

### Building and Running with Docker

1. Build the Docker image:

    ```sh
    docker build -t jedai-backend-no-input .
    ```

2. Run the Docker container:

    ```sh
    docker run -p 4000:4000 --env-file .env jedai-backend-no-input
    ```