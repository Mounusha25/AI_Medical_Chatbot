from dotenv import load_dotenv
from groq import Groq
import base64
import os
from PIL import Image
import io

#Step1: Setup GROQ API
load_dotenv()
GROQ_API_KEY=os.environ.get("GROQ_API_KEY")

#Step2: Convert image to required format with better error handling
def encode_image(image_path):
    try:
        # Try to open and validate the image first
        with Image.open(image_path) as img:
            # Convert to RGB if necessary (handles different formats)
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')
            
            # Save as JPEG in memory
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='JPEG', quality=85)
            img_byte_arr.seek(0)
            
            # Encode to base64
            return base64.b64encode(img_byte_arr.getvalue()).decode("utf-8")
            
    except Exception as e:
        # Fallback: try to read the file directly if PIL fails
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode("utf-8")
        except Exception as fallback_error:
            raise Exception(f"Cannot process image: {str(e)}. Fallback also failed: {str(fallback_error)}")

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

# Universal function for Hugging Face Spaces compatibility
def get_medical_response(query, image_file=None):
    """Universal medical response function that works for both local and Spaces"""
    try:
        if image_file:
            # Handle both local file paths and Gradio file objects
            image_path = image_file.name if hasattr(image_file, 'name') else image_file
            encoded_image = encode_image(image_path)
            return analyze_image_with_query(query, model, encoded_image)
        else:
            # Text-only query
            client = Groq()
            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": query}],
                model="meta-llama/llama-4-scout-17b-16e-instruct"
            )
            return chat_completion.choices[0].message.content
    except Exception as e:
        return f"I apologize, but I'm having trouble processing your request. Please try again or ensure your image is in a supported format (JPG, PNG, GIF, WebP)."