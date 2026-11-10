import os
import json
import subprocess
from dotenv import load_dotenv
from pydantic import BaseModel
from google import genai
from google.genai import types
from google.cloud import texttospeech
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
        "Generate a fascinating, interesting yet simple multiple-choice tech related quiz question. It can be about everyday gadgets or history of gadgets, or tech news about new releases or trending news. The question should focus on popular technology, internet culture, consumer electronics, or computing history that general internet users and tech enthusiasts would recognize and have a fair chance at guessing (avoid overly obscure coding syntax, deep compiler theory, or niche library internals). "
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

def generate_audio(input_data, output_path: str):
    print(f"🎙️ Generating Studio-tier Google Cloud voiceover -> {output_path}...")
    
    # Check if input_data is a file path (for SSML formatting) or a direct string script
    if isinstance(input_data, str) and os.path.exists(input_data):
        with open(input_data, "r") as f:
            data = json.load(f)
        question = data["question"]
        options = data["options"]
        
        # Construct SSML string with punctuated inflection
        ssml_text = f"<speak>Quick Quiz? <break time=\"500ms\"/> {question}<break time=\"800ms\"/>"
        for i, option in enumerate(options):
            option_letter = chr(65 + i) # A, B, C, D
            ssml_text += f"{option_letter}: {option}. <break time=\"1s\"/>"
        ssml_text += "</speak>"
        input_text = texttospeech.SynthesisInput(ssml=ssml_text)
    else:
        # Fallback for plain text string inputs (like answer_audio)
        input_text = texttospeech.SynthesisInput(text=str(input_data))

    client = texttospeech.TextToSpeechClient()
    
    # Premium Studio-tier female voice for maximum realism
    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US",
        name="en-US-Studio-O", 
        ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
    )
    
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3,
        speaking_rate=0.96, # Natural, relaxed cadence
	pitch=1.9
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

    # 2. Generate Voiceover 1: Question and Choices (using JSON file path to trigger SSML pauses)
    generate_audio(json_path, "remotion_src/public/voiceover.mp3")

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