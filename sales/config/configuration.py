from sales.entity.config_entity import DataIngestionConfig, TrainingPipelineConfig, DataValidationConfig, DataTransformationConfig, ModelEvaluationConfig, ModelPusherConfig, ModelTrainerConfig
from sales.util.util import read_yaml
from sales.logger import logging
from sales.exception import SalesException
from sales.constant import *
import os, sys

class Configuration:

    def __init__(self, config_file_path: str= CONFIG_FILE_PATH, 
                current_time_stamp:str= CURRENT_TIME_STAMP)-> None:

        
        self.config_info= read_yaml(file_path=config_file_path)
        self.current_time_stamp= current_time_stamp
        self.training_pipeline_config= self.get_training_pipeline_config()



    def get_data_ingestion_config(self)-> DataIngestionConfig:
        try:
            artifact_dir= self.training_pipeline_config.artifact_dir
            data_ingestion_artifact_dir= os.path.join(artifact_dir, DATA_INGESTION_ARTIFACT_DIR, self.current_time_stamp)

            data_ingestion_info= self.config_info[DATA_INGESTION_CONFIG_KEY]

            train_download_url= data_ingestion_info[TRAIN_DOWNLOAD_URL_KEY]

            test_download_url= data_ingestion_info[TEST_DOWNLOAD_URL_KEY]

            ingested_train_dir= os.path.join(data_ingestion_artifact_dir, data_ingestion_info[INGESTED_TRAIN_DIR_KEY])

            ingested_test_dir= os.path.join(data_ingestion_artifact_dir, data_ingestion_info[INGESTED_TEST_DIR_KEY])

            data_ingestion_config= DataIngestionConfig(train_download_url=train_download_url,
            test_download_url=test_download_url,
            ingested_train_dir= ingested_train_dir,
            ingested_test_dir= ingested_test_dir)

            logging.info(f"Data Ingestion Config: {data_ingestion_config}")

            return data_ingestion_config

        except Exception as e:
            raise SalesException(e,sys) from e


    def get_data_validation_config (self)-> DataValidationConfig:
        try:
            artifact_dir= self.training_pipeline_config.artifact_dir

            data_validation_artifact_dir= os.path.join(artifact_dir, DATA_VALIDATION_ARTIFACT_DIR, self.current_time_stamp)

            data_validation_info= self.config_info[DATA_VALIDATION_CONFIG_KEY]

            schema_file_path= os.path.join(ROOT_DIR, 
                                          data_validation_info[DATA_VALIDATION_SCHEMA_DIR_KEY],
                                          data_validation_info[DATA_VALIDATION_SCHEMA_FILE_NAME_KEY]
                                          )

            report_file_path= os.path.join(data_validation_artifact_dir, 
                                           data_validation_info[DATA_VALIDATION_REPORT_FILE_NAME_KEY],
                                           )

            report_page_file_name= os.path.join(data_validation_artifact_dir,
                                                data_validation_info[DATA_VALIDATION_REPORT_PAGE_FILE_NAME_KEY]
                                                )

            data_validation_config= DataValidationConfig(schema_file_path= schema_file_path,
                                                        report_file_path= report_file_path,
                                                        report_page_file_path= report_page_file_name
                                                        )

            logging.info(f"Data Validation Config: {data_validation_config}")

            return data_validation_config

        except Exception as e:
            raise SalesException(e,sys) from e

    def get_data_transformation_config(self)-> DataTransformationConfig:
        pass

    def get_model_trainer_config(self)-> ModelTrainerConfig:
        pass

    def get_model_evaluation_config(self)-> ModelEvaluationConfig:
        pass

    def get_model_pusher_config(self)-> ModelPusherConfig:
        pass

    def get_training_pipeline_config(self)-> TrainingPipelineConfig:
        try:
            training_pipeline_config= self.config_info[TRAINING_PIPELINE_CONFIG_KEY]

            artifact_dir= os.path.join(ROOT_DIR, 
            training_pipeline_config[TRAINING_PIPELINE_NAME_KEY], 
            training_pipeline_config[TRAINING_PIPELINE_ARTIFACT_DIR_KEY])

            training_pipeline_config= TrainingPipelineConfig(artifact_dir= artifact_dir)
            logging.info(f"Training Pipeline Config: {training_pipeline_config}")

            return training_pipeline_config

        except Exception as e:
            raise SalesException(e,sys) from e










        
        
