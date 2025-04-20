import numpy as np
import pandas as pd
import joblib
import os
import sys
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix

# Add parent directory to path to import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import setup_logger

# Set up logger
logger = setup_logger("persona_model", "logs/model.log")

class PersonaModel:
    """
    Machine learning model to predict user persona based on behavior.
    
    Supports two model types:
    - RandomForest
    - LogisticRegression
    """
    
    def __init__(self, model_type="RandomForest"):
        """
        Initialize the model.
        
        Parameters:
        -----------
        model_type : str
            Type of model to use ('RandomForest' or 'LogisticRegression')
        """
        self.model_type = model_type
        self.model = None
        self.scaler = StandardScaler()
        self.features = [
            'login_hour', 'session_duration_mins', 'files_accessed',
            'unique_directories_accessed', 'usb_connected', 'websites_visited',
            'email_sent_count', 'after_hours', 'keyboard_intensity'
        ]
        logger.info(f"PersonaModel initialized with model type: {model_type}")
    
    def train(self, data, test_size=0.2, random_state=42):
        """
        Train the model on the provided data.
        
        Parameters:
        -----------
        data : pd.DataFrame
            DataFrame containing user behavior data
        test_size : float
            Proportion of data to use for testing
        random_state : int
            Random seed for reproducibility
            
        Returns:
        --------
        dict
            Dictionary with training metrics
        """
        logger.info("Starting model training process")
        
        # Prepare the data
        X = data[self.features]
        y = data['persona']
        
        # Split the data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state, stratify=y
        )
        
        # Scale the features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Initialize the model
        if self.model_type == "RandomForest":
            self.model = RandomForestClassifier(
                n_estimators=100, 
                max_depth=10,
                random_state=random_state
            )
        elif self.model_type == "LogisticRegression":
            self.model = LogisticRegression(
                max_iter=1000,
                C=1.0,
                random_state=random_state
            )
        else:
            logger.error(f"Unknown model type: {self.model_type}")
            raise ValueError(f"Unknown model type: {self.model_type}")
        
        # Train the model
        logger.info(f"Training {self.model_type} model on {len(X_train)} samples")
        self.model.fit(X_train_scaled, y_train)
        
        # Evaluate the model
        y_pred = self.model.predict(X_test_scaled)
        accuracy = accuracy_score(y_test, y_pred)
        report = classification_report(y_test, y_pred, output_dict=True)
        
        # Log results
        logger.info(f"Model training completed with accuracy: {accuracy:.4f}")
        logger.info(f"Classification report:\n{classification_report(y_test, y_pred)}")
        
        # Return metrics
        return {
            "accuracy": accuracy,
            "report": report,
            "num_samples": len(data)
        }
    
    def predict(self, user_behavior):
        """
        Predict the persona of a user based on behavior.
        
        Parameters:
        -----------
        user_behavior : dict or pd.DataFrame
            User behavior data
            
        Returns:
        --------
        str
            Predicted persona
        """
        if self.model is None:
            logger.error("Model not trained. Call train() first.")
            raise RuntimeError("Model not trained. Call train() first.")
        
        # Convert to DataFrame if dict
        if isinstance(user_behavior, dict):
            user_behavior = pd.DataFrame([user_behavior])
        
        # Ensure all features are present
        for feature in self.features:
            if feature not in user_behavior.columns:
                logger.error(f"Missing feature: {feature}")
                raise ValueError(f"Missing feature: {feature}")
        
        # Extract features
        X = user_behavior[self.features]
        
        # Scale features
        X_scaled = self.scaler.transform(X)
        
        # Make prediction
        persona = self.model.predict(X_scaled)[0]
        
        # Get probability
        proba = self.model.predict_proba(X_scaled)[0]
        max_proba = max(proba)
        
        logger.info(f"Predicted persona: {persona} with probability: {max_proba:.4f}")
        
        return persona
    
    def save_model(self, model_path, scaler_path=None):
        """
        Save the trained model and scaler to disk.
        
        Parameters:
        -----------
        model_path : str
            Path to save the model
        scaler_path : str
            Path to save the scaler (optional)
        """
        if self.model is None:
            logger.error("Model not trained. Call train() first.")
            raise RuntimeError("Model not trained. Call train() first.")
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        
        # Save model
        joblib.dump(self.model, model_path)
        logger.info(f"Model saved to {model_path}")
        
        # Save scaler if path provided
        if scaler_path:
            joblib.dump(self.scaler, scaler_path)
            logger.info(f"Scaler saved to {scaler_path}")
    
    def load_model(self, model_path, scaler_path=None):
        """
        Load a trained model and scaler from disk.
        
        Parameters:
        -----------
        model_path : str
            Path to the saved model
        scaler_path : str
            Path to the saved scaler (optional)
        """
        # Load model
        try:
            self.model = joblib.load(model_path)
            logger.info(f"Model loaded from {model_path}")
            
            # Update model type
            if isinstance(self.model, RandomForestClassifier):
                self.model_type = "RandomForest"
            elif isinstance(self.model, LogisticRegression):
                self.model_type = "LogisticRegression"
            
            # Load scaler if path provided
            if scaler_path:
                self.scaler = joblib.load(scaler_path)
                logger.info(f"Scaler loaded from {scaler_path}")
            
            return True
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            return False


if __name__ == "__main__":
    # Example usage
    try:
        # Import data generator
        sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data'))
        from data.data_generator import generate_synthetic_data
        
        # Generate data
        data = generate_synthetic_data(n_samples=1000)
        
        # Initialize and train model
        model = PersonaModel(model_type="RandomForest")
        metrics = model.train(data)
        
        print(f"Model trained with accuracy: {metrics['accuracy']:.4f}")
        
        # Save model
        model_dir = os.path.dirname(os.path.abspath(__file__))
        model.save_model(
            os.path.join(model_dir, "persona_model.joblib"),
            os.path.join(model_dir, "scaler.joblib")
        )
        
        # Make a sample prediction
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
        
    except Exception as e:
        logger.error(f"Error in main execution: {str(e)}")
        print(f"Error: {str(e)}") 