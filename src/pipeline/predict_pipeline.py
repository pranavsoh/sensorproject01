import os
import sys
import pandas as pd
from flask import Request
from dataclasses import dataclass
from werkzeug.utils import secure_filename
from src.logger import logging
from src.exception import CustomException
from src.constant import *
from src.utils.main_utils import MainUtils

@dataclass
class PredictionPipelineConfig:
    prediction_output_dirname: str = "predictions"
    prediction_file_name: str = "prediction_file.csv"
    model_file_path: str = os.path.join(artifact_folder, 'model.pkl')
    preprocessor_path: str = os.path.join(artifact_folder, 'preprocessor.pkl')
    prediction_file_path: str = os.path.join(prediction_output_dirname, prediction_file_name)

class PredictionPipeline:
    # ✅ Constructor fixed: _init_ → __init__
    def __init__(self, request: Request):
        self.request = request
        self.utils = MainUtils()
        self.prediction_pipeline_config = PredictionPipelineConfig()

    def save_input_file(self) -> str:
        """Save uploaded CSV file and return the path."""
        try:
            input_dir = "prediction_artifacts"
            os.makedirs(input_dir, exist_ok=True)

            input_file = self.request.files.get('file')
            if not input_file or input_file.filename.strip() == "":
                raise CustomException("No file selected. Please choose a CSV file to upload.", sys)

            filename = secure_filename(input_file.filename)
            file_path = os.path.join(input_dir, filename)
            input_file.save(file_path)
            logging.info(f"Input file saved at: {file_path}")

            return file_path
        except Exception as e:
            raise CustomException(f"Failed to save input file: {e}", sys) from e

    def predict(self, features: pd.DataFrame):
        """Transform input features and predict using the trained model."""
        try:
            model = self.utils.load_object(self.prediction_pipeline_config.model_file_path)
            preprocessor = self.utils.load_object(self.prediction_pipeline_config.preprocessor_path)
            transformed_features = preprocessor.transform(features)
            predictions = model.predict(transformed_features)
            return predictions
        except Exception as e:
            raise CustomException(f"Prediction failed: {e}", sys) from e

    def get_predicted_dataframe(self, input_file_path: str):
        """Read CSV, predict, and save results."""
        try:
            df = pd.read_csv(input_file_path)
            if "Unnamed: 0" in df.columns:
                df = df.drop(columns=["Unnamed: 0"])

            predictions = self.predict(df)
            df[TARGET_COLUMN] = [pred for pred in predictions]
            df[TARGET_COLUMN] = df[TARGET_COLUMN].map({0: 'bad', 1: 'good'})

            os.makedirs(self.prediction_pipeline_config.prediction_output_dirname, exist_ok=True)
            df.to_csv(self.prediction_pipeline_config.prediction_file_path, index=False)
            logging.info(f"Predictions saved to {self.prediction_pipeline_config.prediction_file_path}")
            return df
        except Exception as e:
            raise CustomException(f"Failed to generate predicted dataframe: {e}", sys) from e

    def run_pipeline(self):
        """Run the full prediction pipeline and return config with output path."""
        try:
            input_path = self.save_input_file()
            self.get_predicted_dataframe(input_path)
            return self.prediction_pipeline_config
        except Exception as e:
            raise CustomException(f"Prediction pipeline failed: {e}", sys) from e
