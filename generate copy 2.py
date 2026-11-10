import os
import json
import subprocess
from dotenv import load_dotenv
from pydantic import BaseModel
from google import genai
from google.genai import types
from elevenlabs.client import ElevenLabs
from upload import upload_short

# Load environment variables from .env
load_dotenv()

class QuizQuestion(BaseModel):
    question: str
    options: list[str]
    correct_answer: str
    explanation: str

def generate_quiz() -> QuizQuestion:
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    prompt = (
        "Generate a fascinating, interesting yet simple multiple-choice tech related quiz question. It can be about everyday gadgets or history of gadgets, or tech news about new releases or trending news. The question should focus on popular technology, internet culture, consumer electronics, or computing history that general internet users and tech enthusiasts would recognize and have a fair chance at guessing (avoid overly obscure coding syntax, deep compiler theory, or niche library internals)"
        "Provide exactly 4 options, the correct answer (matching one of the options exactly), and a short 1-sentence explanation."
    )
    
    try:
        print("🤖 Generating tech quiz question with Gemini (gemini-3.8-flash)...")
        response = client.models.generate_content(
            model='gemini-3.8-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=QuizQuestion,
            ),
        )
        return response.parsed
    except Exception as e:
        print(f"⚠️ API quota/limit hit ({e}). Falling back to local offline trivia question!")
        return QuizQuestion(
            question="What does the 'virtual DOM' in React primarily optimize?",
            options=[
                "Direct database queries",
                "Efficient UI diffing and DOM batching",
                "Network packet routing",
                "CSS style compilation speed"
            ],
            correct_answer="Efficient UI diffing and DOM batching",
            explanation="React uses the virtual DOM to calculate minimal DOM mutations before batch-updating the browser."
        )

def generate_audio_11labs(text: str, output_path: str):
    print(f"🎙️ Generating voiceover -> {output_path}...")
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        raise ValueError("ELEVENLABS_API_KEY not found in environment variables.")
    
    client = ElevenLabs(api_key=api_key)
    
    audio_stream = client.text_to_speech.convert(
        voice_id="fUjY9K2nAIwlALOwSiwc",
        model_id="eleven_multilingual_v2",
        text=text,
        output_format="mp3_44100_128"
    )
    
    with open(output_path, "wb") as f:
        for chunk in audio_stream:
            f.write(chunk)
    print(f"✅ Audio saved to {output_path}")

from google.cloud import texttospeech

def generate_audio_old(text: str, output_path: str):
    print(f"🎙️ Generating Google Cloud voiceover -> {output_path}...")
    client = texttospeech.TextToSpeechClient()

    input_text = texttospeech.SynthesisInput(text=text)
    
    # Choose your preferred voice (e.g., en-US-Neural2-D for male or en-US-Neural2-F for female)
    voice = texttospeech.VoiceSelectionParams(
    language_code="en-US",
    name="en-US-Studio-Q", # Much more realistic and dynamic
    ssml_gender=texttospeech.SsmlVoiceGender.MALE
    )
    
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )

    response = client.synthesize_speech(
        input=input_text, voice=voice, audio_config=audio_config
    )

    with open(output_path, "wb") as out:
        out.write(response.audio_content)
    print(f"✅ Audio saved to {output_path}")

from google.cloud import texttospeech
import json

def generate_audio(json_path: str, output_path: str):
    print(f"🎙️ Generating Studio-tier Google Cloud voiceover -> {output_path}...")
    
    # Load quiz data to format SSML with pauses
    with open(json_path, "r") as f:
        data = json.load(f)

    question = data["question"]
    options = data["options"]
    
    # Construct SSML string with built-in pauses after each choice
    ssml_text = f"<speak>{question}<break time=\"800ms\"/>"
    
    for i, option in enumerate(options):
        option_letter = chr(65 + i) # A, B, C, D
        ssml_text += f"Option {option_letter}: {option}. <break time=\"1s\"/>"
        
    ssml_text += "5 seconds to guess. Let's go!</speak>"

    client = texttospeech.TextToSpeechClient()

    input_text = texttospeech.SynthesisInput(ssml=ssml_text)
    
    # Premium Studio-tier female voice for maximum realism
    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US",
        name="en-US-Studio-O", 
        ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
    )
    
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3,
        speaking_rate=0.96, # Natural, relaxed cadence
    )

    response = client.synthesize_speech(
        input=input_text, voice=voice, audio_config=audio_config
    )

    with open(output_path, "wb") as out:
        out.write(response.audio_content)
    print(f"✅ Audio saved to {output_path}")

def trigger_remotion_render():
    print("🎬 Triggering Remotion render...")
    original_dir = os.getcwd()
    os.chdir("remotion_src")
    
    try:
        cmd = ["npx", "remotion", "render", "Root", "out/tech-quiz.mp4"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ Remotion render failed:")
            print(result.stderr)
            return False
        else:
            print("✨ Video rendered successfully at remotion_src/out/tech-quiz.mp4!")
            return True
    finally:
        os.chdir(original_dir)

if __name__ == "__main__":
    os.makedirs("remotion_src/public", exist_ok=True)
    os.makedirs("remotion_src/out", exist_ok=True)

    # 1. Generate Quiz Content
    quiz_data = generate_quiz()
    print(f"\n💡 Question: {quiz_data.question}")
    for i, opt in enumerate(quiz_data.options):
        print(f"   {i+1}. {opt}")
    print(f"🎯 Correct: {quiz_data.correct_answer}\n")

    # Save structured JSON data for Remotion
    json_path = "remotion_src/public/quiz_data.json"
    with open(json_path, "w") as f:
        f.write(quiz_data.model_dump_json(indent=2))

    # 2. Generate Voiceover 1: Question and Choices
    question_script = f"Tech Quiz time! {quiz_data.question} Is it: " + ", or ".join(quiz_data.options) + "?"
    generate_audio(question_script, "remotion_src/public/voiceover.mp3")

    # 3. Generate Voiceover 2: Answer and Explanation
    answer_script = f"The correct answer is {quiz_data.correct_answer}. {quiz_data.explanation}"
    generate_audio(answer_script, "remotion_src/public/answer_audio.mp3")

    # 4. Render Final Video via Remotion CLI
    rendered = trigger_remotion_render()

    # 5. Automatically Upload to YouTube Shorts
    if rendered:
        print("\n🚀 Handing off to YouTube Upload pipeline...")
        upload_short(
            video_path="remotion_src/out/tech-quiz.mp4",
            title=quiz_data.question[:70], # Keep title concise for Shorts
            description=f"Can you guess the right answer? Explanation: {quiz_data.explanation}",
            tags=["Coding", "TechTrivia", "SoftwareEngineering", "ProgrammingQuiz"]
        )
