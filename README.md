# DartScoreMate – Real-time Dart Score Recognition Web App

## 📚 Table of Contents
- [DartScoreMate – Real-time Dart Score Recognition Web App](#dartscoremate--real-time-dart-score-recognition-web-app)
  - [📚 Table of Contents](#-table-of-contents)
  - [🔍 About the Project](#-about-the-project)
  - [✨ Features](#-features)
  - [Features](#features)
    - [Advanced Features](#advanced-features)
  - [Current Status](#current-status)
  - [Grading](#grading)
  - [Current estimated points are marked in 🔵 blue.](#current-estimated-points-are-marked-in--blue)
  - [Links](#links)
- [Project status](#project-status)
  - [🌳 Branches and Commits](#-branches-and-commits)
  - [🌿 Branches](#-branches)
    - [`develop` Branch](#develop-branch)
    - [`main` Branch](#main-branch)
    - [`feature` Branches](#feature-branches)
    - [Branch Naming Conventions](#branch-naming-conventions)
    - [Typical Workflow](#typical-workflow)
  - [✍️ Commit Message Convention](#️-commit-message-convention)
    - [Commit Types:](#commit-types)
- [🧪 Installation \& Setup](#-installation--setup)
  - [⚠️ Which App Features require Live Camera Feed?](#️-which-app-features-require-live-camera-feed)
  - [✅ How to Check if Your Setup Supports the Camera:](#-how-to-check-if-your-setup-supports-the-camera)
    - [🪟 Windows (Docker Desktop + WSL)](#-windows-docker-desktop--wsl)
    - [🐧 Linux](#-linux)
    - [🍎 macOS](#-macos)
  - [👥 Contributors](#-contributors)
  - [🚦 Status \& Roadmap](#-status--roadmap)
  - [🗓 Meeting History](#-meeting-history)

## 🔍 About the Project
DartScoreMate is a web-based application for tracking and enhancing dart games in real-time.  
It uses camera-based score detection and provides AI-powered recommendations for better play.


## ✨ Features
<details>
  <summary>✨ Click to expand</summary>
  
  ## Features
  - Create Users ✅  
  - Track Score ✅  
  - Save Games (SQL/text files)  
  - ChatGPT Integration (Prompt: You are a darts export and answer specific questions related to darts)... ✅  
  - Live-View of Dart Board (static) ✅  

  ### Advanced Features
  - Live Video of Dart Board 🆗  
  - User-Login  
  - Detect Score from Image  
  - Personalized Shot Recommendations

</details>

## Current Status
✅ flask environment  
✅ docker file  
✅ captured images of dartboard with arrows  
✅ streamlit camera caption app

## Grading 
<details>
  <summary>Click to expand</summary>

  ## Current estimated points are marked in 🔵 blue.
  - OOP & Framework (50) 🔵37
  - Unittests (5) 🔵5
  - Requirements / Docker (10) 7
  - Documentation (10) 🔵5
  - Gitlab (10) 🔵10
  - Presentation (15) 🔵2

  ❌ no hand-in with just one file  
  ❌ meaningless commit-messages: use standard words (FIX, FEAT, DOCS,...) and effective description  
  ✅ good code logic (design patterns, classes, ...)  
  ✅ monitor package dependencies (conda + uv/requirements.txt)  
  ✅ code documentation (docstrings, comments, ...)  
  ✅ Unittests: best practice = one per function  
  ✅ Presentation is on **May** $\mathbf{16^{th}}$ with 80-90% of project complete.

</details>

## Links
[📘 Moodle Course – Softwaredevelopment II](https://weblearn.fh-kufstein.ac.at/course/view.php?id=2643)  
[🎯 Dart GitHub Inspiration Project](https://github.com/TheAlgorithms/Dart)


# Project status 
First stable version of app is rolled out. Now working on the presentation for Mid-May.

## 🌳 Branches and Commits
<details>
  <summary>Click to expand</summary>

  ## 🌿 Branches

We use a structured Git workflow to keep our codebase stable and organized.

### `develop` Branch
- **Default and protected branch**
- Starting point for new branches (features, fixes, etc.)
- New branches are created from `develop` and later merged back into it.
- Once a set of features is complete and texted, `develop` is merged into `main`

### `main` Branch
* **Protected Branch**
* Contains **stable, production-ready versions** of the project.
* No direct feature development takes place here
* Only thoroughly tested code from `develop` is merged into `main`

### `feature` Branches

* Used for developing `**new features** or **bug fixes**.
* Always created from the `develop` branch
* After completion, feature branches are merged back into `develop` 

### Branch Naming Conventions

* Features: `feature_your-feature-name` or `feature/your-feature-name`
* Fixes: `fix_your-fix-name` or `fix/your-fix-name`

### Typical Workflow

```
                     +------------------------+
                     |         main           |
                     |   (stable releases)    |
                     +-----------^------------+
                                 |
                      (merge from develop)
                                 |
                     +-----------+-------------+
                     |        develop          |
                     |  (integration branch)   |
                     +-----------^-------------+
                                 |
      +--------------+-----------^-------------+--------------+
      |                      |        |                       |
      +------------+       +------------+        +------------+
      | feature/   |       | feature/   |        | fix/       |
      | new-api    |       | ui-desing  |        | typo-fix   |
      +------------+       +------------+        +------------+
```
---

## ✍️ Commit Message Convention

We follow a **conventional commit** style to make our commit history clear and organized. Commit messages should use one of the following prefixes:

### Commit Types:
- **FEAT**: A new feature or functionality.  
  Example: `FEAT: Add new user authentication flow`
  
- **DOCS**: Changes to documentation.  
  Example: `DOCS: Update README with setup instructions`
  
- **CHORE**: Routine tasks, maintenance, or refactoring without changing functionality.  
  Example: `CHORE: Update dependencies`

- **TESTS**: Adding or modifying tests.  
  Example: `TESTS: Write unit tests for user service`

- **FIX**: Bug fixes or correcting code that was not working as expected.  
  Example: `FIX: Resolve issue with user login error handling`

- **REFACTOR**: Code improvements without changing functionality (e.g., cleaning up or optimizing code).  
  Example: `REFACTOR: Simplify user profile rendering logic`

- **STYLE**: Non-functional changes like formatting or styling (e.g., fixing typos, adjusting layout).  
  Example: `STYLE: Fix indentation in authentication module`


</details>

# 🧪 Installation & Setup

<details>
  <summary>👾 What You'll need</summary>

  - 🐍 **Python 3.8 or higher**  
  - 📷 **OpenCV-compatible OS** (for camera support)  
  - 💾 **SQL Database** access (used to store game data)  
  - 🐋 **Docker** (for running the app in a container)  
  - 🧠 **Groq API Key** (for the built-in chatbot — create one for free [here](https://console.groq.com/keys))
</details>


<details>
  <summary>🤖 How to get started</summary>
  
1. **Clone the Project:** 
    ```
    git clone https://gitlab.web.fh-kufstein.ac.at/hillebranddaniel/dartscoremate_softwareentwicklung2.git
    ```
2. **Navigate to the project:** 
    ```
    cd dartscoremate_softwareentwicklung2
    ```
3. **Add Secrets to your Repo:** 
   1. navigate to `src/flask_app`
   2. create a new file `.env`
   3. Fill out the following lines and paste them into the `.env`-file:
    ```
    DB_HOST=XXXXX
    DB_PORT=XXXXX
    DB_USER=XXXXX
    DB_PASSWORD=XXXXX
    DB_NAME=XXXXX
    GROQ_API_KEY=XXXXX
    ``` 
4. **To start the app locally:**
   1. initialize a new virtual environment 
    ```
    python3 -m venv venv
    source venv/bin/activate
    ```
    2. install all required packages with `uv`
    ```
    pip install uv
    uv pip install .
    ```
    3. run the main darts app via `python3 -m src.flask_app.main`
    4. run the streamlit app via `streamlit run src/pic_snap/app.py`
 5. **To start the app from Docker:** 
    1. run `docker-compose up --build`
</details>
<details>
<summary>🐋 Docker Setup</summary>

You can run this project in Docker across Windows, Linux, or macOS, and most of the app's functionalities will work just fine. However, some features (such as those requiring a **live camera feed**) may face **limitations** depending on your OS and hardware access—especially on Windows due to **WSL** constraints.

## ⚠️ Which App Features require Live Camera Feed?

1. **Board Status**: Shows live image of dartboard
2. **Score Prediction**: Get score prediction of current throw based on live dartboard images.
3. **Pic Snap**: A small streamlit app to take pictures of your dartboard and save them to a directory. Mainly useful for training a score-prediction algorithm. 

## ✅ How to Check if Your Setup Supports the Camera:

### 🪟 Windows (Docker Desktop + WSL)

1. Mount your USB camera to WSL using [`usbipd`](https://learn.microsoft.com/de-de/windows/wsl/connect-usb): 
    ```
    usbipd list # list all usb devices
    usbipd bind --busid X-X # make device X-X accessible to WSL
    usbipd attach --wsl --busid X-X
    ```
2. Check if the USB device is detected in WSL: 
    ```
    lsusb
    ```
    return should be similar to 
    ```
    Bus 001 Device 002: ID 0bda:5844 Realtek Semiconductor Corp. USB Camera
    ```
3. Check if the USB device is detected as as a webcam 
    ```
    ls -l /dev/video*
    ```
    Should return 
    ```
    crw-rw---- 1 root video 81, 0 Mar 31 13:00 /dev/video0
    crw-rw---- 1 root video 81, 1 Mar 31 13:00 /dev/video1
    ```
4. Test your camera using `ffmpeg`, `cheese` or `guvcview`. If you see an image, then your Setup Supports USB Camera Image Feed.
5. If 1-3 succeeded but 4 failed, this is most likely because of missing camera drivers in WSL. You can tackle this issue by building a new WSL-kernel from scratch that includes the necessary camera drivers. This process is not so straightforward, so I recommend to follow [this video guide](https://www.youtube.com/watch?v=t_YnACEPmrM&ab_channel=AgileDevArt) by *AgileDevArt*. After successfully build a new WSL-Kernel with the right drivers, reopen any foto-app like `ffmpeg`, `cheese` or `guvcview` and see if you can now see an image. 
6. If you still don't see an image, it is very likely that it is still a driver issue. Troubleshooting here can be very difficult. An alternative way to tackle this problem is by installing a proper Linux distribution like *Ubunutu* with dual-boot and running Docker from there. See [this guide](https://gcore.com/learning/dual-boot-ubuntu-windows-setup) for further reference.

### 🐧 Linux
Running the project on native Linux provides the **most reliable camera support.** Docker will have full access to the host's USB devices, assuming you grant permission.

If you plan to use live camera features, this is the **recommended setup.**

### 🍎 macOS

macOS does not allow Docker containers direct access to USB cameras due to virtualization and security constraints.

**Live camera features will not work** on macOS unless you implement a workaround (e.g., camera-to-HTTP feed), which is outside the scope of this project.

</details>


## 👥 Contributors
- Patrick Feller – Flask setup  
- Chris Lehmann – Unit tests  
- Kathrin Lindauer – SQL  
- Ana Orkić – CSS  
- Daniel Hillebrand – PM, Docker, GitLab  
- Lyudmila Shamina - 


## 🚦 Status & Roadmap
- ✅ Flask environment  
- ✅ Docker ready  
- ✅ Static board + image capture  
- ✅ Streamlit camera test  
- ⏳ Score detection in progress  
- ⏳ Save games to SQL in progress  
- 📌 First deploy planned April  
- 🗓 Final presentation: May 16


## 🗓 Meeting History
- 2025-03-10 – Kickoff  
- 2025-03-17 – Planning  
- 2025-03-24 – Review  
- 2025-04-14 – Next meeting
