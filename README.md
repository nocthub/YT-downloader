🎬 YT-Content-Downloader

A robust, multi-container web application for downloading YouTube content as high-quality Video (MP4) or Audio (MP3).

This project leverages the power of yt-dlp within an asynchronous backend (Flask) and provides a real-time, interactive user interface (Streamlit). Deploy the entire system with a single docker compose up command.

✨ Features

Dual Mode: Choose between downloading content as a high-resolution Video (.mp4) or extracting the Audio (.mp3).

Asynchronous Processing: Downloads run in the background via a dedicated Flask API, ensuring the Streamlit frontend remains responsive and never times out.

Real-Time Status: Monitor download progress with dynamic updates and speed indicators.

File Management: Access, stream preview, download, and delete previously captured media files from the integrated library.

Containerized: Built for easy deployment and scalability using Docker Compose.

⚙️ Tech Stack & Architecture

This application follows a service-oriented architecture, separated into two key containers:

Service

Role

Technology

Port

Frontend

User Interface, status polling, and file library display.

Python, Streamlit

8501

Backend (API)

Manages asynchronous download tasks, video info fetching, and file serving/deletion.

Python, Flask, yt-dlp

5000

The two containers communicate via a Docker network, and they share the /downloads directory via a shared volume for persistent file storage.

🚀 Getting Started

These instructions will get a copy of the project up and running on your local machine using Docker.

Prerequisites

You must have Docker and Docker Compose installed on your system.

Install Docker

Install Docker Compose

1. Project Structure

Ensure your project directory contains the necessary files:

yt-content-downloader/
├── app.py           # Streamlit Frontend Code
├── api.py           # Flask Backend API Code
├── Dockerfile       # Dockerfile for the Streamlit Frontend
├── requirements.txt # Dependencies for Streamlit
└── docker-compose.yml (Create this file)


2. Docker Compose Configuration

Create a docker-compose.yml file to define and orchestrate the two services.

version: '3.8'

services:
  # --- Backend Service (Flask API) ---
  yt-backend:
    container_name: yt-backend
    build:
      context: .
      # Assuming you use the main Dockerfile for the Flask API for simplicity, 
      # or you can create a dedicated Dockerfile for the API
      dockerfile: Dockerfile 
    image: yt-downloader-backend:latest
    command: ["python", "api.py"]
    # Shared volume where downloaded files will be saved
    volumes:
      - ./downloads:/app/downloads 
    ports:
      - "5000:5000"
    
  # --- Frontend Service (Streamlit App) ---
  yt-frontend:
    container_name: yt-frontend
    build:
      context: .
      dockerfile: Dockerfile
    image: yt-downloader-frontend:latest
    command: ["streamlit", "run", "app.py", "--server.address=0.0.0.0"]
    # Mount the same volume to access downloaded files
    volumes:
      - ./downloads:/app/downloads 
    ports:
      - "8501:8501"
    # Ensure backend is ready before starting frontend
    depends_on:
      - yt-backend


3. Running the Application

Create the Downloads Folder:

mkdir downloads


Build and Run Services:

docker compose up --build -d


This command builds the images, starts both containers in detached mode, and creates the shared volume.

Access the App:
Open your web browser and navigate to:

http://localhost:8501


🛑 Stopping the Application

To stop and remove the containers, volumes, and network, run:

docker compose down -v


🖼️ Screenshots (Optional)

If you have a screenshot of the running application, embed it here.

Replace https://learn.microsoft.com/en-us/answers/questions/4122543/screenshots-folder with your actual image link:

![Application Screenshot](https://placehold.co/800x400/1C3A3A/f0f2f6?text=Screenshot+of+YT+Downloader+App)


🤝 Contribution

Contributions are welcome! If you find a bug or have an enhancement idea, please open an issue or submit a pull request.

📝 License

This project is licensed under the MIT License - see the LICENSE file for details.
