import os
from datetime import datetime

def get_current_time_stamp():
    return f"{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}"

    
ROOT_DIR = os.getcwd()  #to get current working directory
CONFIG_DIR = "config"
CONFIG_FILE_NAME = "config.yaml"
CONFIG_FILE_PATH = os.path.join(ROOT_DIR,CONFIG_DIR,CONFIG_FILE_NAME)


CURRENT_TIME_STAMP = get_current_time_stamp()

#data ingestion config related variables
DATA_INGESTION_CONFIG_KEY= "data_ingestion_config"
DATA_INGESTION_ARTIFACT_DIR= "data_ingestion"
TRAIN_DOWNLOAD_URL_KEY= "train_download_url"
TEST_DOWNLOAD_URL_KEY= "test_download_url"
INGESTED_TRAIN_DIR_KEY= "ingested_train_dir"
INGESTED_TEST_DIR_KEY= "ingested_test_dir"


# Training pipeline related variable
TRAINING_PIPELINE_CONFIG_KEY = "training_pipeline_config"
TRAINING_PIPELINE_ARTIFACT_DIR_KEY = "artifact_dir"
TRAINING_PIPELINE_NAME_KEY = "pipeline_name"
