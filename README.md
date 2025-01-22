[![example-fastapi](https://github.com/koyeb/example-fastapi/actions/workflows/deploy.yaml/badge.svg)](https://github.com/koyeb/example-fastapi/actions)

# Chat Application

## Table of Contents
1. Introduction
2. Features
3. Data Flow
4. Data Flow Architecture
   - Chat Endpoint Flow
   - Data Ingestion Flow
5. Usage Guide
    - Home Endpoint
    - Chat Endpoint
    - Add Context Endpoint
    - Get Chat Logs Endpoint
    - Review Chat Endpoint
    - Delete Documents Endpoint
6. Deployment
    - Local Deployment
    - Docker Deployment
7. Swagger Documentation

## Introduction
Welcome to the Chat Application! This application allows users to interact with an AI assistant, store and retrieve chat logs, and manage multilingual questions and answers. The application uses MongoDB for data storage and supports multiple languages.

## Features
- Chat with an AI assistant
- Store and retrieve chat logs
- Add and manage multilingual questions and answers
- Review and rate chat responses
- Delete specific questions with ID's from particular collections for management purposes.

## Data Flow
1. **User Interaction:** Users interact with the AI assistant through the chat endpoint.
2. **Data Storage:** Admin questions and AI responses are stored in MongoDB collections.
3. **Multilingual Support:** Questions and answers can be added in multiple languages and are translated automatically.
4. **Review and Rating:** Users can review and rate chat responses, which are stored for further analysis.
5. **Data Retrieval:** Admin can retrieve chat logs and review questions as needed.

## Data Flow Architecture

### Chat Endpoint Flow
```mermaid
graph TD
    A[User Request] --> B[/chat endpoint]
    B --> C{Knowledge Base Match?}
    C -->|Yes| D[Return Predefined Answer]
    C -->|No| E[Forward to GROQ LLM]
    E --> F[Generate Response] 
    F --> G[Log Interaction]
    D --> G
    G --> H[Return to User]
    H --> I{Review Question Match?}
    I -->|Yes| J[Return Similar Answer]
    I -->|No| K[Add to Review Questions]
```

### Data Ingestion Flow
```mermaid
graph TD
    A[Admin Input] --> B[/add_multilingual_question]
    B --> C[Validate Language Pairs]
    C --> D[Translation Service]
    D --> E[Store in MongoDB]
    E --> F[Update Search Index]
```

## Usage Guide

### Home Endpoint
- **Purpose:** To check if the application is running correctly.
- **Usage:** Access the root URL (`/`) of the application. You should see a message indicating that the site is running correctly.

### Chat Endpoint
- **Purpose:** To interact with the AI assistant.
- **Usage:** Send a POST request to the `/chat` endpoint with your question. The AI assistant will respond, and the conversation will be logged in the database. If the `id` parameter is provided and valid, the previous conversation context associated with that `id` will be used to generate the response. If the `id` is not provided or invalid, a new `id` will be generated, and the response will be based on the new context. Unanswered questions are stored in the unanswered questions collection if not already present.

### Add Context Endpoint
- **Purpose:** To add questions and answers in multiple languages.
- **Usage:** Send a POST request to the `/add_multilingual_question` endpoint with your question and answer in the desired languages. The application will translate and store them in the database.

### Get Chat Logs Endpoint
- **Purpose:** To retrieve chat logs from the past X hours or all logs if no parameter is provided.
- **Usage:** Send a GET request to the `/get_chat_logs` endpoint with an optional `hours` parameter to filter logs from the past X hours.

### Review Chat Endpoint
- **Purpose:** To add a chat log to the Review-Questions collection for further review.
- **Usage:** Send a POST request to the `/rate_chat` endpoint with the log ID of the chat you want to review. The chat log will be added to the Review-Questions collection.

### Delete Documents Endpoint
- **Purpose:** To delete a specific review question by ID.
- **Usage:** Send a DELETE request to the `/review_questions/{id}` endpoint with the ID of the review question you want to delete.

## Deployment

### Local Deployment
1. **Install Dependencies:**
    - Ensure you have Python installed.
    - Install the required dependencies using the following command:
      ```sh
      pip install -r requirements.txt
      ```

2. **Run the Application:**
    - Start the application using the following command:
      ```sh
      uvicorn main:app --reload
      ```
    - The application will be available at `http://127.0.0.1:8000`.

### Docker Deployment
1. **Build the Docker Image:**
    - Build the Docker image using the following command:
      ```sh
      docker build -t fastapi-chat-app .
      ```

2. **Run the Docker Container:**
    - Run the Docker container using the following command:
      ```sh
      docker run -p 8000:8000 fastapi-chat-app
      ```

3. **Using Docker Compose:**
    - Alternatively, you can use Docker Compose to build and run the application:
      ```sh
      docker-compose up --build
      ```
    - The application will be available at `http://127.0.0.1:8000`.

## Swagger Documentation
You can access the Swagger documentation for all endpoints at the `/docs` endpoint. This provides an interactive interface to test and understand the API endpoints.

Thank you for using the Chat Application! If you have any questions or need further assistance, please refer to the documentation or contact support.

## Contributing

If you have any questions, ideas or suggestions regarding this application sample, feel free to open an [issue](//github.com//koyeb/example-fastapi/issues) or fork this repository and open a [pull request](//github.com/koyeb/example-fastapi/pulls).
