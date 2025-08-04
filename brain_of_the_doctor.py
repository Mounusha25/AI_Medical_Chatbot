from dotenv import load_dotenv
from groq import Groq
import base64
import os

#Step1: Setup GROQ API
load_dotenv()
GROQ_API_KEY=os.environ.get("GROQ_API_KEY")

#Step2: Convert image to required format
#image_path = "acne.jpg"
def encode_image(image_path):
    image_file = open(image_path, "rb")
    return base64.b64encode(image_file.read()).decode("utf-8")

#step3: Setup Multimodal API

model = "meta-llama/llama-4-scout-17b-16e-instruct"
query = "Is there something wrong with this skin condition?"

def analyze_image_with_query(query, model, encoded_image):
    client=Groq()  
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "text", 
                    "text": query
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{encoded_image}",
                    },
                },
            ],
        }]
    chat_completion=client.chat.completions.create(
        messages=messages,
        model=model
    )

    return chat_completion.choices[0].message.content