from sklearn import preprocessing
from sales.exception import SalesException
from sales.logger import logging
from sales.entity.config_entity import DataTransformationConfig
from sales.entity.artifact_entity import DataIngestionArtifact, DataValidationArtifact, DataTransformationArtifact
import sys, os
import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
import pandas as pd
from sales.constant import *
from sales.util.util import load_data, read_yaml, save_numpy_array_data, save_object


class FeatureGenerator(BaseEstimator, TransformerMixin):


    def __init__(self,  Outlet_Establishment_Year_id= 3):
        self.Outlet_Establishment_Year_id= Outlet_Establishment_Year_id
        
    def fit(self, X, y= None):
        return self
    
    def transform(self, X, y= None):
       try:
            X[:,self.Outlet_Establishment_Year_id]= 2022- X[:,self.Outlet_Establishment_Year_id]
                
            return X
       except Exception as e:
        raise SalesException(e,sys) from e 

class DataTransformation:

    def __init__(self, data_transformation_config: DataTransformationConfig,
                 data_ingestion_artifact: DataIngestionArtifact,
                 data_validation_artifact: DataValidationArtifact
                 ):
        try:
            logging.info(f"{'>>' * 30}Data Transformation log started.{'<<' * 30} ")
            self.data_transformation_config= data_transformation_config
            self.data_ingestion_artifact = data_ingestion_artifact
            self.data_validation_artifact = data_validation_artifact

        except Exception as e:
            raise SalesException(e,sys) from e


    def get_data_transformer_object(self)-> ColumnTransformer:
        try:
            schema_file_path= self.data_validation_artifact.schema_file_path

            dataset_schema= read_yaml(file_path= schema_file_path)
            
            numerical_columns = dataset_schema[NUMERICAL_COLUMN_KEY]
            categorical_columns = dataset_schema[CATEGORICAL_COLUMN_KEY]


            num_pipeline = Pipeline(steps=[
                ('imputer', SimpleImputer(strategy="median")),
                 ('feature_generator', FeatureGenerator()),
                ('scaler', StandardScaler())
            ]
            )


            cat_pipeline = Pipeline(steps=[
                 ('impute', SimpleImputer(strategy="most_frequent")),
                 ('one_hot_encoder', OneHotEncoder()),
                 ('scaler', StandardScaler(with_mean=False))
            ]
            )

            logging.info(f"Categorical columns: {categorical_columns}")
            logging.info(f"Numerical columns: {numerical_columns}")


            preprocessing = ColumnTransformer([
                ('num_pipeline', num_pipeline, numerical_columns),
                ('cat_pipeline', cat_pipeline, categorical_columns),
            ])
            return preprocessing

        except Exception as e:
            raise SalesException(e,sys) from e 

    def reduce_cardinality(self, file_path):
        try:
            df= pd.read_csv(file_path)
            df["Item_Fat_Content"] = df["Item_Fat_Content"].map(
                {"Low Fat": 'Low Fat', "LF": "Low Fat", 'low fat': "Low Fat", "Regular": "Regular"})

            #df['Outlet_Establishment_Year']= df['Outlet_Establishment_Year'].apply(lambda x: 2022 - x)

            df["Item_Identifier"] = df["Item_Identifier"].apply(lambda x: x[0:2]).map(
                {"FD": "Food", "DR": "Drink", "NC": "Non_consumable"})
            
            return df
        except Exception as e:
            raise SalesException(e, sys) from e           


    def initiate_data_transformation(self)->DataTransformationArtifact:
        try:
            logging.info(f"Obtaining preprocessing object.")
            preprocessing_obj = self.get_data_transformer_object()


            logging.info(f"Obtaining training and test file path.")
            train_file_path = self.data_ingestion_artifact.train_file_path
            test_file_path = self.data_ingestion_artifact.test_file_path
            

            schema_file_path = self.data_validation_artifact.schema_file_path
            
            logging.info(f"Loading training and test data as pandas dataframe after reducing cardinality.")
            train_df = load_data(file_path=train_file_path, schema_file_path=schema_file_path)
            train_df= self.reduce_cardinality(file_path= train_file_path)

            
            test_df = load_data(file_path=test_file_path, schema_file_path=schema_file_path)
            test_df= self.reduce_cardinality(file_path= test_file_path)
            logging.info(f"Size of train and test df are {train_df.shape} & {test_df.shape}")

            schema = read_yaml(file_path=schema_file_path)

            target_column_name = schema[TARGET_COLUMN_KEY]


            logging.info(f"Splitting input and target feature from training and testing dataframe.")
            input_feature_train_df = train_df.drop(columns=[target_column_name],axis=1)
            target_feature_train_df = train_df[target_column_name]

            input_feature_test_df = test_df.drop(columns=[target_column_name],axis=1)
            target_feature_test_df = test_df[target_column_name]
            logging.info(f"Size of input feature train and input feature test df are {input_feature_train_df.shape} & {input_feature_test_df.shape}")

            logging.info(f"Applying preprocessing object on training dataframe and testing dataframe")
            input_feature_train_arr=preprocessing_obj.fit_transform(input_feature_train_df)
            input_feature_test_arr = preprocessing_obj.transform(input_feature_test_df)


            #logging.info(f"Size of input feature train array and input feature test array df are {input_feature_train_arr.shape} & {input_feature_test_arr.shape}")
            #logging.info(f"size of target feature train array is {np.array(target_feature_train_df).shape}")
            train_arr = np.c_[ input_feature_train_arr.toarray(), np.array(target_feature_train_df)]

            test_arr = np.c_[input_feature_test_arr.toarray(), np.array(target_feature_test_df)]
            
            transformed_train_dir = self.data_transformation_config.transformed_train_dir
            transformed_test_dir = self.data_transformation_config.transformed_test_dir

            train_file_name = os.path.basename(train_file_path).replace(".csv",".npz")
            test_file_name = os.path.basename(test_file_path).replace(".csv",".npz")

            transformed_train_file_path = os.path.join(transformed_train_dir, train_file_name)
            transformed_test_file_path = os.path.join(transformed_test_dir, test_file_name)

            logging.info(f"Saving transformed training and testing array.")
            
            save_numpy_array_data(file_path=transformed_train_file_path,array=train_arr)
            save_numpy_array_data(file_path=transformed_test_file_path,array=test_arr)

            preprocessing_obj_file_path = self.data_transformation_config.preprocessed_object_file_path

            logging.info(f"Saving preprocessing object.")
            save_object(file_path=preprocessing_obj_file_path,obj=preprocessing_obj)

            data_transformation_artifact = DataTransformationArtifact(is_transformed=True,
            message="Data transformation successful.",
            transformed_train_file_path=transformed_train_file_path,
            transformed_test_file_path=transformed_test_file_path,
            preprocessed_object_file_path=preprocessing_obj_file_path

            )
            logging.info(f"Data transformation artifact: {data_transformation_artifact}")
            return data_transformation_artifact
        except Exception as e:
            raise SalesException(e,sys) from e

    def __del__(self):
        logging.info(f"{'>>'*30}Data Transformation log completed.{'<<'*30} \n\n")

