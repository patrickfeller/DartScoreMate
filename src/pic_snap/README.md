# Streamlit Camera Capture Application

A short Streamlit application that collects pictures from three cameras to generate a dataset for potential model training. For your Dart-Scoring-Application.

## Start Application
1. Install required packages from `requirements.txt`:
   ```bash
   pip install -r requirements.txt
   ```
2. Start the application with:
   ```bash
   streamlit run app.py
   ```

## How to Use the App
1. Choose the correct camera for Camera A, B, and C.
2. Adjust your preferred camera settings and specify the save path in the sidebar.
3. Enter the name of the folder where the pictures should be saved.
4. Click on **Capture Image** to take a picture.

## Notes
- For optimal performance, use at least two different USB controllers on your PC.
- If using only one USB controller with a USB hub, you might need to restart your PC several times.
