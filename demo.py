from sklearn import pipeline
from sales.pipeline.pipeline import Pipeline
from sales.exception import SalesException
from sales.logger import logging

def main():
    try:
        pipeline = Pipeline()
        #pipeline.run_pipeline()
        pipeline.start()
        logging.info("main function execution completed.")

    except Exception as e:
        logging.error(f"{e}")
        print(e)


if __name__ == "__main__":
    main()