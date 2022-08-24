from multiprocessing.dummy import Pipe
from xml.etree.ElementTree import PI
from flask import Flask,request
import sys

from matplotlib.style import context
from sales.logger import logging
from sales.exception import SalesException
import os,sys
from sales.pipeline.pipeline import Pipeline
from sales.entity.sales_predictor import Salespredictor,SalesData
from flask import send_file, abort, render_template
ROOT_DIR = os.getcwd()
LOG_FOLDER_NAME = "sales_logs"
PIPELINE_FOLDER_NAME = "sales"
SAVED_MODELS_DIR_NAME = "saved_models"
LOG_DIR = os.path.join(ROOT_DIR, LOG_FOLDER_NAME)
PIPELINE_DIR = os.path.join(ROOT_DIR, PIPELINE_FOLDER_NAME)
MODEL_DIR = os.path.join(ROOT_DIR, SAVED_MODELS_DIR_NAME)

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
    files = {os.path.join(abs_path, file): file for file in os.listdir(abs_path)}

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
    
    experiment_list = pipeline.get_experiment_history()
    context = {
        "experiment_list":[experiment.to_html(classes='table table-striped') for experiment in experiment_list]
    }
    return render_template('experiment_history.html',context=context)

@app.route('/train', methods=['GET', 'POST'])
def train():
    if not pipeline.experiment.running_status:
        pipeline.start()
    context = {
        "experiment": pipeline.get_experiment_status().to_html(classes='table table-striped')
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


@app.route('/logs', defaults={'req_path': 'logs'})
@app.route('/logs/<path:req_path>')
def render_log_dir(req_path):
    os.makedirs("logs", exist_ok=True)
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
    return render_template('log_files.html', result=result)



if __name__=="__main__":
    app.run(debug= True)