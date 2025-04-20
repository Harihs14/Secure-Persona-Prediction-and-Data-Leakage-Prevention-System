import os
import sys
import argparse
import time
import threading
import signal
import logging
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import project modules
from model.persona_model import PersonaModel
from monitoring.file_monitor import FileMonitor
from data.data_generator import generate_synthetic_data
from utils import setup_logger

# Set up logger
logger = setup_logger("main", "logs/main.log")

def train_model(model_type="RandomForest", save_path=None):
    """
    Train and save the persona prediction model.
    
    Parameters:
    -----------
    model_type : str
        Type of model to train ('RandomForest' or 'LogisticRegression')
    save_path : str
        Path to save the model
    """
    logger.info(f"Training {model_type} model...")
    
    try:
        # Generate synthetic data
        data_path = os.path.join("data", "user_behavior_data.csv")
        data = generate_synthetic_data(n_samples=1000, output_file=data_path)
        logger.info(f"Generated synthetic data with {len(data)} samples")
        
        # Initialize and train model
        model = PersonaModel(model_type=model_type)
        metrics = model.train(data)
        
        logger.info(f"Model trained with accuracy: {metrics['accuracy']:.4f}")
        
        # Save model
        if not save_path:
            save_path = os.path.join("model", "persona_model.joblib")
        
        scaler_path = os.path.join(os.path.dirname(save_path), "scaler.joblib")
        model.save_model(save_path, scaler_path)
        
        logger.info(f"Model saved to {save_path}")
        logger.info(f"Scaler saved to {scaler_path}")
        
        return model
        
    except Exception as e:
        logger.error(f"Error training model: {str(e)}")
        raise

def start_file_monitoring(paths=None):
    """
    Start file monitoring system.
    
    Parameters:
    -----------
    paths : list
        List of paths to monitor
    
    Returns:
    --------
    FileMonitor
        Initialized file monitor
    """
    logger.info("Starting file monitoring...")
    
    try:
        # Initialize file monitor
        monitor = FileMonitor(paths_to_monitor=paths)
        
        # Start monitoring
        monitor.start_monitoring()
        
        logger.info("File monitoring started successfully")
        
        return monitor
        
    except Exception as e:
        logger.error(f"Error starting file monitoring: {str(e)}")
        raise

def launch_dashboard():
    """Launch the Streamlit dashboard."""
    logger.info("Launching dashboard...")
    
    try:
        # Use subprocess to avoid blocking the main thread
        import subprocess
        
        # Command to run the dashboard
        cmd = ["streamlit", "run", os.path.join("gui", "dashboard.py")]
        
        # Start the process
        process = subprocess.Popen(cmd)
        
        logger.info("Dashboard launched successfully")
        
        return process
        
    except Exception as e:
        logger.error(f"Error launching dashboard: {str(e)}")
        raise

def handle_shutdown(monitor, dashboard_process):
    """Handle application shutdown."""
    logger.info("Shutting down application...")
    
    try:
        # Stop file monitoring
        if monitor and monitor.is_running:
            monitor.stop_monitoring()
            logger.info("File monitoring stopped")
        
        # Stop dashboard
        if dashboard_process:
            dashboard_process.terminate()
            dashboard_process.wait()
            logger.info("Dashboard stopped")
        
        logger.info("Application shutdown complete")
        
    except Exception as e:
        logger.error(f"Error during shutdown: {str(e)}")

def signal_handler(sig, frame, monitor=None, dashboard_process=None):
    """Signal handler for graceful shutdown."""
    logger.info(f"Received signal {sig}")
    handle_shutdown(monitor, dashboard_process)
    sys.exit(0)

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Secure Persona Prediction and Data Leakage Prevention System")
    
    parser.add_argument("--train", action="store_true", help="Train the model before starting")
    parser.add_argument("--model-type", type=str, default="RandomForest", 
                        choices=["RandomForest", "LogisticRegression"],
                        help="Type of model to train")
    parser.add_argument("--monitor-path", type=str, action="append", 
                        help="Path to monitor (can be specified multiple times)")
    parser.add_argument("--no-dashboard", action="store_true", 
                        help="Do not launch the dashboard")
    
    return parser.parse_args()

def main():
    """Main application entry point."""
    # Parse arguments
    args = parse_arguments()
    
    logger.info("Starting Secure Persona Prediction and Data Leakage Prevention System")
    
    # Initialize variables
    model = None
    monitor = None
    dashboard_process = None
    
    try:
        # Train model if requested
        if args.train:
            model = train_model(model_type=args.model_type)
        else:
            # Try to load existing model
            model_path = os.path.join("model", "persona_model.joblib")
            scaler_path = os.path.join("model", "scaler.joblib")
            
            if os.path.exists(model_path) and os.path.exists(scaler_path):
                model = PersonaModel()
                if model.load_model(model_path, scaler_path):
                    logger.info(f"Model loaded from {model_path}")
                else:
                    logger.warning("Failed to load model. Training a new one...")
                    model = train_model(model_type=args.model_type)
            else:
                logger.info("No existing model found. Training a new one...")
                model = train_model(model_type=args.model_type)
        
        # Start file monitoring
        monitor = start_file_monitoring(paths=args.monitor_path)
        
        # Set up signal handlers
        signal.signal(signal.SIGINT, lambda sig, frame: signal_handler(sig, frame, monitor, dashboard_process))
        signal.signal(signal.SIGTERM, lambda sig, frame: signal_handler(sig, frame, monitor, dashboard_process))
        
        # Launch dashboard unless disabled
        if not args.no_dashboard:
            dashboard_process = launch_dashboard()
            
            # Wait for dashboard to initialize
            time.sleep(2)
            
            # Print information for user
            print("\n" + "="*80)
            print("Secure Persona Prediction and Data Leakage Prevention System is running")
            print("="*80)
            print("\nDashboard is available at: http://localhost:8501")
            print("\nPress Ctrl+C to stop\n")
        
        # Keep running until interrupted
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        # Handle keyboard interrupt (Ctrl+C)
        logger.info("Received keyboard interrupt")
        handle_shutdown(monitor, dashboard_process)
        
    except Exception as e:
        logger.error(f"Unhandled exception: {str(e)}")
        handle_shutdown(monitor, dashboard_process)
        raise
        
    finally:
        logger.info("Application exited")

if __name__ == "__main__":
    main() 