# 🩺 AI Medical Voicebot: Multimodal Symptom Analysis with Voice & Vision

An interactive AI-powered medical assistant that listens to your symptoms, analyzes uploaded images of conditions (e.g., skin problems), and responds like a real doctor — both in **text** and **realistic voice**.

---

## 🚀 Demo

▶️ [Live App on Gradio](Yet to deploy) 

---

## 🎯 Key Features

- 🎤 **Speech Recognition (STT)**: Transcribes patient symptoms from voice using [Whisper-v3].
- 🧠 **Multimodal AI Diagnosis**: Combines voice + medical image input and provides a diagnosis via [GROQ LLaMA-4].
- 🗣️ **Realistic Doctor Voice (TTS)**: Uses [ElevenLabs] to convert doctor responses to natural-sounding speech.
- 🖼️ **Image Understanding**: Accepts patient-uploaded images for analysis (e.g., rashes, acne).
- 🌐 **Fully Interactive UI**: Built with [Gradio], designed for accessibility and ease of use.

---

## 🧪 Example Workflow

1. User speaks their symptoms.
2. (Optional) User uploads an image of a skin condition.
3. AI transcribes the speech, processes the image, and generates a diagnosis.
4. Doctor’s response is shown in text and played back via voice.

---

## 🧰 Tech Stack

| Module           | Tool / API                    |
|------------------|-------------------------------|
| Frontend         | [Gradio Blocks]               |
| Speech-to-Text   | Whisper Large v3 via [GROQ]   |
| Image+Text AI    | LLaMA-4 via [GROQ]            |
| Text-to-Speech   | [ElevenLabs] TTS API          |
| Audio Handling   | `pydub`, `SpeechRecognition`  |
| Env Management   | `python-dotenv`               |

---

## 📁 Project Structure

```bash
AI_Medical_Voicebot/
│
├── Gradio_final_app.py         # Main Gradio UI
├── voice_of_the_patient.py     # Voice recording + transcription
├── voice_of_the_doctor.py      # TTS logic (ElevenLabs & gTTS)
├── brain_of_the_doctor.py      # Multimodal AI diagnosis
├── requirements.txt            # Python dependencies
├── .env                        # API keys (GROQ, ElevenLabs)
└── README.md                   # You're here!
```
---

## 💡 Future Enhancements

- Medical history memory (LLM memory)
- Integration with real medical databases (e.g., ICD codes)
- Fine-tuning for pediatric, dermatology, and mental health diagnosis
- Hindi/Multilingual voice support

---

## 🤝 Credits

- **GROQ** for lightning-fast LLaMA inference
- **ElevenLabs** for human-like TTS
- **OpenAI Whisper** for STT
- **Gradio** for rapid prototyping of ML apps

---

## 🧠 Disclaimer

This tool is for **educational and experimental** purposes only. It is **not intended for real medical use**. Always consult a licensed physician for actual health concerns.
