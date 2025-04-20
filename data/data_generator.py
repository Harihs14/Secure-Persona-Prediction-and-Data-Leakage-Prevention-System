import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import random
import os

def generate_synthetic_data(n_samples=1000, output_file=None):
    """
    Generate synthetic user behavior data for model training.
    
    Parameters:
    -----------
    n_samples : int
        Number of samples to generate
    output_file : str
        Path to save the generated data (optional)
        
    Returns:
    --------
    pd.DataFrame
        DataFrame containing the synthetic data
    """
    # User IDs
    user_ids = [f"user_{i}" for i in range(1, 101)]
    
    # Initialize data dictionary
    data = {
        'timestamp': [],
        'user_id': [],
        'login_hour': [],
        'session_duration_mins': [],
        'files_accessed': [],
        'unique_directories_accessed': [],
        'usb_connected': [],
        'websites_visited': [],
        'email_sent_count': [],
        'after_hours': [],
        'keyboard_intensity': [],
        'persona': []
    }
    
    # Set random seed for reproducibility
    np.random.seed(42)
    
    # Generate timestamps for the past 30 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    # Define persona characteristics
    personas = {
        'Normal': {
            'login_hour': (7, 19),  # 7 AM to 7 PM
            'session_duration': (30, 480),  # 30 mins to 8 hours
            'files_accessed': (1, 50),
            'unique_directories': (1, 10),
            'usb_connected': 0.1,  # 10% chance
            'websites_visited': (5, 50),
            'email_sent': (0, 20),
            'after_hours': 0.05,  # 5% chance
            'keyboard_intensity': (30, 100)
        },
        'Suspicious': {
            'login_hour': (5, 23),  # 5 AM to 11 PM
            'session_duration': (10, 720),  # 10 mins to 12 hours
            'files_accessed': (20, 200),
            'unique_directories': (5, 30),
            'usb_connected': 0.4,  # 40% chance
            'websites_visited': (30, 200),
            'email_sent': (10, 50),
            'after_hours': 0.4,  # 40% chance
            'keyboard_intensity': (10, 150)
        },
        'Malicious': {
            'login_hour': (0, 24),  # Any hour
            'session_duration': (5, 1440),  # 5 mins to 24 hours
            'files_accessed': (100, 500),
            'unique_directories': (20, 100),
            'usb_connected': 0.7,  # 70% chance
            'websites_visited': (100, 1000),
            'email_sent': (30, 200),
            'after_hours': 0.8,  # 80% chance
            'keyboard_intensity': (5, 200)
        }
    }
    
    # Generate data
    for _ in range(n_samples):
        # Choose a user
        user_id = random.choice(user_ids)
        
        # Randomly select persona with biased distribution
        # 70% Normal, 20% Suspicious, 10% Malicious
        persona = np.random.choice(['Normal', 'Suspicious', 'Malicious'], 
                                   p=[0.7, 0.2, 0.1])
        
        # Generate timestamp
        random_days = np.random.randint(0, 30)
        timestamp = start_date + timedelta(days=random_days, 
                                           hours=np.random.randint(0, 24),
                                           minutes=np.random.randint(0, 60))
        
        # Generate feature values based on persona
        login_hour = np.random.randint(*personas[persona]['login_hour'])
        session_duration = np.random.randint(*personas[persona]['session_duration'])
        files_accessed = np.random.randint(*personas[persona]['files_accessed'])
        unique_dirs = np.random.randint(*personas[persona]['unique_directories'])
        usb_connected = 1 if np.random.random() < personas[persona]['usb_connected'] else 0
        websites = np.random.randint(*personas[persona]['websites_visited'])
        emails = np.random.randint(*personas[persona]['email_sent'])
        after_hours = 1 if np.random.random() < personas[persona]['after_hours'] else 0
        keyboard = np.random.randint(*personas[persona]['keyboard_intensity'])
        
        # Add noise to make data more realistic
        if np.random.random() < 0.1:  # 10% chance of anomalous behavior
            files_accessed += np.random.randint(0, 50)
            unique_dirs += np.random.randint(0, 5)
            websites += np.random.randint(0, 20)
        
        # Append to data dictionary
        data['timestamp'].append(timestamp)
        data['user_id'].append(user_id)
        data['login_hour'].append(login_hour)
        data['session_duration_mins'].append(session_duration)
        data['files_accessed'].append(files_accessed)
        data['unique_directories_accessed'].append(unique_dirs)
        data['usb_connected'].append(usb_connected)
        data['websites_visited'].append(websites)
        data['email_sent_count'].append(emails)
        data['after_hours'].append(after_hours)
        data['keyboard_intensity'].append(keyboard)
        data['persona'].append(persona)
    
    # Convert to DataFrame
    df = pd.DataFrame(data)
    
    # Save if output file is specified
    if output_file:
        dir_path = os.path.dirname(output_file)
        if dir_path and not os.path.exists(dir_path):
            os.makedirs(dir_path)
        df.to_csv(output_file, index=False)
    
    return df

if __name__ == "__main__":
    # Generate and save the data
    output_path = "user_behavior_data.csv"
    df = generate_synthetic_data(n_samples=1000, output_file=output_path)
    print(f"Generated {len(df)} samples of synthetic user behavior data.")
    print(f"Persona distribution:\n{df['persona'].value_counts()}")
    print(f"Data saved to {output_path}") 