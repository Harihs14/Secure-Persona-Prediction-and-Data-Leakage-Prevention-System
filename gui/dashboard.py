import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import sys
import time
import threading
import queue
from datetime import datetime, timedelta
import random

# Add parent directory to path to import project modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from model.persona_model import PersonaModel
from monitoring.file_monitor import FileMonitor
from utils import setup_logger, timestamp

# Set up logger
logger = setup_logger("dashboard", "logs/dashboard.log")

# Initialize session state variables
if 'file_logs' not in st.session_state:
    st.session_state.file_logs = []
if 'alerts' not in st.session_state:
    st.session_state.alerts = []
if 'user_behavior' not in st.session_state:
    st.session_state.user_behavior = None
if 'persona' not in st.session_state:
    st.session_state.persona = None
if 'monitor' not in st.session_state:
    st.session_state.monitor = None
if 'log_queue' not in st.session_state:
    st.session_state.log_queue = queue.Queue()

def initialize_system():
    """Initialize the system components."""
    # Load or train model
    model_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                             'model', 'persona_model.joblib')
    scaler_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                              'model', 'scaler.joblib')
    
    # Initialize model
    st.session_state.model = PersonaModel()
    
    # Try to load model, or train if not available
    if os.path.exists(model_path) and os.path.exists(scaler_path):
        st.session_state.model.load_model(model_path, scaler_path)
        logger.info("Model loaded from file")
    else:
        # Import data generator
        sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data'))
        from data.data_generator import generate_synthetic_data
        
        # Generate data and train model
        data = generate_synthetic_data(n_samples=1000)
        st.session_state.model.train(data)
        
        # Save model
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        st.session_state.model.save_model(model_path, scaler_path)
        logger.info("Model trained and saved")
    
    # Initialize file monitor
    if not st.session_state.monitor:
        st.session_state.monitor = FileMonitor()
        
        # Custom log handler to capture logs for dashboard
        def log_capture_worker():
            while True:
                # Simulate receiving logs
                time.sleep(1)
                
                # 10% chance of adding file access log
                if random.random() < 0.1:
                    file_types = ['.docx', '.xlsx', '.pdf', '.txt', '.jpg', '.py']
                    file_paths = [
                        '/documents/report', '/downloads/data', 
                        '/desktop/project', '/pictures/image',
                        '/confidential/secret'
                    ]
                    action_types = ['created', 'accessed', 'modified', 'deleted']
                    
                    file_path = f"{random.choice(file_paths)}{random.choice(file_types)}"
                    action = random.choice(action_types)
                    log = {
                        'timestamp': timestamp(),
                        'type': 'file_access',
                        'action': action,
                        'path': file_path
                    }
                    st.session_state.log_queue.put(log)
                
                # 5% chance of adding an alert
                if random.random() < 0.05:
                    alert_levels = ['low', 'medium', 'high']
                    alert_messages = [
                        'Suspicious file access detected',
                        'Multiple login attempts',
                        'Sensitive data accessed',
                        'USB device connected',
                        'Large file transfer detected',
                        'Email with sensitive content detected'
                    ]
                    level = random.choice(alert_levels)
                    message = random.choice(alert_messages)
                    log = {
                        'timestamp': timestamp(),
                        'type': 'alert',
                        'level': level,
                        'message': message
                    }
                    st.session_state.log_queue.put(log)
        
        # Start log capture thread
        log_thread = threading.Thread(target=log_capture_worker)
        log_thread.daemon = True
        log_thread.start()

def process_queue():
    """Process the log queue."""
    try:
        while not st.session_state.log_queue.empty():
            log = st.session_state.log_queue.get_nowait()
            
            if log['type'] == 'file_access':
                st.session_state.file_logs.append(log)
                # Keep only the most recent 100 logs
                if len(st.session_state.file_logs) > 100:
                    st.session_state.file_logs.pop(0)
            
            elif log['type'] == 'alert':
                st.session_state.alerts.append(log)
                # Keep only the most recent 100 alerts
                if len(st.session_state.alerts) > 100:
                    st.session_state.alerts.pop(0)
    except Exception as e:
        logger.error(f"Error processing log queue: {str(e)}")

def predict_persona():
    """Predict the user persona based on current behavior."""
    # In a real application, this would collect real user behavior
    # For this simulation, we'll use random values
    
    # Get current hour
    current_hour = datetime.now().hour
    
    # Simulate current user behavior
    # Base values on time of day to create a pattern
    if 9 <= current_hour <= 17:  # Work hours
        login_hour = current_hour
        session_duration = random.randint(30, 480)
        files_accessed = random.randint(5, 50)
        unique_dirs = random.randint(1, 10)
        usb_connected = 1 if random.random() < 0.1 else 0
        websites = random.randint(5, 50)
        emails = random.randint(0, 20)
        after_hours = 0
        keyboard = random.randint(30, 100)
    else:  # After hours
        login_hour = current_hour
        session_duration = random.randint(5, 120)
        files_accessed = random.randint(1, 100)
        unique_dirs = random.randint(1, 20)
        usb_connected = 1 if random.random() < 0.3 else 0
        websites = random.randint(1, 30)
        emails = random.randint(0, 10)
        after_hours = 1
        keyboard = random.randint(10, 60)
    
    # Occasional random anomalies (15% chance)
    if random.random() < 0.15:
        anomaly_factor = random.randint(2, 5)
        files_accessed *= anomaly_factor
        unique_dirs *= anomaly_factor
        websites *= anomaly_factor
        emails *= anomaly_factor
        keyboard = random.randint(5, 200)
    
    # Create behavior data
    behavior = {
        'login_hour': login_hour,
        'session_duration_mins': session_duration,
        'files_accessed': files_accessed,
        'unique_directories_accessed': unique_dirs,
        'usb_connected': usb_connected,
        'websites_visited': websites,
        'email_sent_count': emails,
        'after_hours': after_hours,
        'keyboard_intensity': keyboard
    }
    
    # Store in session state
    st.session_state.user_behavior = behavior
    
    # Predict persona
    try:
        persona = st.session_state.model.predict(behavior)
        st.session_state.persona = persona
        logger.info(f"Predicted persona: {persona}")
        return persona
    except Exception as e:
        logger.error(f"Error predicting persona: {str(e)}")
        return "Unknown"

