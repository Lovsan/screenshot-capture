# ScreenCapture Pro v1

**A simple GUI tool to capture screenshots.**  
This application listens for the PrintScreen key and automatically saves your screenshots, uploads them to Imgur, and lets you view, edit, and delete them from an intuitive interface.

## Features

- **Instant Capture:**  
  Automatically capture screenshots when the PrintScreen key is pressed.

- **Imgur Integration:**  
  Upload your screenshots to Imgur with a single click.

- **Gallery View:** - called "screenshot history"
  Browse your screenshots in a grid layout with thumbnail previews.

- **Editing and Management:**  
  Open screenshots in your default image editor, rename them, or delete them as needed.
    - **Note:** The image editor feature is currently under development and will be added in an upcoming update. Stay tuned for more details!

## Screenshots

*Below are placeholder images for the screenshots. Replace them with your actual screenshots when ready.*

<div align="center">
  <img src="screenshot_2025-02-08_00-38-27.png" alt="Screenshot 1" width="400px" />
  <img src="screenshot_2025-02-08_00-42-01.png" alt="Screenshot 2" width="400px" />
  <img src="screenshot_2025-02-08_00-49-12.png" alt="Screenshot 3" width="400px" />
</div>

## Installation

1. **Clone the repository:**

```bash
   git clone https://github.com/Lovsan/screenshot-capture.git
```
 

2. **Install dependencies:**
Ensure you have Python installed. Then install the required packages:

```bash
pip install -r requirements.txt
```

3. **Run the application:**

```bash
python desktop_client/main.py
```

## Usage

**Capture a Screenshot:**
Press the PrintScreen key to capture the screen.

**Manage Screenshots:**
Right-click on any screenshot thumbnail to open options like "Open Full Size", "Edit Image", "Rename", "Delete", or "Upload (Imgur)".

**Adjust Settings:**
Use the provided controls to change thumbnail dimensions and other preferences.


**Upcoming Version 2**
Version 2 is currently in the works and will include:

A complete UI overhaul with a responsive design using Flask and Bootstrap.
The ability to host and share images directly from our own server.
Advanced editing features.
User authentication and a personalized gallery experience.
Enhanced sharing options including social media integrations.
Stay tuned for updates!

**Contributing**
Contributions, bug reports, and feature suggestions are welcome! Feel free to open an issue or submit a pull request.

**License**
This project is licensed under the MIT License.
