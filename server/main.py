from flask import Flask, request, send_file
from reportlab.pdfgen import canvas
from io import BytesIO
import logging
from flask_cors import CORS
import ast
import os
import openai
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from io import BytesIO
from reportlab.lib.colors import black
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
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
        print(data_dict)
        if "variation" not in data_dict or data_dict["variation"]=="":
            return {"message":"Can't process your request as mandatory key variation is missing from request body"}
        if "current_recommendation" not in data_dict or data_dict["current_recommendation"]=="":
            return {"message":"Can't process your request as mandatory key current_recommendation is missing from request body"}
        base_prompt = ""
        if "age" in data_dict and data_dict["age"]!="":
            base_prompt+="I am a "+str(data_dict["age"])+" years old"
        if "gender" in data_dict and data_dict["gender"]!="":
            base_prompt+=" "+data_dict["gender"]
        if "location" in data_dict and data_dict["location"]!="":
            base_prompt+=" located at"+" "+data_dict["location"]+"."
        if "sexual_preference" in data_dict and data_dict["sexual_preference"]!="":
            base_prompt+="I am a "+data_dict["sexual_preference"]+"."
        
        base_prompt+="My current youtube recommendations are from topics "+data_dict["current_recommendation"]+"."
      
        base_prompt+="I want to change my recommendations. Can you suggest me some content on youtube with channel name and youtube video title which are \
different from my current recommendation topics by atleast "+ data_dict["variation"]+ " percent while taking my gender, age sexual orientation and location into account. Can you also make sure to suggest at least 15 such recommendations?"

        print(base_prompt)
        openai.api_key = os.getenv("OPENAI_API_KEY")
        messages = [ {"role": "user", "content": base_prompt} ]
        chat = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", messages=messages
        )

        reply = chat.choices[0].message.content

        buffer = BytesIO()

        # Create the PDF object, using the buffer as its "file."
        doc = SimpleDocTemplate(buffer, pagesize=A4)

        styles = getSampleStyleSheet()
        styleN = styles['Normal']

        # Create a list to hold the paragraphs
        story = []

        # Create the paragraphs and add them to the story
        story.append(Paragraph(reply, styleN))

        # Build the story into the document
        doc.build(story)

        # Move buffer cursor to start
        buffer.seek(0)

        # Send buffer in a response
        return send_file(buffer, as_attachment=True, download_name='report.pdf', mimetype='application/pdf')

        # return {"new_recommendations":reply}

    except Exception as e:
        logging.exception("Invalid request body!!!")
        return {"message":"Something went wrong in parsing the request body!!!"}

            
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)