import os
import gradio as gr
import tempfile

# Handle environment loading (works for both local and Spaces)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not available in Spaces, use environment variables directly

# Universal imports that work for both local and Spaces
try:
    # Try local imports first
    from brain_of_the_doctor import encode_image, analyze_image_with_query, get_medical_response
    from voice_of_the_patient import transcribe_with_groq, get_audio_text  
    from voice_of_the_doctor import text_to_speech_with_elevenlabs, generate_audio
    LOCAL_MODE = True
except ImportError:
    # Fallback to Spaces-only imports
    from brain_of_the_doctor import get_medical_response
    from voice_of_the_patient import get_audio_text
    from voice_of_the_doctor import generate_audio
    LOCAL_MODE = False

system_prompt="""You have to act as a professional doctor, i know you are not but this is for learning purpose. 
            What's in this image?. Do you find anything wrong with it medically? 
            If you make a differential, suggest some remedies for them. Donot add any numbers or special characters in 
            your response. Your response should be in one long paragraph. Also always answer as if you are answering to a real person.
            Donot say 'In the image I see' but say 'With what I see, I think you have ....'
            Dont respond as an AI model in markdown, your answer should mimic that of an actual doctor not an AI bot, 
            Keep your answer concise (max 2 sentences). No preamble, start your answer right away please"""


def process_inputs(audio_filepath, image_file):
    # Universal audio transcription that works for both local and Spaces
    if LOCAL_MODE and audio_filepath:
        # Local mode - use GROQ API with environment variables
        speech_to_text_output = transcribe_with_groq(
            GROQ_API_KEY=os.environ.get("GROQ_API_KEY"), 
            audio_filepath=audio_filepath,
            stt_model="whisper-large-v3"
        )
    elif audio_filepath:
        # Spaces mode - use simplified audio processing
        speech_to_text_output = get_audio_text(audio_filepath)
    else:
        speech_to_text_output = ""

    # Handle the image input with enhanced error handling
    if image_file:
        try:
            # Get the file path from the uploaded file
            image_filepath = image_file.name if hasattr(image_file, 'name') else image_file
            
            # Check if it's a supported format
            if image_filepath.lower().endswith('.avif'):
                doctor_response = "I apologize, but AVIF image format is not currently supported. Please upload your medical image in JPG, PNG, GIF, or WebP format for analysis."
                image_display = None
            else:
                # Universal image processing for both local and Spaces
                if LOCAL_MODE:
                    # Local mode - use original functions
                    doctor_response = analyze_image_with_query(
                        query=system_prompt+speech_to_text_output, 
                        encoded_image=encode_image(image_filepath), 
                        model="meta-llama/llama-4-scout-17b-16e-instruct"
                    )
                else:
                    # Spaces mode - use universal function
                    doctor_response = get_medical_response(system_prompt + speech_to_text_output, image_file)
                
                image_display = image_filepath if LOCAL_MODE else image_file
        except Exception as e:
            # Handle any other image processing errors gracefully
            if "UnidentifiedImageError" in str(e) or "cannot identify image file" in str(e):
                doctor_response = "I'm unable to process this image format. Please upload a medical image in JPG, PNG, GIF, or WebP format for analysis."
            elif "avif" in str(e).lower():
                doctor_response = "AVIF format is not supported. Please convert your image to JPG, PNG, GIF, or WebP format and try again."
            else:
                doctor_response = "I encountered an issue analyzing the image. Please try uploading a different image in a standard format (JPG, PNG, GIF, or WebP)."
            image_display = None
    else:
        doctor_response = "No image provided for me to analyze. Please upload a medical image for visual diagnosis."
        image_display = None

    # Return text response first (voice will be generated separately)
    return speech_to_text_output, doctor_response, image_display

def generate_voice_response(doctor_response):
    """Generate voice response after text is displayed - Universal for local and Spaces"""
    if doctor_response and doctor_response.strip():
        try:
            if LOCAL_MODE:
                # Local mode - use original function with file output
                voice_of_doctor = text_to_speech_with_elevenlabs(
                    input_text=doctor_response, 
                    output_filepath="final.mp3"
                )
                return voice_of_doctor
            else:
                # Spaces mode - use universal function
                voice_of_doctor = generate_audio(doctor_response)
                return voice_of_doctor
        except Exception as e:
            # Fallback if voice synthesis fails (no console output)
            return "final.mp3" if LOCAL_MODE else None
    return None

def display_uploaded_image(image_file):
    """Function to show uploaded image in the interface - Universal for local and Spaces"""
    if image_file:
        if LOCAL_MODE:
            return image_file.name, gr.update(visible=True)
        else:
            return image_file, gr.update(visible=True)
    else:
        return None, gr.update(visible=False)

