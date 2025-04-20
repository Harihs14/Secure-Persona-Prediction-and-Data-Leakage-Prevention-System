# Secure Persona System - Usage Guide

This document provides detailed instructions on how to use the Secure Persona Prediction and Data Leakage Prevention System.

## Installation

1. Clone the repository:
   ```
   git clone <repository_url>
   ```

2. Navigate to the project directory:
   ```
   cd Secure_Persona_System
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Running the System

### Basic Usage

To start the system with default settings:

```
python main.py
```

This will:
1. Train a new model if none exists (or load an existing one)
2. Start the file monitoring system
3. Launch the Streamlit dashboard

### Command Line Options

The main script supports several command line options:

- `--train`: Force training a new model even if one already exists
- `--model-type`: Specify the model type (RandomForest or LogisticRegression)
- `--monitor-path`: Specify paths to monitor (can be used multiple times)
- `--no-dashboard`: Run without launching the dashboard

Examples:

```
# Train a new LogisticRegression model
python main.py --train --model-type LogisticRegression

# Monitor specific directories
python main.py --monitor-path /path/to/documents --monitor-path /path/to/downloads

# Run without dashboard (for headless servers)
python main.py --no-dashboard
```

## Using the Dashboard

The Streamlit dashboard is available at http://localhost:8501 when the system is running.

### Dashboard Features

1. **User Persona Prediction**
   - View the current predicted persona (Normal, Suspicious, Malicious)
   - Update the prediction using real-time behavior data
   - Visualize behavior metrics

2. **File Activity Monitoring**
   - See real-time file access logs
   - View file activity distribution charts

3. **Security Alerts**
   - Monitor security alerts in real-time
   - Color-coded by severity level (low, medium, high)
   - View alert distribution charts

## Testing the System

You can run tests to verify that all components are working correctly:

```
python test_system.py
```

This will test:
1. Data generation functionality
2. Persona prediction model
3. File monitoring and data leak detection

## Customizing Sensitivity

To customize the sensitive keywords for data leak detection, modify the `FileMonitor` initialization in `monitoring/file_monitor.py`:

```python
monitor = FileMonitor(
    paths_to_monitor=['/path1', '/path2'],
    sensitive_keywords=[
        "password", "confidential", "secret", "private", 
        # Add custom keywords here
    ]
)
```

## Using Individual Components

### Persona Prediction Model

```python
from model.persona_model import PersonaModel

# Initialize model
model = PersonaModel(model_type="RandomForest")

# Train model
import pandas as pd
data = pd.read_csv("user_behavior_data.csv")
metrics = model.train(data)

# Predict persona
user_behavior = {
    'login_hour': 14,
    'session_duration_mins': 120,
    'files_accessed': 30,
    'unique_directories_accessed': 5,
    'usb_connected': 0,
    'websites_visited': 20,
    'email_sent_count': 5,
    'after_hours': 0,
    'keyboard_intensity': 60
}
persona = model.predict(user_behavior)
print(f"Predicted persona: {persona}")
```

### File Monitor

```python
from monitoring.file_monitor import FileMonitor

# Initialize monitor
monitor = FileMonitor(paths_to_monitor=['/path/to/monitor'])

# Start monitoring
monitor.start_monitoring()

# Check file for sensitive data
has_sensitive, matches = monitor.check_file_for_sensitive_data('/path/to/file.txt')
if has_sensitive:
    print(f"Found {len(matches)} sensitive matches")
    for match in matches:
        print(f"Keyword: {match['keyword']} at line {match['line']}")

# Stop monitoring
monitor.stop_monitoring()
``` 