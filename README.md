# Secure Persona Prediction and Data Leakage Prevention System

This project is a Python-based security system that predicts user behavior patterns and prevents potential data leaks.

## Features

1. **Persona Prediction Module**
   - Uses machine learning to classify user behavior as Normal, Suspicious, or Malicious
   - Trains on user behavior data (login time, file access patterns, etc.)
   - Provides real-time prediction of user personas

2. **Data Leakage Prevention Module**
   - Monitors file system activities 
   - Detects USB device connections
   - Scans for potential data leaks in text/emails
   - Raises alerts for suspicious activities

3. **GUI Dashboard**
   - Displays user persona predictions
   - Shows file activity logs
   - Presents alerts for potential data leaks

## Installation

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

Run the main application:
```
python main.py
```

For the dashboard interface:
```
streamlit run gui/dashboard.py
```

## Project Structure

- `/data`: Sample data and datasets
- `/model`: ML model implementation
- `/monitoring`: File and data leak monitoring
- `/gui`: Streamlit dashboard
- `/logs`: Application logs 