def main():
    """Main dashboard function."""
    # Page config
    st.set_page_config(
        page_title="Secure Persona System",
        page_icon="🔒",
        layout="wide"
    )
    
    # Initialize system if needed
    if 'model' not in st.session_state:
        initialize_system()
    
    # Title
    st.title("Secure Persona Prediction and Data Leakage Prevention System")
    
    # Process queue
    process_queue()
    
    # Create columns for layout
    col1, col2 = st.columns([1, 2])
    
    # Column 1: Persona Information
    with col1:
        st.subheader("User Persona")
        
        # Button to predict persona
        if st.button("Update Persona Prediction"):
            predict_persona()
        
        # Display persona
        if st.session_state.persona:
            persona = st.session_state.persona
            
            # Show different colors based on persona
            if persona == "Normal":
                st.success(f"Current Persona: {persona}")
            elif persona == "Suspicious":
                st.warning(f"Current Persona: {persona}")
            else:  # Malicious
                st.error(f"Current Persona: {persona}")
            
            # Display behavior data
            st.subheader("Current User Behavior")
            behavior_df = pd.DataFrame([st.session_state.user_behavior])
            st.dataframe(behavior_df)
            
            # Create chart for behavior metrics
            st.subheader("Behavior Metrics")
            fig, ax = plt.subplots(figsize=(8, 6))
            
            # Extract numeric features
            metrics = {k: v for k, v in st.session_state.user_behavior.items() 
                     if isinstance(v, (int, float)) and k not in ['login_hour']}
            
            # Create bar chart
            ax.bar(metrics.keys(), metrics.values())
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            
            st.pyplot(fig)
    
    # Column 2: Monitoring and Alerts
    with col2:
        # Tabs for different sections
        tab1, tab2 = st.tabs(["File Activity", "Alerts"])
        
        # Tab 1: File Activity
        with tab1:
            st.subheader("Recent File Activity")
            
            if st.session_state.file_logs:
                # Convert logs to DataFrame
                logs_df = pd.DataFrame(st.session_state.file_logs)
                
                # Sort by timestamp (newest first)
                logs_df = logs_df.sort_values('timestamp', ascending=False)
                
                # Create a filtered dataframe for display
                display_df = logs_df[['timestamp', 'action', 'path']]
                
                # Show table
                st.dataframe(display_df, use_container_width=True)
                
                # Show chart of activity types
                st.subheader("File Activity Distribution")
                
                # Count actions
                action_counts = logs_df['action'].value_counts()
                
                # Create pie chart
                fig, ax = plt.subplots(figsize=(8, 6))
                ax.pie(action_counts, labels=action_counts.index, autopct='%1.1f%%')
                ax.axis('equal')
                
                st.pyplot(fig)
            else:
                st.info("No file activity recorded yet.")
        
        # Tab 2: Alerts
        with tab2:
            st.subheader("Security Alerts")
            
            if st.session_state.alerts:
                # Convert alerts to DataFrame
                alerts_df = pd.DataFrame(st.session_state.alerts)
                
                # Sort by timestamp (newest first)
                alerts_df = alerts_df.sort_values('timestamp', ascending=False)
                
                # Create a filtered dataframe for display
                display_df = alerts_df[['timestamp', 'level', 'message']]
                
                # Color code by level
                def highlight_level(row):
                    if row.level == 'high':
                        return ['background-color: #ff7675'] * len(row)
                    elif row.level == 'medium':
                        return ['background-color: #ffeaa7'] * len(row)
                    return [''] * len(row)
                
                # Show table with highlighting
                st.dataframe(display_df.style.apply(highlight_level, axis=1), use_container_width=True)
                
                # Show chart of alert levels
                st.subheader("Alert Level Distribution")
                
                # Count levels
                level_counts = alerts_df['level'].value_counts()
                
                # Create bar chart
                fig, ax = plt.subplots(figsize=(8, 6))
                bars = ax.bar(level_counts.index, level_counts.values)
                
                # Color bars by level
                colors = {'low': 'green', 'medium': 'orange', 'high': 'red'}
                for i, bar in enumerate(bars):
                    bar.set_color(colors[level_counts.index[i]])
                
                plt.tight_layout()
                
                st.pyplot(fig)
            else:
                st.info("No security alerts recorded yet.")

    # Auto refresh every 5 seconds
    time.sleep(1)
    st.experimental_rerun()

if __name__ == "__main__":
    main() 