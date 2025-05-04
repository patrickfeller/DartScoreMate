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
  - [Technologies and Branches](#technologies-and-branches)
  - [🧰 Tech Stack](#-tech-stack)
  - [🌿 Branches](#-branches)
    - [`develop` Branch](#develop-branch)
    - [`main` Branch](#main-branch)
    - [`feature` Branches](#feature-branches)
    - [Branch Naming Conventions](#branch-naming-conventions)
    - [Typical Workflow](#typical-workflow)
- [🧪 Installation \& Setup](#-installation--setup)
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
  - OOP & Framework (50) 🔵30
  - Unittests (5) 🔵2
  - Requirements / Docker (10) 🔵5
  - Documentation (10) 🔵3
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

## Technologies and Branches
<details>
  <summary>Click to expand</summary>
  
  ## 🧰 Tech Stack
  - Python  
  - Flask  
  - Virtual enviroment (venv)
  - OpenCV (cv2)  
  - Streamlit (camera testing)  
  - SQL (for saving games)  
  - Docker  
  - Groq API (for recommendations)
  - .env file with Api key


  ---

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


</details>

# 🧪 Installation & Setup

<details>
  <summary>👾 What you need?</summary>

  - Python  
  - Flask  
  - Virtual ebviroment (venv)
  - OpenCV (cv2)  
  - Streamlit (camera testing)  
  - SQL (for saving games)  
  - Docker  
  - Groq API (for recommendations)
  - .env file with Api key
</details>

<details>
  <summary>🤖 How to start?</summary>
  
1. git clone https://gitlab.web.fh-kufstein.ac.at/hillebranddaniel/dartscoremate_softwareentwicklung2.git
2. Navigate to the project: (cd dartscoremate_softwareentwicklung2)
3. -m venv venv (source venv/bin/activate)
4. pip install -r requirements.txt
5. Add .env file with Api key (GROQ_API_KEY=your_key)
6. -m src.flask_app.main
7. Open in browser your http://localhost:5000

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
