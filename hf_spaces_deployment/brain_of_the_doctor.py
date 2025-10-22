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
    """Analyze image with query using GROQ multimodal API"""
    try:
        # Get API key from environment
        groq_api_key = os.environ.get("GROQ_API_KEY")
        if not groq_api_key:
            raise Exception("GROQ API key not found")
            
        client = Groq(api_key=groq_api_key)
        
        messages = [
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
            }
        ]
        
        chat_completion = client.chat.completions.create(
            messages=messages,
            model=model
        )

        return chat_completion.choices[0].message.content
        
    except Exception as e:
        print(f"Image analysis error: {e}")
        raise e

def get_medical_response(query, image_file=None):
    """
    Main function to get medical analysis from symptoms and optional image
    Compatible with Hugging Face Spaces
    """
    try:
        # Check if GROQ API key is available
        groq_api_key = os.environ.get("GROQ_API_KEY")
        if not groq_api_key:
            return "API configuration error. Please contact support for assistance."
        
        # Initialize GROQ client with API key
        client = Groq(api_key=groq_api_key)
        
        if image_file:
            # If image is provided, use multimodal analysis
            try:
                # Handle both local file paths and Gradio file objects
                image_path = image_file.name if hasattr(image_file, 'name') else image_file
                encoded_image = encode_image(image_path)
                response = analyze_image_with_query(query, "meta-llama/llama-4-scout-17b-16e-instruct", encoded_image)
                return response
            except Exception as img_error:
                print(f"Image processing error: {img_error}")
                # Fall back to text-only analysis if image fails
                pass
        
        # Text-only analysis
        try:
            chat_completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": query
                    }
                ],
                model="llama3-8b-8192"  # Use text model for non-image queries
            )
            response = chat_completion.choices[0].message.content
            return response
            
        except Exception as api_error:
            print(f"GROQ API error: {api_error}")
            return f"I'm currently unable to process your request due to API limitations. Please try again in a moment or consult a healthcare professional for medical advice."
        
    except Exception as e:
        error_msg = f"Error in medical analysis: {str(e)}"
        print(error_msg)  # For debugging in Spaces logs
        return "I apologize, but I'm experiencing technical difficulties. Please try again or consult a healthcare professional for medical advice."