# -------------------------------------------
# Optimized Professional Medical Interface CSS
# -------------------------------------------
custom_css = """
/* Fast-loading Professional Medical Interface */
:root {
    --primary-blue: #1565c0;
    --secondary-blue: #1976d2;
    --accent-blue: #42a5f5;
    --light-blue: #e3f2fd;
    --text-primary: #0d47a1;
    --text-secondary: #1565c0;
    --border-color: rgba(21, 101, 192, 0.15);
    --shadow-color: rgba(21, 101, 192, 0.1);
    --white: #ffffff;
}

/* Medical Animation Keyframes */
@keyframes pulse {
    0%, 100% { transform: scale(1); opacity: 0.7; }
    50% { transform: scale(1.05); opacity: 1; }
}

@keyframes float {
    0%, 100% { transform: translateY(0px) rotate(0deg); }
    33% { transform: translateY(-10px) rotate(1deg); }
    66% { transform: translateY(-5px) rotate(-1deg); }
}

@keyframes heartbeat {
    0%, 100% { transform: scale(1); }
    25% { transform: scale(1.1); }
    50% { transform: scale(1); }
    75% { transform: scale(1.05); }
}

@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(30px); }
    to { opacity: 1; transform: translateY(0); }
}

@keyframes slideInLeft {
    from { opacity: 0; transform: translateX(-30px); }
    to { opacity: 1; transform: translateX(0); }
}

@keyframes slideInRight {
    from { opacity: 0; transform: translateX(30px); }
    to { opacity: 1; transform: translateX(0); }
}

@keyframes shimmer {
    0% { background-position: -200px 0; }
    100% { background-position: calc(200px + 100%) 0; }
}

@keyframes medicalWave {
    0% { transform: translateX(-100%); }
    100% { transform: translateX(100%); }
}

/* Clean Professional Background */
.gradio-container {
    position: relative;
}

@keyframes medicalFloat {
    0%, 100% { transform: translate(0px, 0px) rotate(0deg); }
    33% { transform: translate(30px, -30px) rotate(1deg); }
    66% { transform: translate(-20px, 20px) rotate(-1deg); }
}

@keyframes medicalGrid {
    0% { transform: translate(0, 0); }
    100% { transform: translate(50px, 50px); }
}

/* Floating Medical Icons Background */
.medical-background {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    pointer-events: none;
    z-index: -1;
    overflow: hidden;
}

.medical-icon-float {
    position: absolute;
    font-size: 2em;
    color: rgba(33, 150, 243, 0.08);
    animation: float 15s infinite ease-in-out;
}

.medical-icon-float:nth-child(1) { top: 10%; left: 10%; animation-delay: 0s; }
.medical-icon-float:nth-child(2) { top: 20%; left: 80%; animation-delay: 2s; }
.medical-icon-float:nth-child(3) { top: 60%; left: 15%; animation-delay: 4s; }
.medical-icon-float:nth-child(4) { top: 80%; left: 70%; animation-delay: 6s; }
.medical-icon-float:nth-child(5) { top: 40%; left: 60%; animation-delay: 8s; }
.medical-icon-float:nth-child(6) { top: 70%; left: 30%; animation-delay: 10s; }

@keyframes float {
    0%, 100% { transform: translateY(0px) rotate(0deg); opacity: 0.05; }
    25% { transform: translateY(-20px) rotate(2deg); opacity: 0.1; }
    50% { transform: translateY(0px) rotate(0deg); opacity: 0.08; }
    75% { transform: translateY(-10px) rotate(-1deg); opacity: 0.06; }
}

/* Pulse Animation for Cards */
.medical-card::after {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: radial-gradient(circle at center, rgba(33, 150, 243, 0.02) 0%, transparent 70%);
    border-radius: 12px;
    opacity: 0;
    animation: cardPulse 4s ease-in-out infinite;
    pointer-events: none;
}

@keyframes cardPulse {
    0%, 100% { opacity: 0; transform: scale(1); }
    50% { opacity: 1; transform: scale(1.02); }
}

/* Global Theme Detection */
@media (prefers-color-scheme: dark) {
    .gradio-container {
        background: var(--bg-primary-dark) !important;
        color: var(--text-primary-dark) !important;
    }
    
    .gradio-container::before {
        background-image: 
            radial-gradient(circle at 20% 80%, rgba(148, 163, 184, 0.08) 0%, transparent 30%),
            radial-gradient(circle at 80% 20%, rgba(71, 85, 105, 0.06) 0%, transparent 30%),
            radial-gradient(circle at 40% 40%, rgba(148, 163, 184, 0.04) 0%, transparent 40%);
    }
    
    .medical-icon-float {
        color: rgba(148, 163, 184, 0.12);
    }
}

/* Global Theme */
.gradio-container {
    background: var(--bg-primary-light) !important;
    font-family: 'Inter', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
    color: var(--text-primary-light) !important;
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
    position: relative;
    overflow-x: hidden;
}

/* Dark theme styles */
.dark .gradio-container {
    background: var(--bg-primary-dark) !important;
    color: var(--text-primary-dark) !important;
}

/* Modern Professional Header */
.header-container {
    background: linear-gradient(135deg, var(--primary-blue) 0%, var(--secondary-blue) 100%) !important;
    padding: 32px 40px !important;
    border-radius: 20px !important;
    margin-bottom: 32px !important;
    box-shadow: 0 8px 40px rgba(0, 102, 204, 0.15) !important;
    border: none !important;
    position: relative !important;
    overflow: hidden !important;
}

.header-container::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1), transparent);
    transition: left 0.8s ease-in-out;
}

.header-container::after {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: 
        radial-gradient(circle at 10% 20%, rgba(255, 255, 255, 0.1) 0%, transparent 20%),
        radial-gradient(circle at 90% 80%, rgba(255, 255, 255, 0.05) 0%, transparent 25%);
    animation: headerPulse 6s ease-in-out infinite;
    pointer-events: none;
}

@keyframes headerPulse {
    0%, 100% { opacity: 0.5; }
    50% { opacity: 1; }
}

.header-container:hover::before {
    left: 100%;
}

.header-container:hover {
    transform: translateY(-2px);
    box-shadow: 0 12px 40px rgba(21, 101, 192, 0.3);
}

.dark .header-container {
    background: linear-gradient(135deg, rgba(30, 41, 59, 0.95) 0%, rgba(51, 65, 85, 0.9) 100%);
    border: 1px solid rgba(148, 163, 184, 0.2);
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.6);
}

.dark .header-container:hover {
    box-shadow: 0 12px 40px rgba(30, 41, 59, 0.8);
}

.dark .header-container::after {
    background: 
        radial-gradient(circle at 10% 20%, rgba(148, 163, 184, 0.1) 0%, transparent 20%),
        radial-gradient(circle at 90% 80%, rgba(148, 163, 184, 0.05) 0%, transparent 25%);
}

/* Professional Light Theme Only */

/* Professional Medical Header */

/* Interactive Card Styling with Enhanced Backgrounds */
.medical-card,
.gradio-group {
    background: var(--bg-card-light) !important;
    border-radius: 12px;
    padding: 24px;
    margin: 15px 0;
    box-shadow: 0 4px 20px var(--shadow-light);
    border: 1px solid var(--border-light);
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
    overflow: hidden;
    cursor: pointer;
}

.dark .medical-card,
.dark .gradio-group {
    background: var(--bg-card-dark) !important;
    border: 1px solid var(--border-dark);
    box-shadow: 0 4px 20px var(--shadow-dark);
}

.medical-card::before,
.gradio-group::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: linear-gradient(90deg, var(--accent-primary), var(--accent-secondary));
    transform: scaleX(0);
    transition: transform 0.3s ease;
}

.medical-card:hover::before,
.gradio-group:hover::before {
    transform: scaleX(1);
}

.medical-card:hover,
.gradio-group:hover {
    transform: translateY(-4px) scale(1.02);
    box-shadow: 0 12px 40px var(--shadow-light);
    border-color: var(--accent-primary);
}

.dark .medical-card:hover,
.dark .gradio-group:hover {
    box-shadow: 0 12px 40px var(--shadow-dark);
}

/* Enhanced Text Styling for Dark Mode */
.dark * {
    color: var(--text-primary-dark) !important;
}

.dark .medical-card p {
    color: var(--text-secondary-dark) !important;
}

.dark .gr-textbox textarea,
.dark .gr-textbox input {
    color: var(--text-primary-dark) !important;
    background: rgba(15, 23, 42, 0.8) !important;
}

.dark .gr-textbox textarea::placeholder,
.dark .gr-textbox input::placeholder {
    color: var(--text-secondary-dark) !important;
    opacity: 0.6 !important;
}

/* Interactive Input Components with Background Animation */
.gr-form > *,
.gr-textbox,
.gr-audio,
.gr-image {
    border-radius: 10px !important;
    border: 2px solid var(--border-light) !important;
    background: var(--bg-card-light) !important;
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
    position: relative !important;
    overflow: hidden !important;
}

.gr-form > *::before,
.gr-textbox::before,
.gr-audio::before,
.gr-image::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(33, 150, 243, 0.05), transparent);
    transition: left 0.6s ease;
    pointer-events: none;
    z-index: 1;
}

.gr-form > *:hover::before,
.gr-textbox:hover::before,
.gr-audio:hover::before,
.gr-image:hover::before {
    left: 100%;
}

.dark .gr-form > *,
.dark .gr-textbox,
.dark .gr-audio,
.dark .gr-image {
    background: var(--bg-card-dark) !important;
    border-color: var(--border-dark) !important;
}

.gr-textbox:hover,
.gr-audio:hover,
.gr-image:hover {
    border-color: var(--accent-primary) !important;
    box-shadow: 0 0 20px var(--glow-color) !important;
    transform: translateY(-1px) !important;
}

/* Enhanced Labels */
.gr-form label,
.gr-textbox label,
.gr-audio label,
.gr-image label {
    color: var(--accent-secondary) !important;
    font-weight: 600 !important;
    font-size: 1em !important;
    margin-bottom: 8px !important;
    transition: color 0.3s ease !important;
}

.dark .gr-form label,
.dark .gr-textbox label,
.dark .gr-audio label,
.dark .gr-image label {
    color: var(--accent-primary) !important;
}

/* Interactive Textbox Styling */
.gr-textbox textarea,
.gr-textbox input {
    color: var(--text-primary-light) !important;
    background: transparent !important;
    border: none !important;
    padding: 14px !important;
    font-size: 14px !important;
    line-height: 1.6 !important;
    transition: all 0.3s ease !important;
    position: relative !important;
    z-index: 2 !important;
}

.gr-textbox textarea::placeholder,
.gr-textbox input::placeholder {
    color: var(--text-secondary-light) !important;
    opacity: 0.7 !important;
    transition: opacity 0.3s ease !important;
}

.gr-textbox:focus-within textarea::placeholder,
.gr-textbox:focus-within input::placeholder {
    opacity: 0.5 !important;
}

/* Interactive Medical Buttons with Animations */
.gradio-button {
    background: linear-gradient(135deg, var(--primary-blue) 0%, var(--secondary-blue) 100%) !important;
    color: var(--white) !important;
    border: none !important;
    border-radius: 14px !important;
    padding: 14px 28px !important;
    font-weight: 600 !important;
    font-size: 15px !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    box-shadow: 0 6px 24px rgba(21, 101, 192, 0.25) !important;
    cursor: pointer !important;
    width: 100% !important;
    box-sizing: border-box !important;
    min-height: 48px !important;
    position: relative !important;
    overflow: hidden !important;
    animation: fadeInUp 0.8s ease-out !important;
}

/* Button Pulse Animation */
.gradio-button::before {
    content: '';
    position: absolute;
    top: 50%;
    left: 50%;
    width: 0;
    height: 0;
    background: rgba(255, 255, 255, 0.3);
    border-radius: 50%;
    transform: translate(-50%, -50%);
    transition: width 0.6s ease, height 0.6s ease;
}

.gradio-button:active::before {
    width: 300px;
    height: 300px;
}

/* Medical Cross Icon Animation */
.gradio-button::after {
    content: '✚';
    position: absolute;
    right: 15px;
    top: 50%;
    transform: translateY(-50%);
    opacity: 0;
    transition: all 0.3s ease;
    font-size: 14px;
}

/* Button Responsive Design */
@media (min-width: 768px) {
    .gradio-button {
        width: auto !important;
        padding: 16px 32px !important;
        font-size: 14px !important;
        border-radius: 16px !important;
    }
}

.gradio-button:hover {
    transform: translateY(-4px) scale(1.02) !important;
    box-shadow: 0 12px 40px rgba(21, 101, 192, 0.4) !important;
    background: linear-gradient(135deg, var(--secondary-blue) 0%, var(--accent-blue) 100%) !important;
}

.gradio-button:hover::after {
    opacity: 1 !important;
    transform: translateY(-50%) rotate(180deg) !important;
}

/* Record Button Special Animation */
.gradio-button[value*="Record"]::after {
    content: '🎤';
    animation: pulse 2s ease-in-out infinite;
}

.gradio-button[value*="Record"]:hover::after {
    animation: heartbeat 1s ease-in-out infinite;
}

/* Mobile Button Optimization */
@media (max-width: 767px) {
    .gradio-button:hover {
        transform: scale(1.02) !important;
    }
    
    .gradio-button:active {
        transform: scale(0.98) !important;
    }
}

.gradio-button::before {
    content: '';
    position: absolute;
    top: 50%;
    left: 50%;
    width: 0;
    height: 0;
    background: rgba(255, 255, 255, 0.2);
    border-radius: 50%;
    transform: translate(-50%, -50%);
    transition: width 0.6s, height 0.6s;
}

.gradio-button::after {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1), transparent);
    transition: left 0.5s ease;
}

.gradio-button:hover::before {
    width: 300px;
    height: 300px;
}

.gradio-button:hover::after {
    left: 100%;
}

.gradio-button:hover {
    transform: translateY(-2px) scale(1.05) !important;
    box-shadow: 0 8px 30px rgba(33, 150, 243, 0.5) !important;
}

.gradio-button:active {
    transform: translateY(0) scale(0.98) !important;
}

/* Clear Button with Different Color */
.clear-btn {
    background: linear-gradient(135deg, #ef4444 0%, #f87171 100%) !important;
}

.clear-btn:hover {
    box-shadow: 0 8px 30px rgba(239, 68, 68, 0.4) !important;
}

/* Modern Section Headers */
.section-header {
    color: var(--primary-blue) !important;
    font-weight: 600 !important;
    font-size: 18px !important;
    margin-bottom: 16px !important;
    display: flex !important;
    align-items: center !important;
    gap: 12px !important;
}

.section-header .medical-icon {
    background: var(--accent-blue) !important;
    color: var(--primary-blue) !important;
    width: 40px !important;
    height: 40px !important;
    border-radius: 10px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    font-size: 20px !important;
}

.theme-dark .section-header {
    color: #90cdf4 !important;
}

.theme-dark .section-header .medical-icon {
    background: #2a4365 !important;
    color: #90cdf4 !important;
}

.dark .section-header {
    color: var(--accent-primary) !important;
}

.section-header::after {
    content: '';
    position: absolute;
    bottom: 0;
    left: 0;
    width: 0;
    height: 2px;
    background: linear-gradient(90deg, var(--accent-primary), var(--accent-secondary));
    transition: width 0.4s ease;
}

.medical-card:hover .section-header::after,
.gradio-group:hover .section-header::after {
    width: 100%;
}

/* Animated Medical Icons */
.medical-icon {
    color: var(--accent-primary) !important;
    margin-right: 10px;
    font-size: 1.3em;
    transition: all 0.3s ease;
    display: inline-block;
}

.medical-card:hover .medical-icon,
.gradio-group:hover .medical-icon {
    transform: scale(1.2) rotate(5deg);
    filter: drop-shadow(0 4px 8px var(--glow-color));
}

/* Enhanced Audio Component */
.gr-audio {
    border: 2px solid var(--border-light) !important;
    border-radius: 10px !important;
    background: var(--bg-card-light) !important;
    padding: 12px !important;
    transition: all 0.3s ease !important;
}

.dark .gr-audio {
    background: var(--bg-card-dark) !important;
    border-color: var(--border-dark) !important;
}

/* Interactive Image Upload with Background Animation */
.image-upload {
    border: 3px dashed var(--border-light) !important;
    border-radius: 10px !important;
    background: rgba(33, 150, 243, 0.02) !important;
    min-height: 180px !important;
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
    position: relative !important;
    overflow: hidden !important;
}

.dark .image-upload {
    background: rgba(148, 163, 184, 0.05) !important;
    border-color: var(--border-dark) !important;
}

.image-upload::before {
    content: '📸 Drop your medical image here or click to upload';
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    color: var(--text-secondary-light);
    font-weight: 500;
    opacity: 0;
    transition: opacity 0.3s ease;
    pointer-events: none;
    z-index: 2;
}

.image-upload::after {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: radial-gradient(circle at center, rgba(33, 150, 243, 0.05) 0%, transparent 60%);
    opacity: 0;
    transition: opacity 0.3s ease;
    pointer-events: none;
}

.dark .image-upload::before {
    color: var(--text-secondary-dark);
}

.image-upload:hover::before {
    opacity: 1;
}

.image-upload:hover::after {
    opacity: 1;
}

.image-upload:hover {
    border-color: var(--accent-primary) !important;
    background: rgba(33, 150, 243, 0.08) !important;
    transform: scale(1.02) !important;
    box-shadow: 0 8px 25px var(--glow-color) !important;
}

/* Enhanced Info Banner with Background Animation */
.info-banner {
    background: linear-gradient(135deg, rgba(33, 150, 243, 0.08) 0%, rgba(21, 101, 192, 0.05) 100%);
    border: 1px solid rgba(33, 150, 243, 0.2);
    border-radius: 10px;
    padding: 18px;
    margin: 20px 0;
    text-align: center;
    box-shadow: 0 4px 15px rgba(33, 150, 243, 0.1);
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
}

.info-banner::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(33, 150, 243, 0.1), transparent);
    transition: left 0.8s ease;
}

.info-banner:hover::before {
    left: 100%;
}

.dark .info-banner {
    background: linear-gradient(135deg, rgba(148, 163, 184, 0.1) 0%, rgba(71, 85, 105, 0.05) 100%);
    border-color: var(--border-dark);
}

.info-banner:hover {
    transform: translateY(-1px);
    box-shadow: 0 6px 20px rgba(33, 150, 243, 0.15);
}

.info-banner strong {
    color: var(--accent-secondary) !important;
    font-weight: 600 !important;
}

.dark .info-banner strong {
    color: var(--accent-primary) !important;
}

/* Interactive Footer */
.footer {
    text-align: center;
    margin-top: 30px;
    padding: 24px;
    background: var(--bg-card-light);
    border-radius: 12px;
    border-top: 3px solid var(--accent-primary);
    box-shadow: 0 -4px 20px var(--shadow-light);
    transition: all 0.3s ease;
}

.dark .footer {
    background: var(--bg-card-dark);
    box-shadow: 0 -4px 20px var(--shadow-dark);
}

.footer:hover {
    transform: translateY(-2px);
    box-shadow: 0 -6px 25px var(--shadow-light);
}

.dark .footer:hover {
    box-shadow: 0 -6px 25px var(--shadow-dark);
}

.footer p {
    color: var(--text-secondary-light) !important;
    font-weight: 500 !important;
    margin: 6px 0 !important;
    font-size: 0.9em !important;
    transition: color 0.3s ease !important;
}

.dark .footer p {
    color: var(--text-secondary-dark) !important;
}

.footer strong {
    color: #ef4444 !important;
    font-weight: 600 !important;
}

/* Enhanced focus states with glow */
.gr-textbox:focus-within,
.gr-audio:focus-within,
.gr-image:focus-within {
    border-color: var(--accent-primary) !important;
    box-shadow: 0 0 0 4px var(--glow-color) !important;
    transform: translateY(-2px) !important;
}

/* Loading states with shimmer effect */
.gr-loading {
    background: linear-gradient(90deg, 
        var(--bg-card-light), 
        rgba(33, 150, 243, 0.1), 
        var(--bg-card-light)) !important;
    background-size: 200% 100% !important;
    animation: shimmer 1.5s ease-in-out infinite !important;
}

.dark .gr-loading {
    background: linear-gradient(90deg, 
        var(--bg-card-dark), 
        rgba(148, 163, 184, 0.2), 
        var(--bg-card-dark)) !important;
}

@keyframes shimmer {
    0% { background-position: 200% 0; }
    100% { background-position: -200% 0; }
}

/* Responsive Design */
@media (max-width: 768px) {
    .medical-card {
        margin: 10px 0;
        padding: 20px;
    }
    
    .header-container {
        padding: 15px 20px;
    }
    
    .gradio-button {
        padding: 12px 20px !important;
        font-size: 13px !important;
    }
    
    .medical-icon-float {
        font-size: 1.5em;
    }
}

/* Enhanced styling for unified interactive boxes */
.gradio-group {
    background: var(--bg-card-light) !important;
    border-radius: 12px !important;
    padding: 24px !important;
    margin: 15px 0 !important;
    box-shadow: 0 4px 20px var(--shadow-light) !important;
    border: 1px solid var(--border-light) !important;
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
    position: relative !important;
    overflow: visible !important;
    cursor: pointer !important;
}

.dark .gradio-group {
    background: var(--bg-card-dark) !important;
    border: 1px solid var(--border-dark) !important;
    box-shadow: 0 4px 20px var(--shadow-dark) !important;
}

/* Modern Clean Layout */
* {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
}

/* Interactive Full-Screen Layout with Medical Background */
body {
    background: var(--bg-primary) !important;
    margin: 0 !important;
    padding: 0 !important;
    min-height: 100vh !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
    overflow-x: hidden !important;
    position: relative !important;
}

/* Animated Medical Background Elements */
body::before {
    content: '';
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    pointer-events: none;
    z-index: 0;
    background: 
        radial-gradient(circle at 15% 20%, rgba(33, 150, 243, 0.03) 0%, transparent 50%),
        radial-gradient(circle at 85% 80%, rgba(21, 101, 192, 0.02) 0%, transparent 50%),
        radial-gradient(circle at 50% 50%, rgba(66, 165, 245, 0.015) 0%, transparent 70%);
    animation: pulse 8s ease-in-out infinite;
}

/* Floating Medical Icons */
body::after {
    content: '🏥 💊 🩺 ❤️ 🧬 💉 🔬 📋';
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    font-size: 1.5em;
    color: rgba(21, 101, 192, 0.05);
    display: flex;
    flex-wrap: wrap;
    justify-content: space-around;
    align-items: center;
    pointer-events: none;
    z-index: 1;
    animation: float 12s ease-in-out infinite;
}

.gradio-container {
    background: transparent !important;
    max-width: 100% !important;
    width: 100% !important;
    margin: 0 !important;
    padding: 15px !important;
    box-sizing: border-box !important;
    position: relative !important;
    z-index: 10 !important;
    animation: fadeInUp 0.8s ease-out !important;
}

/* Responsive Container */
@media (min-width: 768px) {
    .gradio-container {
        padding: 25px !important;
        max-width: 1200px !important;
        margin: 0 auto !important;
    }
}

@media (min-width: 1200px) {
    .gradio-container {
        max-width: 1400px !important;
        padding: 30px !important;
    }
}

/* Interactive Professional Card Design with Animations */
.gr-group,
.gradio-group {
    background: var(--card-bg) !important;
    border-radius: 20px !important;
    padding: 20px !important;
    margin: 15px 0 !important;
    border: 1px solid var(--border-color) !important;
    box-shadow: 0 8px 32px var(--shadow-color) !important;
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
    backdrop-filter: blur(12px) !important;
    width: 100% !important;
    box-sizing: border-box !important;
    position: relative !important;
    overflow: hidden !important;
    animation: slideInUp 0.6s ease-out !important;
}

/* Medical Card Accent Border Animation */
.gr-group::before,
.gradio-group::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: linear-gradient(90deg, 
        var(--primary-blue) 0%, 
        var(--accent-blue) 50%, 
        var(--primary-blue) 100%);
    border-radius: 20px 20px 0 0;
    opacity: 0;
    transition: opacity 0.3s ease;
}

/* Shimmer Effect on Hover */
.gr-group::after,
.gradio-group::after {
    content: '';
    position: absolute;
    top: 0;
    left: -200px;
    width: 200px;
    height: 100%;
    background: linear-gradient(90deg, 
        transparent, 
        rgba(255, 255, 255, 0.4), 
        transparent);
    transition: all 0.6s ease;
    z-index: 1;
}

/* Responsive Card Padding */
@media (min-width: 768px) {
    .gr-group,
    .gradio-group {
        padding: 28px !important;
        margin: 20px 0 !important;
        border-radius: 24px !important;
    }
}

@media (min-width: 1024px) {
    .gr-group,
    .gradio-group {
        padding: 32px !important;
        margin: 25px 0 !important;
    }
}

/* Interactive Card Hover Effects */
.gr-group:hover,
.gradio-group:hover {
    transform: translateY(-6px) scale(1.02) !important;
    box-shadow: 0 15px 50px var(--hover-shadow) !important;
    background: var(--card-bg-hover) !important;
    border-color: var(--accent-blue) !important;
}

.gr-group:hover::before,
.gradio-group:hover::before {
    opacity: 1 !important;
}

.gr-group:hover::after,
.gradio-group:hover::after {
    left: 100% !important;
}

/* Medical Icon Animations */
.gr-group:nth-child(1) { animation-delay: 0.1s; }
.gr-group:nth-child(2) { animation-delay: 0.2s; }
.gr-group:nth-child(3) { animation-delay: 0.3s; }
.gr-group:nth-child(4) { animation-delay: 0.4s; }

.gradio-group:nth-child(1) { animation-delay: 0.1s; }
.gradio-group:nth-child(2) { animation-delay: 0.2s; }
.gradio-group:nth-child(3) { animation-delay: 0.3s; }
.gradio-group:nth-child(4) { animation-delay: 0.4s; }

/* Professional Responsive Input Fields */
.gr-textbox,
.gr-audio,
.gr-image {
    background: var(--white) !important;
    border: 2px solid var(--border-color) !important;
    border-radius: 16px !important;
    color: var(--text-primary) !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    box-shadow: 0 4px 16px rgba(21, 101, 192, 0.08) !important;
    width: 100% !important;
    box-sizing: border-box !important;
}

/* Mobile Input Optimization */
@media (max-width: 767px) {
    .gr-textbox,
    .gr-audio,
    .gr-image {
        font-size: 16px !important; /* Prevents zoom on iOS */
        padding: 14px !important;
    }
}

.gr-textbox:focus-within,
.gr-audio:focus-within,
.gr-image:focus-within {
    border-color: var(--primary-blue) !important;
    box-shadow: 0 0 0 4px rgba(21, 101, 192, 0.15), 0 8px 24px rgba(21, 101, 192, 0.12) !important;
    transform: translateY(-2px) !important;
}

/* Professional Responsive Typography */
.gr-textbox label,
.gr-audio label,
.gr-image label {
    color: var(--text-secondary) !important;
    font-weight: 600 !important;
    font-size: 15px !important;
    margin-bottom: 10px !important;
    line-height: 1.4 !important;
}

/* Responsive Typography */
@media (min-width: 768px) {
    .gr-textbox label,
    .gr-audio label,
    .gr-image label {
        font-size: 14px !important;
        margin-bottom: 8px !important;
    }
}

/* Headings and Text Hierarchy */
h1, h2, h3, h4, h5, h6 {
    color: var(--text-primary) !important;
    line-height: 1.3 !important;
}

h1 { font-size: 1.8em !important; }
h2 { font-size: 1.5em !important; }
h3 { font-size: 1.3em !important; }

@media (min-width: 768px) {
    h1 { font-size: 2em !important; }
    h2 { font-size: 1.7em !important; }
    h3 { font-size: 1.4em !important; }
}

input, textarea {
    border: none !important;
    outline: none !important;
    color: var(--text-primary) !important;
    font-size: 14px !important;
}

/* Professional Responsive Info Banner */
.info-banner {
    background: var(--light-blue) !important;
    border: 2px solid var(--accent-blue) !important;
    border-radius: 16px !important;
    color: var(--text-primary) !important;
    padding: 16px !important;
    margin: 15px 0 !important;
    font-size: 15px !important;
    line-height: 1.5 !important;
}

/* Responsive Info Banner */
@media (min-width: 768px) {
    .info-banner {
        padding: 20px !important;
        margin: 20px 0 !important;
        font-size: 14px !important;
        border-radius: 18px !important;
    }
}
    font-weight: 500 !important;
}

/* Professional Responsive Utilities */
.text-center { text-align: center !important; }
.text-left { text-align: left !important; }
.text-right { text-align: right !important; }

/* Mobile-First Responsive Grid */
.grid {
    display: grid;
    gap: 15px;
    width: 100%;
}

@media (min-width: 768px) {
    .grid {
        gap: 20px;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    }
}

@media (min-width: 1024px) {
    .grid {
        gap: 25px;
        grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
    }
}

/* Responsive Spacing */
.space-y-4 > * + * { margin-top: 16px !important; }
.space-y-6 > * + * { margin-top: 24px !important; }

/* Interactive Medical Elements */
.medical-card-icon {
    display: inline-block;
    font-size: 1.8em;
    margin-right: 10px;
    animation: float 4s ease-in-out infinite;
}

.medical-card-icon:nth-child(odd) {
    animation-delay: 1s;
}

/* Loading Animation for AI Processing */
.ai-processing {
    position: relative;
    overflow: hidden;
}

.ai-processing::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, 
        transparent 0%, 
        rgba(66, 165, 245, 0.2) 50%, 
        transparent 100%);
    animation: shimmer 2s ease-in-out infinite;
}

/* Medical Success Animation */
@keyframes medicalSuccess {
    0% { transform: scale(1); }
    50% { transform: scale(1.1); background-color: rgba(76, 175, 80, 0.1); }
    100% { transform: scale(1); }
}

.success-animation {
    animation: medicalSuccess 0.6s ease-out;
}

/* Heartbeat Animation for Health Monitoring */
.health-monitor {
    animation: heartbeat 1.5s ease-in-out infinite;
}

/* Stethoscope Icon Animation */
.stethoscope-icon {
    display: inline-block;
    animation: float 3s ease-in-out infinite;
    transform-origin: center;
}

/* Medical Cross Rotation */
.medical-cross {
    display: inline-block;
    animation: rotate 8s linear infinite;
}

@keyframes rotate {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
}

/* Prescription Pad Effect */
.prescription-effect {
    background: linear-gradient(135deg, 
        rgba(255, 255, 255, 0.9) 0%, 
        rgba(227, 242, 253, 0.8) 100%);
    border-left: 4px solid var(--primary-blue);
    position: relative;
}

.prescription-effect::before {
    content: '℞';
    position: absolute;
    top: 10px;
    right: 15px;
    color: var(--primary-blue);
    font-size: 1.5em;
    opacity: 0.3;
    animation: pulse 3s ease-in-out infinite;
}

/* Mobile Touch Optimizations */
@media (max-width: 767px) {
    .gradio-container {
        padding: 12px !important;
    }
    
    .gr-group,
    .gradio-group {
        padding: 16px !important;
        margin: 12px 0 !important;
    }
    
    input, textarea {
        font-size: 16px !important; /* Prevents zoom on iOS */
        padding: 12px !important;
    }
    
    .medical-card-icon {
        font-size: 1.5em !important;
        margin-right: 8px !important;
    }
    
    /* Disable complex animations on mobile for performance */
    .medical-icons, .wave-effect, .pattern-bg {
        animation: none !important;
    }
}
}
"""

