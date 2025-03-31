


## DartScoreMate

<a href="#Tab1">ReadMe</a> | 
<a href="#Tab2">Team Charter</a> | 


<div id="tab1" class="tabcontent">
  <h3>Einführung</h3>
  <p># DartScoreMate_Softwareentwicklung2
<details>
  <summary>Click to expand</summary>

  **THIS README STILL NEEDS TO BE WRITTEN OUT**: Sections might include Project Description, Explanation of Key Concepts, Links to Frameworks/important packages, ..

  1. **Header** – short introduction + table of contents  
  2. **Project description and motivation**  
  3. **Required apps/packages/frameworks** (and in our case, hardware components)  
  4. **Guide on how to start the app**  
  5. **Explanation of test cases** that are incorporated in GitLab and how to use them (linked issues 11)  
  6. **Introduction of key app concepts** (e.g., the image detection algorithm if we have it ready) with URLs to further resources  
  7. **Introduction of project members** – their skills and tasks in the project  
  8. **Project status**  

</details>


We want to build a Dart Score web-app, which measures a dart player's current score in real-time 
and based on the collected score data gives suggestions for the next "moves" of a player in order to get the highest possible score. 

**Key elements:** 
Real-time score data collected via cameras installed on a dart field 
An integrated AI model which calculates best possible moves 
A user interface which displays current score and suggested further throws


**Features of V1:**
<details>
  <summary>Click to expand</summary>

Create Users ✅
Track Score ✅
Save Games (SQL/text files) 
ChatGPT Integration (Prompt: You are a darts export and answer specific questions related to darts)... ✅
Live-View of Dart Board (static) ✅

**Advanced Features**

Live Video of Dart Board 🆗
User-Login 
Detect Score from Image
Personalized Shot Recommendations 

</details>

## Current Status
✅ [flask environment ](https://gitlab.web.fh-kufstein.ac.at/hillebranddaniel/dartscoremate_softwareentwicklung2/-/blob/main/src/python/main.py?ref_type=heads)


✅ [docker file](https://gitlab.web.fh-kufstein.ac.at/hillebranddaniel/dartscoremate_softwareentwicklung2/-/blob/main/Dockerfile?ref_type=heads)

✅ [captured images of dartboard with arrows](https://gitlab.web.fh-kufstein.ac.at/hillebranddaniel/dartscoremate_softwareentwicklung2/-/tree/main/src/python/data/captured_images?ref_type=heads)

✅ [streamlit camera caption app ](https://gitlab.web.fh-kufstein.ac.at/hillebranddaniel/dartscoremate_softwareentwicklung2/-/tree/develop/src/pic_snap?ref_type=heads)



## Grading
<details>
  <summary>Click to expand</summary>

<p> Current estimated points are marked in 🔵blue</span>.


* OOP & Framework (50) 🔵30
* Unittests (5) 🔵2
* Requirements / Docker (10) 🔵5
* Documentation (10) 🔵3
* Gitlab (10) 🔵10
* Presentation (15) 🔵2

### remarks
- ❌ no hand-in with just one file 
- ❌ meaningless commit-messages: use standard words (FIX, FEAT, DOCS,...) and effective description
- ✅ good code logic (design patterns, classes, ...)
- ✅ monitor package dependencies (conda + uv/`requirements.txt`)
- ✅ code documentation (docstrings, comments, ...)
- ✅ Unittests: best practice = one per function
- ✅ Presentation is on **May $\mathbf{16^{th}}$** with 80-90\% of project complete.

</details>



## Authors and acknowledgment
**Patrick Feller**

✅make first flask environment 

**Chris Lehmann**
Unit tests 



**Kathrin Lindauer**
SQL



**Ana Orkić**
CSS


**Daniel Hillebrand**
Project Management | Docker | Gitlab | Model Training

## Links
* [Moodle-Course Softwaredevelopment II](https://weblearn.fh-kufstein.ac.at/course/view.php?id=2643)
* [Darts Gitlab Project Inspiration](https://github.com/TheAlgorithms/Dart)

## Project status

Planned deploy of a first app deploy with this week. Some KVPs and Preparing the Presentation in April. 

## Meeting History
- 2025-03-10 6pm via TeamsTeam (project kickoff meeting)
- 2025-03-17 6pm via TeamsTeam 
- 2025-03-24 6pm via TeamsTeam 
- 2025-03-21 6pm via TeamsTeam

$\Rightarrow$ **next meeting: 2025-04-14 6pm via TeamsTeam** $\Leftarrow$ 
<div id="Team Charter" class="tabcontent">
  <h3>Team Charter</h3>
  <p>
  <details>
  <summary>Click to expand</summary>

  Wir arbeiten selbstständig und formulieren bei Fragen konkrete Problemstellungen


        
      
Wir fragen Hilfe an, indem wir andere Leute in Issues markieren, und antworten zeitnah auf Fragen, die an uns gestellt wurden.


        
      
Wir dokumentieren unseren Arbeitsfortschritt sauber in den uns zugewiesenen Issues und halten diese Dokumentation immer aktuell (inkl. Time-Track)


        
      
Wir versuche, Deadlines einzuhalten und melden uns rechtzeitig, wenn wir für ein Issue mehr Zeit brauchen oder eine Aufgabe nicht alleine schaffen


        
      
Wir kommunizieren vorwiegend über GitLab/Teams und nur in dringenden Fällen über WhatsApp


        
      
Wir arbeiten alle in separaten (Feature)-Branches, Mergen diesen nach Develop und nur stabile Versionen in den main branch.</p>
</div>

</details>


