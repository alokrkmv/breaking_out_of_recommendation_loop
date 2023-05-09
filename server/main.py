from flask import Flask, request
import logging
from flask_cors import CORS
import ast
logging.basicConfig(level = logging.INFO)
app = Flask(__name__)
CORS(app)

@app.route("/generate_recommendation",methods=["POST"])
def generate_recommendation():
    '''This is a post API layer written on the top of gpt3.5 API which takes users demographical information
    and current recommendation into consideration and suggest contents which can help them in breaking from the recommendation loop
    
    Request: 
        "data":{
        "gender":<str, optional>,
        "age":<int,optional>,
        "location":<str,optional>,
        "variation":<str, mandatory>,
        "current_recommendation":<str,mandatory>
            
        }

    Response:
        "response":{
            "recommendations":<text>
        }

    '''
    try:
        req_data = request.json
        data_dict = None
        if type(req_data)==dict:
            data_dict = req_data.get("data")
        else:
            data_dict = ast.literal_eval(req_data)

        if data_dict == None:
            response_dict = {
                "message":"Invalid request body!!! please make sure that request body follows the given request template",
                "request_template":{ "data":{
                "gender":"<str, optional>",
                "age":"<int,optional>",
                "location":"<str,optional>",
                "variation":"<str, mandatory>",
                "current_recommendation":"<str,mandatory>"}

                }
            }
            return response_dict
        if "variation" not in data_dict or data_dict["variation"]=="":
            return {"message":"Can't process your request as mandatory key variation is missing from request body"}
        if "current_recommendation" not in data_dict or data_dict["current_recommendation"]=="":
            return {"message":"Can't process your request as mandatory key current_recommendation is missing from request body"}


    except Exception as e:
        logging.log("Invalid request body!!!")
        return {"message":"Something went wrong in parsing the request body!!!"}

            
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)