# -------------------------------------------
# Enhanced UI Interface with Animated Medical Backgrounds and Theme Toggle
# -------------------------------------------
with gr.Blocks(css=custom_css, theme=gr.themes.Default(primary_hue="blue", secondary_hue="blue"), title="🏥 Medical AI Assistant") as demo:
    
    # Clean professional interface - Light theme only
    
    # Interactive Medical Header with Animations
    header_html = gr.HTML("""
        <div class="medical-header" style="
            background: linear-gradient(135deg, rgba(21, 101, 192, 0.95) 0%, rgba(33, 150, 243, 0.9) 100%);
            box-shadow: 0 8px 32px rgba(21, 101, 192, 0.25);
            border-radius: 0 0 28px 28px;
            padding: 25px 20px;
            margin: -15px -15px 25px -15px;
            position: relative;
            overflow: hidden;
            animation: slideDown 0.8s ease-out;
        ">
            <!-- Animated Medical Icons Background -->
            <div class="medical-icons" style="
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                z-index: 1;
                opacity: 0.1;
            ">
                <div class="medical-icon" style="position: absolute; top: 15%; left: 10%; animation: float 6s ease-in-out infinite;">🩺</div>
                <div class="medical-icon" style="position: absolute; top: 25%; right: 15%; animation: float 8s ease-in-out infinite 1s;">💊</div>
                <div class="medical-icon" style="position: absolute; top: 60%; left: 20%; animation: float 7s ease-in-out infinite 2s;">❤️</div>
                <div class="medical-icon" style="position: absolute; top: 70%; right: 25%; animation: float 9s ease-in-out infinite 3s;">🧬</div>
                <div class="medical-icon" style="position: absolute; top: 40%; left: 5%; animation: float 5s ease-in-out infinite 1.5s;">🔬</div>
                <div class="medical-icon" style="position: absolute; top: 30%; right: 5%; animation: float 10s ease-in-out infinite 2.5s;">💉</div>
            </div>
            
            <!-- Animated Wave Effect -->
            <div class="wave-effect" style="
                position: absolute;
                bottom: 0;
                left: 0;
                width: 100%;
                height: 3px;
                background: linear-gradient(90deg, transparent, rgba(255,255,255,0.6), transparent);
                animation: medicalWave 3s ease-in-out infinite;
            "></div>
            
            <div style="position: relative; z-index: 2;">
                <h1 class="medical-title" style='
                    text-align: center; 
                    color: white; 
                    font-size: 1.6em; 
                    font-weight: 700; 
                    margin: 0; 
                    text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
                    line-height: 1.2;
                    animation: fadeInScale 1s ease-out 0.3s both;
                '>
                    🏥 Medical AI Assistant
                </h1>
                <p class="medical-subtitle" style='
                    text-align: center; 
                    color: rgba(255,255,255,0.95); 
                    font-size: 0.95em; 
                    margin: 12px 0 0 0; 
                    text-shadow: 1px 1px 3px rgba(0,0,0,0.2);
                    line-height: 1.4;
                    animation: fadeInUp 1s ease-out 0.6s both;
                '>
                    AI-Powered Medical Analysis • Voice Recognition • Image Diagnosis
                </p>
                
                <!-- Interactive Status Indicator -->
                <div class="status-indicator" style="
                    position: absolute;
                    top: 15px;
                    right: 20px;
                    width: 12px;
                    height: 12px;
                    background: #4caf50;
                    border-radius: 50%;
                    animation: pulse 2s ease-in-out infinite;
                    box-shadow: 0 0 10px rgba(76, 175, 80, 0.5);
                "></div>
            </div>
        </div>
        
        <style>
        @keyframes slideDown {
            from { transform: translateY(-100%); opacity: 0; }
            to { transform: translateY(0); opacity: 1; }
        }
        
        @keyframes fadeInScale {
            from { transform: scale(0.8); opacity: 0; }
            to { transform: scale(1); opacity: 1; }
        }
        
        .medical-header:hover .medical-icon {
            animation-duration: 3s !important;
            transform: scale(1.2) !important;
        }
        
        .medical-title:hover {
            transform: scale(1.05);
            transition: transform 0.3s ease;
        }
        
        @media (min-width: 768px) {
            .medical-header {
                margin: -25px -25px 30px -25px !important;
                padding: 35px 30px !important;
                border-radius: 0 0 32px 32px !important;
            }
            .medical-title {
                font-size: 2em !important;
            }
            .medical-subtitle {
                font-size: 1.1em !important;
            }
        }
        
        @media (min-width: 1200px) {
            .medical-header {
                margin: -30px -30px 35px -30px !important;
                padding: 40px 40px !important;
                border-radius: 0 0 36px 36px !important;
            }
            .medical-title {
                font-size: 2.2em !important;
            }
        }
        </style>
    """)
    
    # Interactive Professional Information Banner
    gr.HTML("""
        <div class="interactive-info-banner" style="
            background: linear-gradient(135deg, rgba(227, 242, 253, 0.8) 0%, rgba(187, 222, 251, 0.6) 100%);
            border: 2px solid rgba(66, 165, 245, 0.3);
            border-radius: 20px;
            padding: 18px 24px;
            margin: 20px 0;
            text-align: center;
            font-size: 15px;
            font-weight: 500;
            position: relative;
            overflow: hidden;
            animation: slideInUp 0.8s ease-out 0.9s both;
            box-shadow: 0 4px 20px rgba(21, 101, 192, 0.1);
        ">
            <!-- Animated Background Pattern -->
            <div class="pattern-bg" style="
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: 
                    radial-gradient(circle at 25% 25%, rgba(66, 165, 245, 0.1) 0%, transparent 50%),
                    radial-gradient(circle at 75% 75%, rgba(33, 150, 243, 0.08) 0%, transparent 50%);
                animation: pulse 4s ease-in-out infinite;
                z-index: 1;
            "></div>
            
            <div style="position: relative; z-index: 2;">
                <span class="pulse-icon" style="
                    display: inline-block;
                    animation: pulse 2s ease-in-out infinite;
                    margin-right: 8px;
                    font-size: 1.2em;
                ">💡</span>
                <strong style="color: var(--primary-blue);">Quick Start:</strong> 
                <span style="color: var(--text-primary);">
                    Record your symptoms, upload a medical image, and receive comprehensive AI-powered medical insights with voice feedback
                </span>
            </div>
            
            <!-- Interactive Dots -->
            <div class="interactive-dots" style="
                position: absolute;
                bottom: 8px;
                right: 15px;
                display: flex;
                gap: 4px;
            ">
                <div style="width: 6px; height: 6px; background: var(--accent-blue); border-radius: 50%; animation: pulse 1.5s ease-in-out infinite;"></div>
                <div style="width: 6px; height: 6px; background: var(--accent-blue); border-radius: 50%; animation: pulse 1.5s ease-in-out infinite 0.5s;"></div>
                <div style="width: 6px; height: 6px; background: var(--accent-blue); border-radius: 50%; animation: pulse 1.5s ease-in-out infinite 1s;"></div>
            </div>
        </div>
        
        <style>
        @keyframes slideInUp {
            from { transform: translateY(30px); opacity: 0; }
            to { transform: translateY(0); opacity: 1; }
        }
        
        .interactive-info-banner:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 25px rgba(21, 101, 192, 0.15);
            transition: all 0.3s ease;
        }
        
        .interactive-info-banner:hover .pulse-icon {
            animation-duration: 1s;
            transform: scale(1.1);
        }
        
        @media (max-width: 767px) {
            .interactive-info-banner {
                font-size: 14px !important;
                text-align: left !important;
                padding: 16px 20px !important;
                border-radius: 16px !important;
            }
            
            .interactive-dots {
                display: none !important;
            }
        }
        </style>
    """)
    
    # Main Interface Layout with Unified Interactive Boxes
    with gr.Row():
        # Left Column - Input Section with Unified Interactive Elements
        with gr.Column(scale=1):
            # Unified Voice Input Box
            with gr.Group(elem_classes=["medical-card"]):
                gr.HTML("""
                    <h3 class="section-header">
                        <span class="medical-icon">🎤</span>Voice Input
                    </h3>
                    <p style="margin-bottom: 15px; font-size: 0.9em; line-height: 1.5; color: var(--text-secondary-light);">
                        Clearly describe your symptoms, pain levels, duration, and any relevant medical history by speaking into the microphone
                    </p>
                """)
                audio_input = gr.Audio(
                    sources=["microphone"], 
                    type="filepath", 
                    label="🎙️ Record Your Medical Symptoms",
                    interactive=True
                )

            # Unified Medical Imaging Box
            with gr.Group(elem_classes=["medical-card"]):
                gr.HTML("""
                    <h3 class="section-header">
                        <span class="medical-icon">📷</span>Medical Imaging
                    </h3>
                    <p style="margin-bottom: 15px; font-size: 0.9em; line-height: 1.5; color: var(--text-secondary-light);">
                        Upload high-quality photos of skin conditions, rashes, wounds, or other visible medical concerns for AI-powered visual analysis
                    </p>
                """)
                
                image_input = gr.File(
                    label="📸 Upload Medical Image for Analysis (JPG, PNG, GIF, WebP - AVIF not supported)",
                    file_types=["image"],
                    file_count="single"
                )
                
                uploaded_image_display = gr.Image(
                    label="📋 Uploaded Medical Image",
                    interactive=False,
                    visible=False
                )

            # Unified Action Buttons Box
            with gr.Group(elem_classes=["medical-card"]):
                gr.HTML("""
                    <h3 class="section-header">
                        <span class="medical-icon">⚡</span>Medical Analysis Actions
                    </h3>
                    <p style="margin-bottom: 15px; font-size: 0.9em; line-height: 1.5; color: var(--text-secondary-light);">
                        Initiate comprehensive AI medical analysis or clear all input fields to start fresh
                    </p>
                """)
                with gr.Row():
                    submit_btn = gr.Button(
                        "🔍 Analyze Medical Condition", 
                        variant="primary",
                        size="lg",
                        scale=2
                    )
                    clear_btn = gr.Button(
                        "🗑️ Clear All Fields", 
                        variant="secondary",
                        size="lg",
                        elem_classes=["clear-btn"],
                        scale=1
                    )

        # Right Column - Output Section with Unified Interactive Elements
        with gr.Column(scale=1):
            # Unified Transcription Output Box
            with gr.Group(elem_classes=["medical-card"]):
                gr.HTML("""
                    <h3 class="section-header">
                        <span class="medical-icon">📝</span>Transcribed Patient Input
                    </h3>
                    <p style="margin-bottom: 15px; font-size: 0.9em; color: var(--text-secondary-light);">
                        Your spoken symptoms converted to text for analysis and medical record documentation
                    </p>
                """)
                symptoms_text = gr.Textbox(
                    label="🗣️ Symptoms Transcription",
                    placeholder="Your spoken symptoms will appear here after recording. The AI will process both audio and text for comprehensive analysis...",
                    lines=3,
                    interactive=False,
                    show_copy_button=True
                )

            # Unified Medical Assessment Box
            with gr.Group(elem_classes=["medical-card"]):
                gr.HTML("""
                    <h3 class="section-header">
                        <span class="medical-icon">🩺</span>AI Medical Assessment
                    </h3>
                    <p style="margin-bottom: 15px; font-size: 0.9em; color: var(--text-secondary-light);">
                        Comprehensive medical analysis with potential conditions, recommendations, and treatment guidance
                    </p>
                """)
                doctor_response = gr.Textbox(
                    label="� AI Doctor",
                    placeholder="Detailed medical analysis, potential diagnoses, and professional recommendations will appear here. Please note this is for educational purposes only...",
                    lines=6,
                    interactive=False,
                    show_copy_button=True
                )

            # Unified Audio Response Box
            with gr.Group(elem_classes=["medical-card"]):
                gr.HTML("""
                    <h3 class="section-header">
                        <span class="medical-icon">🔊</span>Audio Medical Response
                    </h3>
                    <p style="margin-bottom: 15px; font-size: 0.9em; color: var(--text-secondary-light);">
                        Listen to the AI doctor's assessment with natural speech synthesis for comprehensive understanding
                    </p>
                """)
                voice_output = gr.Audio(
                    label="🎵 AI Doctor's Voice Response",
                    interactive=False,
                    show_download_button=True
                )

    # Enhanced Professional Footer with Additional Information
    gr.HTML("""
        <div class="footer">
            <p><strong>⚠️ Important Medical Disclaimer:</strong> This AI assistant provides educational information and preliminary analysis only. It should never replace professional medical consultation, diagnosis, or treatment.</p>
            <p style="margin-top: 12px; font-size: 0.85em; opacity: 0.8;">
                🔒 Privacy Protected • 🌍 Globally Accessible • 🚀 Advanced AI Healthcare Technology • 🎯 Educational Purpose
            </p>
            <p style="margin-top: 8px; font-size: 0.8em; opacity: 0.7;">
                Always consult qualified healthcare professionals for medical advice, diagnosis, and treatment decisions.
            </p>
        </div>
    """)

    # Bind logic - Process text first, then voice
    submit_btn.click(
        fn=process_inputs,
        inputs=[audio_input, image_input],
        outputs=[symptoms_text, doctor_response, uploaded_image_display]
    ).then(
        fn=generate_voice_response,
        inputs=[doctor_response],
        outputs=[voice_output]
    )
    
    # Display uploaded image when file is selected
    image_input.change(
        fn=display_uploaded_image,
        inputs=[image_input],
        outputs=[uploaded_image_display, uploaded_image_display]
    )
    
    clear_btn.click(
        lambda: (None, None, "", "", None, None), 
        inputs=[], 
        outputs=[audio_input, image_input, symptoms_text, doctor_response, voice_output, uploaded_image_display]
    )
    
# Run the app
if __name__ == "__main__":
    # Universal launch configuration for both local and Hugging Face Spaces
    if LOCAL_MODE:
        # Local development configuration
        demo.launch(
            server_name="0.0.0.0",  # Accept connections from any IP
            server_port=None,       # Auto-find available port
            share=True,             # Create public tunnel URL for sharing
            debug=False,            # Clean output for production
            show_error=True,        # Show errors for debugging
            favicon_path=None,      # You can add your icon.png here later
            app_kwargs={"title": "AI Medical Assistant - Professional Healthcare Chatbot"}
        )
    else:
        # Hugging Face Spaces configuration
        demo.launch(
            server_name="0.0.0.0",
            server_port=7860,  # Default port for Hugging Face Spaces
            share=False,  # Not needed on Spaces
            debug=False,
            show_error=True,
            favicon_path=None,
            app_kwargs={"title": "AI Medical Assistant - Professional Healthcare Chatbot"}
        )