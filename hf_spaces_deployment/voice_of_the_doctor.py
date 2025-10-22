import os
import tempfile
from gtts import gTTS
from dotenv import load_dotenv
from elevenlabs import ElevenLabs
import subprocess
import platform

load_dotenv()

#Step1a: Setup Text to Speech–TTS–model with gTTS

def text_to_speech_with_gtts_old(input_text, output_filepath):
    language="en"

    audioobj= gTTS(
        text=input_text,
        lang=language,
        slow=False
    )
    audioobj.save(output_filepath)


input_text="Hi this is Ai with Hassan!"
#text_to_speech_with_gtts_old(input_text=input_text, output_filepath="gtts_testing.mp3")

#Step1b: Setup Text to Speech–TTS–model with ElevenLabs

ELEVENLABS_API_KEY=os.environ.get("ELEVENLABS_API_KEY")
client=ElevenLabs(api_key=ELEVENLABS_API_KEY)
def text_to_speech_with_elevenlabs_old(input_text, output_filepath):
 
    audio=client.text_to_speech.convert(
        text= input_text,
        voice_id = "O7p2vmz2iEYgMXxkbsif",
        output_format= "mp3_22050_32",
        model_id = "eleven_turbo_v2"
    )
    with open(output_filepath, "wb") as f:
        for chunk in audio:
            f.write(chunk)

#text_to_speech_with_elevenlabs_old(input_text, output_filepath="elevenlabs_testing.mp3") 

#Step2: Use Model for Text output to Voice


def text_to_speech_with_gtts(input_text, output_filepath):
    language="en"

    audioobj= gTTS(
        text=input_text,
        lang=language,
        slow=False
    )
    audioobj.save(output_filepath)
    os_name = platform.system()
    try:
        if os_name == "Darwin":  # macOS
            subprocess.run(['afplay', output_filepath])
        elif os_name == "Windows":  # Windows
            subprocess.run(['powershell', '-c', f'(New-Object Media.SoundPlayer "{output_filepath}").PlaySync();'])
        elif os_name == "Linux":  # Linux
            subprocess.run(['aplay', output_filepath])  # Alternative: use 'mpg123' or 'ffplay'
        else:
            raise OSError("Unsupported operating system")
    except Exception as e:
        # Silent error handling - no console output
        pass


input_text="Hi this is Ai with Hassan, autoplay testing!"
#text_to_speech_with_gtts(input_text=input_text, output_filepath="gtts_testing_autoplay.mp3")


def text_to_speech_with_elevenlabs(input_text, output_filepath):
    audio=client.text_to_speech.convert(
        text= input_text,
        voice_id = "O7p2vmz2iEYgMXxkbsif",
        output_format= "mp3_22050_32",
        model_id = "eleven_turbo_v2"
    )
    with open(output_filepath, "wb") as f:
        for chunk in audio:
            f.write(chunk)
    os_name = platform.system()
    try:
        if os_name == "Darwin":  # macOS
            subprocess.run(['afplay', output_filepath])
        elif os_name == "Windows":  # Windows
            subprocess.run(['powershell', '-c', f'(New-Object Media.SoundPlayer "{output_filepath}").PlaySync();'])
        elif os_name == "Linux":  # Linux
            subprocess.run(['aplay', output_filepath])  # Alternative: use 'mpg123' or 'ffplay'
        else:
            raise OSError("Unsupported operating system")
    except Exception as e:
        # Silent error handling - no console output  
        pass
    return output_filepath

def generate_audio(text_response):
    """
    Main function to generate audio from text response
    Compatible with Hugging Face Spaces
    """
    try:
        if not text_response or text_response.strip() == "":
            return None
        
        # Check if ElevenLabs API key is available
        ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY")
        if not ELEVENLABS_API_KEY:
            print("ElevenLabs API key not found, falling back to gTTS")
            # Fallback to gTTS
            try:
                import tempfile
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
                output_path = temp_file.name
                temp_file.close()
                
                tts = gTTS(text=text_response, lang='en', slow=False)
                tts.save(output_path)
                return output_path
            except Exception as gtts_error:
                print(f"gTTS fallback failed: {gtts_error}")
                return None
        
        # Create temporary file for audio output
        import tempfile
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        output_path = temp_file.name
        temp_file.close()
        
        # Generate audio using ElevenLabs (without autoplay for Spaces)
        client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
        audio = client.text_to_speech.convert(
            text=text_response,
            voice_id="O7p2vmz2iEYgMXxkbsif",
            output_format="mp3_22050_32",
            model_id="eleven_turbo_v2"
        )
        
        # Save audio to file
        with open(output_path, "wb") as f:
            for chunk in audio:
                f.write(chunk)
        
        return output_path
        
    except Exception as e:
        print(f"Audio generation error: {e}")  # For debugging in Spaces
        # Final fallback to gTTS
        try:
            import tempfile
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
            output_path = temp_file.name
            temp_file.close()
            
            tts = gTTS(text=text_response, lang='en', slow=False)
            tts.save(output_path)
            return output_path
        except Exception as final_error:
            print(f"Final fallback failed: {final_error}")
            return None

#text_to_speech_with_elevenlabs(input_text, output_filepath="elevenlabs_testing_autoplay.mp3")