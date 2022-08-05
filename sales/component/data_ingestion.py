from sales.logger import logging
from sales.exception import SalesException
from sales.entity.config_entity import DataIngestionConfig
from sales.entity.artifact_entity import DataIngestionArtifact
import sys, os
import urllib.request


class DataIngestion:

    def __init__(self, data_ingestion_config: DataIngestionConfig):
        try:
            logging.info(f"{'='*20}Data Ingestion log started.{'='*20} ")
            self.data_ingestion_config = data_ingestion_config

        except Exception as e:
            raise SalesException(e,sys) from e

    def initiate_data_ingestion(self)-> DataIngestionArtifact:

        try:

            #Downloading train file
            
            ingestion_train_dir= self.data_ingestion_config.ingested_train_dir
            train_download_url= self.data_ingestion_config.train_download_url


            if os.path.exists(ingestion_train_dir):
                os.remove(ingestion_train_dir)

            os.makedirs(ingestion_train_dir, exist_ok= True)

            train_file_name= os.path.basename(train_download_url)
            train_file_path= os.path.join(ingestion_train_dir, train_file_name)

            logging.info(f"Downloading training data from [{train_download_url}] into [{train_file_path}]")

            urllib.request.urlretrieve(train_download_url, train_file_path)
            logging.info(f"Train File {train_file_path} has been downloaded successfully")

            #downloading test file

            test_download_url= self.data_ingestion_config.test_download_url
            ingestion_test_dir= self.data_ingestion_config.ingested_test_dir
            test_download_url= self.data_ingestion_config.test_download_url


            if os.path.exists(ingestion_test_dir):
                os.remove(ingestion_test_dir)

            os.makedirs(ingestion_test_dir, exist_ok= True)

            test_file_name= os.path.basename(test_download_url)
            test_file_path= os.path.join(ingestion_test_dir, test_file_name)

            logging.info(f"Downloading testing data from [{test_download_url}] into [{test_file_path}]")

            urllib.request.urlretrieve(test_download_url, test_file_path)
            logging.info(f"Test File {test_file_path} has been downloaded successfully")

            data_ingestion_artifact= DataIngestionArtifact(train_file_path= train_file_path, 
            test_file_path= test_file_path,
            is_ingested= True,
            message= "Data Ingestion completed successfully")

            return data_ingestion_artifact


        except Exception as e:
            raise SalesException(e,sys) from e


    def __del__(self):
        logging.info(f"{'='*20}Data Ingestion log completed.{'='*20} \n\n")
    






            







        




        
        

