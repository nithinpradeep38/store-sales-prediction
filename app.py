
from flask import Flask,request
from sales.util.util import read_yaml,write_yaml_file
import json

from matplotlib.style import context
from sales.logger import logging
from sales.exception import SalesException
import os,sys
from sales.config.configuration import Configuration
from sales.constant import get_current_time_stamp
from sales.logger import get_log_dataframe
from sales.pipeline.pipeline import Pipeline
from sales.entity.sales_predictor import Salespredictor,SalesData
from sales.constant import CONFIG_DIR, get_current_time_stamp

from flask import send_file, abort, render_template
ROOT_DIR = os.getcwd()
LOG_FOLDER_NAME = "logs"
PIPELINE_FOLDER_NAME = "sales"
SAVED_MODELS_DIR_NAME = "saved_models"
LOG_DIR = os.path.join(ROOT_DIR, LOG_FOLDER_NAME)
PIPELINE_DIR = os.path.join(ROOT_DIR, PIPELINE_FOLDER_NAME)
MODEL_DIR = os.path.join(ROOT_DIR, SAVED_MODELS_DIR_NAME)
MODEL_CONFIG_FILE_PATH = os.path.join(ROOT_DIR,CONFIG_DIR,"model.yaml")
SALES_DATA_KEY = "sales_data"
ITEM_OUTLET_SALES_KEY = "item_outlet_sales"

app = Flask(__name__)
pipeline=Pipeline()



@app.route('/artifact', defaults={'req_path': 'sales'})
@app.route('/artifact/<path:req_path>')
def render_artifact_dir(req_path):
    os.makedirs("sales", exist_ok=True)
    # Joining the base and the requested path
    print(f"req_path: {req_path}")
    abs_path = os.path.join(req_path)
    print(abs_path)
    # Return 404 if path doesn't exist
    if not os.path.exists(abs_path):
        return abort(404)

    # Check if path is a file and serve
    if os.path.isfile(abs_path):
        if ".html" in abs_path:
            with open(abs_path, "r",encoding="utf-8") as file:
                content = ''
                for line in file.readlines():
                    content = f"{content}{line}"
                return content
        return send_file(abs_path)

    # Show directory contents
    files = {os.path.join(abs_path, file_name): file_name for file_name in os.listdir(abs_path) if "artifact" in os.path.join(abs_path,file_name)}

    result = {
        "files": files,
        "parent_folder": os.path.dirname(abs_path),
        "parent_label": abs_path
    }
    return render_template('files.html', result=result)


@app.route('/', methods=['GET', 'POST'])
def index():
    try:
        return render_template('index.html')
    except Exception as e:
        return str(e)


@app.route('/view_experiment_hist', methods=['GET', 'POST'])
def view_experiment_history():
    experiment_df = Pipeline.get_experiments_status()
    context = {
        "experiment":experiment_df.to_html(classes='table table-striped col-12')
    }
    return render_template('experiment_history.html',context=context)

@app.route('/train', methods=['GET', 'POST'])
def train():
    message=""
    pipeline=Pipeline(config=Configuration(current_time_stamp=get_current_time_stamp()))
    if not Pipeline.experiment.running_status:
        message="Training started."
        pipeline.start()
    else:
        message="Training is already in progress."
    context = {
        "experiment": pipeline.get_experiments_status().to_html(classes='table table-striped col-12'  ),
        "message":message
    }
    return render_template('train.html',context=context)


