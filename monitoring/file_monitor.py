import sys
import os
import time
from datetime import datetime
import threading
import re
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import random

# Add parent directory to path to import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import setup_logger, log_activity, log_alert

# Set up logger
logger = setup_logger("file_monitor", "logs/file_monitor.log")

class FileMonitor:
    """
    Monitor file system activities and detect potential data leakage.
    """
    
    def __init__(self, paths_to_monitor=None, sensitive_keywords=None):
        """
        Initialize the file monitor.
        
        Parameters:
        -----------
        paths_to_monitor : list
            List of paths to monitor
        sensitive_keywords : list
            List of sensitive keywords to detect in files
        """
        # Default paths to monitor
        self.paths_to_monitor = paths_to_monitor or [os.getcwd()]
        
        # Default sensitive keywords
        self.sensitive_keywords = sensitive_keywords or [
            "password", "confidential", "secret", "private", "bank", "credit card",
            "ssn", "social security", "account", "classified", "restricted"
        ]
        
        # Compile regex for sensitive keywords
        self.keywords_pattern = re.compile(
            r'(' + '|'.join(re.escape(kw) for kw in self.sensitive_keywords) + r')', 
            re.IGNORECASE
        )
        
        # Event handler for file system events
        self.event_handler = FileEventHandler(self)
        
        # Observer for monitoring file system
        self.observer = Observer()
        
        # Flags for monitoring status
        self.is_running = False
        
        # USB detection simulation thread
        self.usb_thread = None
        self.usb_detected = False
        
        logger.info("FileMonitor initialized")
        logger.info(f"Paths to monitor: {self.paths_to_monitor}")
        logger.info(f"Sensitive keywords: {self.sensitive_keywords}")
    
    def start_monitoring(self):
        """
        Start monitoring the file system.
        """
        if self.is_running:
            logger.warning("File monitoring already running")
            return
        
        logger.info("Starting file monitoring")
        
        try:
            # Set up observer for each path
            for path in self.paths_to_monitor:
                if os.path.exists(path):
                    self.observer.schedule(self.event_handler, path, recursive=True)
                    logger.info(f"Monitoring path: {path}")
                else:
                    logger.warning(f"Path does not exist: {path}")
            
            # Start observer
            self.observer.start()
            self.is_running = True
            
            # Start USB detection simulation
            self.usb_thread = threading.Thread(target=self._simulate_usb_detection)
            self.usb_thread.daemon = True
            self.usb_thread.start()
            
            logger.info("File monitoring started successfully")
            
        except Exception as e:
            logger.error(f"Error starting file monitoring: {str(e)}")
            raise
    
    def stop_monitoring(self):
        """
        Stop monitoring the file system.
        """
        if not self.is_running:
            logger.warning("File monitoring not running")
            return
        
        logger.info("Stopping file monitoring")
        
        try:
            self.observer.stop()
            self.observer.join()
            self.is_running = False
            
            logger.info("File monitoring stopped successfully")
            
        except Exception as e:
            logger.error(f"Error stopping file monitoring: {str(e)}")
            raise
    
    def check_file_for_sensitive_data(self, file_path):
        """
        Check if a file contains sensitive data.
        
        Parameters:
        -----------
        file_path : str
            Path to the file to check
            
        Returns:
        --------
        tuple
            (bool, list) - Whether sensitive data was found and the matched keywords
        """
        if not os.path.exists(file_path):
            logger.warning(f"File does not exist: {file_path}")
            return False, []
        
        # Check if it's a text file
        if not self._is_text_file(file_path):
            return False, []
        
        try:
            matches = []
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line_num, line in enumerate(f, 1):
                    for match in self.keywords_pattern.finditer(line):
                        keyword = match.group(0)
                        matches.append({
                            'keyword': keyword,
                            'line': line_num,
                            'context': line.strip()
                        })
            
            if matches:
                logger.warning(f"Sensitive data found in file: {file_path}")
                for match in matches:
                    logger.warning(f"  Keyword: {match['keyword']} at line {match['line']}")
                return True, matches
            
            return False, []
            
        except Exception as e:
            logger.error(f"Error checking file for sensitive data: {str(e)}")
            return False, []
    
    def _is_text_file(self, file_path):
        """
        Check if a file is a text file.
        
        Parameters:
        -----------
        file_path : str
            Path to the file to check
            
        Returns:
        --------
        bool
            Whether the file is a text file
        """
        text_extensions = ['.txt', '.py', '.js', '.html', '.csv', '.json', '.xml', '.md', '.log', '.ini', '.cfg', '.conf']
        _, ext = os.path.splitext(file_path)
        return ext.lower() in text_extensions
    
    def _simulate_usb_detection(self):
        """
        Simulate USB device detection.
        """
        while self.is_running:
            # Simulate USB detection with 5% probability every 30 seconds
            time.sleep(30)
            if random.random() < 0.05:
                self.usb_detected = True
                usb_name = f"USB{random.randint(1, 10)}"
                logger.warning(f"USB device detected: {usb_name}")
                log_alert(logger, "medium", f"USB device detected: {usb_name}")
                time.sleep(10)  # Device connected for 10 seconds
                logger.info(f"USB device removed: {usb_name}")
                self.usb_detected = False
    
    def handle_file_access(self, file_path, access_type):
        """
        Handle a file access event.
        
        Parameters:
        -----------
        file_path : str
            Path to the file being accessed
        access_type : str
            Type of access (read, write, etc.)
        """
        logger.info(f"File {access_type}: {file_path}")
        log_activity(logger, access_type, file_path)
        
        # Check for sensitive data if file was modified or created
        if access_type in ["created", "modified"]:
            has_sensitive, matches = self.check_file_for_sensitive_data(file_path)
            if has_sensitive:
                alert_level = "high" if self.usb_detected else "medium"
                alert_msg = f"Sensitive data found in file: {file_path}"
                log_alert(logger, alert_level, alert_msg)
                
                # Simulate blocking action if sensitive data found with USB connected
                if self.usb_detected:
                    logger.error(f"ALERT: Potential data exfiltration detected! File with sensitive data accessed while USB connected.")
                    return {
                        "action": "block",
                        "reason": "Potential data exfiltration detected",
                        "alert_level": "high"
                    }
        
        # Simulate detecting email exfiltration attempt
        if ".eml" in file_path.lower() or "email" in file_path.lower():
            has_sensitive, _ = self.check_file_for_sensitive_data(file_path)
            if has_sensitive:
                alert_msg = f"Potential email data leak detected: {file_path}"
                log_alert(logger, "high", alert_msg)
                logger.error(f"ALERT: {alert_msg}")
                return {
                    "action": "block",
                    "reason": "Potential email data leak detected",
                    "alert_level": "high"
                }
        
        return {
            "action": "allow",
            "reason": "No threat detected",
            "alert_level": "low"
        }


