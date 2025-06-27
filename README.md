# Image Uploader

A simple, secure web application for uploading, viewing, and deleting images, built with Flask. This project is configured for easy deployment on platforms like Render.

## Features

-   **Image Upload:** Supports `png`, `jpg`, `jpeg`, and `gif` files.
-   **Secure by Design:**
    -   Validates file content (magic numbers) to prevent malicious uploads.
    -   Generates random, secure filenames to avoid user input vulnerabilities.
    -   Protects against path traversal attacks on file deletion.
-   **Gallery View:** Displays all uploaded images, sorted with the newest first.
-   **IP Whitelisting:** Optional access control via an environment variable.
-   **Production Ready:** Uses Gunicorn as a WSGI server and WhiteNoise for efficient static file serving.

## Live Demo

[https://image-uploader-y9i0.onrender.com/]

## Tech Stack

-   **Backend:** Flask
-   **WSGI Server:** Gunicorn
-   **Static Files:** WhiteNoise
-   **Frontend:** HTML5, CSS3

## Setup & Run Locally

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/0xPolyCoder/image-uploader.git
    cd image-uploader
    ```
2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the development server:**
    ```bash
    python3 app.py
    ```
    The application will be available at `http://127.0.0.1:5000`.

## Deployment (Render)

This application is ready to deploy on Render. Simply connect your GitHub repository, and Render will automatically use the `Procfile` and `requirements.txt` to build and launch the service.

### Environment Variables

To configure the application, set the following environment variables in the Render dashboard:

-   `SECRET_KEY`: **(Required)** A long, random string for session security. Use Render's "Generate" button to create one.
-   `WHITELISTED_IP`: **(Optional)** If set, only this IP address can access the application. Example: `198.51.100.10`.


