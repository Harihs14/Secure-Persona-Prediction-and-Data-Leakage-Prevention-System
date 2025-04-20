#!/usr/bin/env python
"""
Test script for Secure Persona Prediction and Data Leakage Prevention System

This script tests the basic functionality of all system components.
"""

import os
import sys
import time
import pandas as pd

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import project modules
from model.persona_model import PersonaModel
from monitoring.file_monitor import FileMonitor
from data.data_generator import generate_synthetic_data
from utils import setup_logger

# Set up logger
logger = setup_logger("test", "logs/test.log")

def test_data_generator():
    """Test the data generation module."""
    print("Testing data generator...")
    
    try:
        # Generate data
        output_path = os.path.join("data", "test_user_behavior.csv")
        df = generate_synthetic_data(n_samples=100, output_file=output_path)
        
        # Check data
        print(f"Generated {len(df)} samples")
        print(f"Columns: {df.columns.tolist()}")
        print(f"Persona distribution: {df['persona'].value_counts().to_dict()}")
        
        # Check if file was created
        if os.path.exists(output_path):
            print(f"Data file created at: {output_path}")
            
        print("Data generator test completed successfully.\n")
        return True
        
    except Exception as e:
        print(f"Error testing data generator: {str(e)}")
        return False

def test_model():
    """Test the persona prediction model."""
    print("Testing persona prediction model...")
    
    try:
        # Generate synthetic data
        df = generate_synthetic_data(n_samples=200)
        
        # Train model
        model = PersonaModel(model_type="RandomForest")
        metrics = model.train(df)
        
        # Check metrics
        print(f"Model trained with {metrics['num_samples']} samples")
        print(f"Accuracy: {metrics['accuracy']:.4f}")
        
        # Test prediction
        sample = {
            'login_hour': 3,
            'session_duration_mins': 600,
            'files_accessed': 250,
            'unique_directories_accessed': 50,
            'usb_connected': 1,
            'websites_visited': 300,
            'email_sent_count': 45,
            'after_hours': 1,
            'keyboard_intensity': 20
        }
        
        # Convert to DataFrame
        sample_df = pd.DataFrame([sample])
        
        # Predict
        persona = model.predict(sample_df)
        print(f"Predicted persona for sample: {persona}")
        
        # Save and load model
        model_path = os.path.join("model", "test_model.joblib")
        scaler_path = os.path.join("model", "test_scaler.joblib")
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        
        # Save model
        model.save_model(model_path, scaler_path)
        print(f"Model saved to {model_path}")
        
        # Load model
        new_model = PersonaModel()
        success = new_model.load_model(model_path, scaler_path)
        
        if success:
            print("Model loaded successfully")
            
            # Test prediction with loaded model
            new_persona = new_model.predict(sample_df)
            print(f"Predicted persona with loaded model: {new_persona}")
            
            # Check if predictions match
            if persona == new_persona:
                print("Predictions match between original and loaded model")
            else:
                print("Warning: Predictions do not match")
        
        # Clean up
        if os.path.exists(model_path):
            os.remove(model_path)
        if os.path.exists(scaler_path):
            os.remove(scaler_path)
        
        print("Model test completed successfully.\n")
        return True
        
    except Exception as e:
        print(f"Error testing model: {str(e)}")
        return False

def test_file_monitor():
    """Test the file monitoring module."""
    print("Testing file monitor...")
    
    try:
        # Create test directory
        test_dir = os.path.join("data", "test_monitoring")
        os.makedirs(test_dir, exist_ok=True)
        
        # Initialize file monitor
        monitor = FileMonitor(paths_to_monitor=[test_dir])
        
        # Start monitoring
        monitor.start_monitoring()
        print("File monitoring started")
        
        # Create test file with sensitive data
        test_file = os.path.join(test_dir, "test_sensitive.txt")
        with open(test_file, "w") as f:
            f.write("This is a test file with sensitive data.\n")
            f.write("My password is 123456\n")
            f.write("This is confidential information\n")
            f.write("Bank account: 1234567890\n")
        print(f"Created test file with sensitive data: {test_file}")
        
        # Wait for file system events to be processed
        time.sleep(2)
        
        # Check file for sensitive data
        has_sensitive, matches = monitor.check_file_for_sensitive_data(test_file)
        
        if has_sensitive:
            print(f"Detected {len(matches)} sensitive keywords in test file:")
            for match in matches:
                print(f"  Keyword: {match['keyword']} at line {match['line']}")
        else:
            print("No sensitive data detected in test file")
        
        # Stop monitoring
        monitor.stop_monitoring()
        print("File monitoring stopped")
        
        # Clean up
        if os.path.exists(test_file):
            os.remove(test_file)
        
        # Clean up test directory
        if os.path.exists(test_dir):
            os.rmdir(test_dir)
        
        print("File monitor test completed successfully.\n")
        return True
        
    except Exception as e:
        print(f"Error testing file monitor: {str(e)}")
        return False

def run_all_tests():
    """Run all tests."""
    print("=" * 80)
    print("TESTING SECURE PERSONA PREDICTION AND DATA LEAKAGE PREVENTION SYSTEM")
    print("=" * 80 + "\n")
    
    # Run tests
    tests = [
        ("Data Generator", test_data_generator),
        ("Persona Model", test_model),
        ("File Monitor", test_file_monitor)
    ]
    
    results = {}
    
    for name, test_func in tests:
        print("=" * 40)
        print(f"Testing: {name}")
        print("=" * 40)
        
        try:
            result = test_func()
            results[name] = result
        except Exception as e:
            print(f"Unhandled exception: {str(e)}")
            results[name] = False
    
    # Print summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    all_passed = True
    for name, result in results.items():
        status = "PASSED" if result else "FAILED"
        print(f"{name}: {status}")
        all_passed = all_passed and result
    
    print("\nOverall status:", "PASSED" if all_passed else "FAILED")
    print("=" * 80)
    
    return all_passed

if __name__ == "__main__":
    run_all_tests() 