@app.route('/predict', methods=['GET', 'POST'])
def predict():
    context = {
        SALES_DATA_KEY: None,
        ITEM_OUTLET_SALES_KEY: None
    }

    if request.method == 'POST':
            Item_Identifier = request.form['Item_Identifier']
            Item_Fat_Content = request.form['Item_Fat_Content']
            Item_Type = request.form['Item_Type']
            Outlet_Identifier = request.form['Outlet_Identifier']
            Outlet_Type = request.form['Outlet_Type']
            
            Item_MRP = float(request.form['Item_MRP'])
            Item_Visibility = float(request.form['Item_Visibility'])
            Item_Weight = float(request.form['Item_Weight'])
            Outlet_Establishment_Year= int(request.form['Outlet_Establishment_Year'])
            Outlet_Location_Type = request.form['Outlet_Location_Type']
            Outlet_Size = request.form['Outlet_Size']

            sales_data = SalesData(Item_Identifier=Item_Identifier,
                                              Item_Fat_Content = Item_Fat_Content,
                                              Item_Type = Item_Type,
                                              Outlet_Identifier = Outlet_Identifier,
                                              Outlet_Type = Outlet_Type,
                                              Item_MRP = Item_MRP,
                                            Item_Visibility = Item_Visibility,
                                            Item_Weight = Item_Weight,
                                            Outlet_Establishment_Year = Outlet_Establishment_Year , 
                                            Outlet_Location_Type = Outlet_Location_Type,
                                            Outlet_Size = Outlet_Size)

            sales_df = sales_data.get_sales_input_data_frame()
            sales_predictor = Salespredictor(model_dir=MODEL_DIR)
            item_outlet_sales = sales_predictor.predict(X=sales_df)
            context = {
            SALES_DATA_KEY: sales_data.get_sales_data_as_dict(),
            ITEM_OUTLET_SALES_KEY: item_outlet_sales,
                     }
            return render_template('predict.html', context=context)
    return render_template("predict.html", context=context)


@app.route('/saved_models', defaults={'req_path': 'saved_models'})
@app.route('/saved_models/<path:req_path>')
def saved_models_dir(req_path):
    os.makedirs("saved_models", exist_ok=True)
    # Joining the base and the requested path
    print(f"req_path: {req_path}")
    abs_path = os.path.join(req_path)
    print(abs_path)
    # Return 404 if path doesn't exist
    if not os.path.exists(abs_path):
        return abort(404)

    # Check if path is a file and serve
    if os.path.isfile(abs_path):
        return send_file(abs_path)

    # Show directory contents
    files = {os.path.join(abs_path, file): file for file in os.listdir(abs_path)}

    result = {
        "files": files,
        "parent_folder": os.path.dirname(abs_path),
        "parent_label": abs_path
    }
    return render_template('saved_models_files.html', result=result)

@app.route("/update_model_config",methods=['GET','POST'])
def update_model_config():
    try:
        if request.method=='POST':
            model_config = request.form['new_model_config']
            model_config = model_config.replace("'",'"')
            print(model_config)
            model_config =json.loads(model_config)

            write_yaml_file(file_path=MODEL_CONFIG_FILE_PATH,data=model_config)

        model_config=  read_yaml(file_path=MODEL_CONFIG_FILE_PATH)
        return render_template('update_model.html', result={"model_config":model_config})

    except  Exception as e:
        logging.exception(e)
        return str(e)


@app.route(f'/logs', defaults={'req_path': f'{LOG_FOLDER_NAME}'})
@app.route(f'/{LOG_FOLDER_NAME}/<path:req_path>')
def render_log_dir(req_path):
    os.makedirs(LOG_FOLDER_NAME, exist_ok=True)
    # Joining the base and the requested path
    logging.info(f"req_path: {req_path}")
    abs_path = os.path.join(req_path)
    print(abs_path)
    # Return 404 if path doesn't exist
    if not os.path.exists(abs_path):
        return abort(404)

    # Check if path is a file and serve
    if os.path.isfile(abs_path):
        log_df = get_log_dataframe(abs_path)
        context = {"log":log_df.to_html(classes="table-striped",index=False)}
        return render_template('log.html', context=context)

    # Show directory contents
    files = {os.path.join(abs_path, file): file for file in os.listdir(abs_path)}

    result = {
        "files": files,
        "parent_folder": os.path.dirname(abs_path),
        "parent_label": abs_path
    }
    return render_template('log_files.html', result=result)



if __name__=="__main__":
    app.run(debug= True)