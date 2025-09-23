import sys
import os
import pandas as pd
import numpy as np
from pymongo import MongoClient
from pathlib import Path
from src.constant import *
from src.exception import CustomException
from src.logger import logging
from src.utils.main_utils import MainUtils
from dataclasses import dataclass

# Configuration dataclass
@dataclass
class DataIngestionConfig:
    artifact_folder: str = os.path.join("artifacts", "data_ingestion")  # folder to save ingested data

# Main DataIngestion class
class DataIngestion:
    def _init_(self):
        # Initialize config and utils
        self.data_ingestion_config = DataIngestionConfig()
        self.utils = MainUtils()
    
    def export_collection_as_dataframe(self, collection_name, db_name) -> pd.DataFrame:
        """
        Export MongoDB collection to a pandas DataFrame
        """
        try:
            mongo_client = MongoClient(MONGO_DB_URL)
            collection = mongo_client[db_name][collection_name]
            df = pd.DataFrame(list(collection.find()))
            
            # Drop _id column if exists
            if "_id" in df.columns.to_list():
                df = df.drop(columns=['_id'], axis=1)
            
            df.replace({"na": np.nan}, inplace=True)
            return df
        except Exception as e:
            raise CustomException(str(e), sys)
    
    def export_data_into_feature_store_file_path(self) -> str:
        """
        Export data from MongoDB into a CSV in artifact folder
        """
        try:
            logging.info("Exporting data from MongoDB")
            
            raw_file_path = self.data_ingestion_config.artifact_folder
            os.makedirs(raw_file_path, exist_ok=True)
            
            # Export collection as DataFrame
            sensor_data = self.export_collection_as_dataframe(
                collection_name=MONGO_COLLECTION_NAME,
                db_name=MONGO_DATABASE_NAME
            )
            
            feature_store_file_path = os.path.join(raw_file_path, 'wafer_fault.csv')
            sensor_data.to_csv(feature_store_file_path, index=False)
            
            logging.info(f"Saved exported data into feature store file path: {feature_store_file_path}")
            return feature_store_file_path
        except Exception as e:
            raise CustomException(str(e), sys)
    
    def initiate_data_ingestion(self) -> str:
        """
        Main method to initiate data ingestion
        """
        logging.info("Entered initiate_data_ingestion method of DataIngestion class")
        try:
            feature_store_file_path = self.export_data_into_feature_store_file_path()
            logging.info("Got the data from MongoDB")
            logging.info("Exited initiate_data_ingestion method of DataIngestion class")
            return feature_store_file_path
        except Exception as e:
            raise CustomException(str(e), sys)

