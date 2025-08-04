from dotenv import load_dotenv
import os
import gradio as gr

from brain_of_the_doctor import encode_image, analyze_image_with_query
from voice_of_the_patient import record_audio, transcribe_with_groq
from voice_of_the_doctor import text_to_speech_with_gtts, text_to_speech_with_elevenlabs

load_dotenv()

system_prompt="""You have to act as a professional doctor, i know you are not but this is for learning purpose. 
            What's in this image?. Do you find anything wrong with it medically? 
            If you make a differential, suggest some remedies for them. Donot add any numbers or special characters in 
            your response. Your response should be in one long paragraph. Also always answer as if you are answering to a real person.
            Donot say 'In the image I see' but say 'With what I see, I think you have ....'
            Dont respond as an AI model in markdown, your answer should mimic that of an actual doctor not an AI bot, 
            Keep your answer concise (max 2 sentences). No preamble, start your answer right away please"""


def process_inputs(audio_filepath, image_filepath):
    # Transcribe the audio input to text
    speech_to_text_output = transcribe_with_groq(
        GROQ_API_KEY=os.environ.get("GROQ_API_KEY"), 
        audio_filepath=audio_filepath,
        stt_model="whisper-large-v3"
    )

    # Handle the image input
    if image_filepath:
        doctor_response = analyze_image_with_query(
            query=system_prompt+speech_to_text_output, 
            encoded_image=encode_image(image_filepath), 
            model="meta-llama/llama-4-scout-17b-16e-instruct"
        ) #model="meta-llama/llama-4-maverick-17b-128e-instruct") 
    else:
        doctor_response = "No image provided for me to analyze"

    # Convert the doctor's response to speech
    voice_of_doctor = text_to_speech_with_elevenlabs(
        input_text=doctor_response, 
        output_filepath="final.mp3"
    ) 

    return speech_to_text_output, doctor_response, voice_of_doctor

# -------------------------------------------
# UI Interface
# -------------------------------------------
with gr.Blocks(theme=gr.themes.Soft(primary_hue="blue"), title="Smart Medical Assistant") as demo:
    
    # Centered, styled title using HTML
    gr.HTML("""
        <h1 style='text-align: center; color: #1e3a8a; font-size: 2.5em; font-family: sans-serif;'>
            🩺 Smart Medical Assistant: AI Diagnosis with Voice & Image Analysis
        </h1>
        <p style='text-align: center; color: #4b5563; font-size: 1.1em;'>
            Talk to the AI doctor and get feedback based on your symptoms and image input.
        </p>
    """)
    
    # gr.Markdown("## 🩺 Smart Medical Assistant: AI Diagnosis with Voice & Image Analysis")
    # gr.Markdown("Talk to the AI doctor and get medical feedback based on your symptoms and image input.")

    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### 🎤 Record your Symptoms")
            audio_input = gr.Audio(sources=["microphone"], type="filepath", label="Patient's Voice")

            gr.Markdown("### 🖼️ Upload an Image of the Condition (Optional)")
            image_input = gr.Image(type="filepath", label="Upload Image")

            submit_btn = gr.Button("🩺 Submit for Diagnosis")
            clear_btn = gr.Button("❌ Clear")

        with gr.Column(scale=1):
            gr.Markdown("### 🗣️ Your Symptoms (Transcribed)")
            symptoms_text = gr.Textbox(label="Speech to Text", interactive=False)

            gr.Markdown("### 🧑‍⚕️ Doctor’s Suggestions")
            doctor_response = gr.Textbox(label="Doctor’s Response", lines=3, interactive=False)

            gr.Markdown("### 🔊 Doctor’s Voice Response")
            voice_output = gr.Audio(label="Doctor's Voice Response")

    # Bind logic
    submit_btn.click(fn=process_inputs,
                     inputs=[audio_input, image_input],
                     outputs=[symptoms_text, doctor_response, voice_output])
    
    clear_btn.click(lambda: ("", "", "", None), 
                    inputs=[], 
                    outputs=[audio_input, symptoms_text, doctor_response, voice_output])
    
    # Run the app
if __name__ == "__main__":
    demo.launch(favicon_path="ai_doctor_logo.png", debug=True, share=True)