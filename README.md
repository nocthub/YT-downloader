# 🎬 YT-Content-Downloader

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?style=for-the-badge&logo=python&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-24.0%2B-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

A robust, full-stack web application for downloading YouTube content as high-quality **Video (MP4)** or **Audio (MP3)**.

This project leverages the power of **yt-dlp** within an asynchronous backend (Flask) and provides a real-time, interactive user interface (Streamlit). The entire system is containerized for easy deployment.

---

## ✨ Features

- **🎥 Dual Mode**: Choose between downloading high-resolution Video (`.mp4`) or extracting Audio (`.mp3`).
- **⚡ Asynchronous Processing**: Downloads run in the background via a dedicated Flask API, ensuring the UI remains responsive.
- **📊 Real-Time Status**: Monitor download progress with dynamic updates and speed indicators.
- **📂 File Management**: Access, stream, download, and delete media files directly from the integrated library.
- **🐳 Dockerized**: Built for instant deployment using Docker Compose.

---

## ⚙️ Tech Stack & Architecture

The application follows a microservices architecture with two main containers sharing a volume:

| Service | Role | Technology | Port |
| :--- | :--- | :--- | :--- |
| **Frontend** | UI, status polling, and file library. | Python, Streamlit | `8501` |
| **Backend** | Async download tasks & file management. | Python, Flask, yt-dlp | `5000` |

graph TD
    User([User]) -->|Interacts| Frontend[Streamlit Frontend <br> Port 8501]
    Frontend -->|Requests Download| Backend[Flask API <br> Port 5000]
    Backend -->|Spawns Process| YTDLP[yt-dlp Engine]
    YTDLP -->|Downloads| YouTube[YouTube Servers]
    YTDLP -->|Saves File| SharedVol[Shared Docker Volume]
    SharedVol -->|Reads File| Frontend
    Frontend -->|Delivers File| User
    

### Project Structure
```bash
YT-downloader/
├── BACKEND/             # Flask API & yt-dlp logic
│   ├── api.py
│   ├── Dockerfile
│   └── ...
├── FRONTEND/            # Streamlit User Interface
│   ├── app.py
│   ├── Dockerfile
│   └── ...
├── docker-compose.yml   # Orchestration config
└── README.md