class FileEventHandler(FileSystemEventHandler):
    """
    Handler for file system events.
    """
    
    def __init__(self, file_monitor):
        """
        Initialize the event handler.
        
        Parameters:
        -----------
        file_monitor : FileMonitor
            Reference to the file monitor
        """
        self.file_monitor = file_monitor
    
    def on_created(self, event):
        """Handle file creation events."""
        if not event.is_directory:
            self.file_monitor.handle_file_access(event.src_path, "created")
    
    def on_modified(self, event):
        """Handle file modification events."""
        if not event.is_directory:
            self.file_monitor.handle_file_access(event.src_path, "modified")
    
    def on_moved(self, event):
        """Handle file move events."""
        if not event.is_directory:
            self.file_monitor.handle_file_access(event.src_path, "moved from")
            self.file_monitor.handle_file_access(event.dest_path, "moved to")
    
    def on_deleted(self, event):
        """Handle file deletion events."""
        if not event.is_directory:
            self.file_monitor.handle_file_access(event.src_path, "deleted")


# Example usage
if __name__ == "__main__":
    try:
        # Create a sample text file with sensitive data
        with open("test_sensitive.txt", "w") as f:
            f.write("This is a test file with sensitive data.\n")
            f.write("My password is 123456\n")
            f.write("This is confidential information\n")
            f.write("Bank account: 1234567890\n")
        
        # Initialize file monitor
        monitor = FileMonitor()
        
        # Start monitoring
        monitor.start_monitoring()
        
        print("File monitoring started. Press Ctrl+C to stop.")
        
        # Check the sample file
        has_sensitive, matches = monitor.check_file_for_sensitive_data("test_sensitive.txt")
        if has_sensitive:
            print(f"Found {len(matches)} sensitive data matches in test file:")
            for match in matches:
                print(f"  Keyword: {match['keyword']} at line {match['line']}")
        
        # Keep running until Ctrl+C
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
        
        # Stop monitoring
        monitor.stop_monitoring()
        
        print("File monitoring stopped.")
        
    except Exception as e:
        logger.error(f"Error in main execution: {str(e)}")
        print(f"Error: {str(e)}") 