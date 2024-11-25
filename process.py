import azure.cognitiveservices.speech as speechsdk
import requests
import openai

# Azure Configuration
SPEECH_KEY = "FUCNqGyw8ARBlooiKvvILTBbnIt5Wj0WDXdoBuZY9U0mcPOatXOsJQQJ99AKACBsN54XJ3w3AAAYACOGbaHb"
SPEECH_REGION = "canadacentral"
TRANSLATOR_KEY = "FqBzn2GGCf5iaLe1lxlJ9kwv9yBMvGnAD28Q8Z8FsMlUpUgGwRvUJQQJ99AKACBsN54XJ3w3AAAbACOGNoTF"
TRANSLATOR_ENDPOINT = "https://api.cognitive.microsofttranslator.com"
OPENAI_KEY = "3hGvPadu81ijb4fdtNG4owhjvfxVCzrOos7m9l40JBu8431vUzB8JQQJ99AKACBsN54XJ3w3AAABACOGnQmW"
OPENAI_ENDPOINT = "https://openai-wth-genai.openai.azure.com/"
OPENAI_DEPLOYMENT_NAME = "gpt-35-turbo" 

# Speech-to-Text (STT)
def speech_to_text(audio_file):
    speech_config = speechsdk.SpeechConfig(subscription=SPEECH_KEY, region=SPEECH_REGION)
    audio_config = speechsdk.audio.AudioConfig(filename=audio_file)
    recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

    result = recognizer.recognize_once()
    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        return result.text
    else:
        raise Exception(f"Speech recognition failed: {result.reason}")

# Language Detection and Translation
def detect_language_and_translate(text, to_lang="en"):
    path = "/translate?api-version=3.0"
    params = {"to": to_lang}
    url = TRANSLATOR_ENDPOINT + path
    headers = {
        "Ocp-Apim-Subscription-Key": TRANSLATOR_KEY,
        "Content-Type": "application/json"
    }
    body = [{"text": text}]

    response = requests.post(url, headers=headers, json=body)
    response.raise_for_status()
    data = response.json()
    detected_language = data[0]["detectedLanguage"]["language"]
    translated_text = data[0]["translations"][0]["text"]

    return detected_language, translated_text

# Generative AI Response using Azure OpenAI
def generate_ai_response(prompt):
    openai.api_type = "azure"
    openai.api_key = OPENAI_KEY
    openai.api_base = OPENAI_ENDPOINT
    openai.api_version = "2023-03-15-preview"

    response = openai.ChatCompletion.create(
        engine=OPENAI_DEPLOYMENT_NAME,
        messages=[{"role": "system", "content": "You are a helpful customer service agent."},
                  {"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=200
    )
    return response['choices'][0]['message']['content']

# Text-to-Speech (TTS)
def text_to_speech(text, language="en-US", output_file="response.wav"):
    speech_config = speechsdk.SpeechConfig(subscription=SPEECH_KEY, region=SPEECH_REGION)
    speech_config.speech_synthesis_language = language
    audio_config = speechsdk.audio.AudioOutputConfig(filename=output_file)
    synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

    synthesizer.speak_text_async(text).get()
    return output_file

# Full Workflow
def handle_customer_service(audio_file):
    # Step 1: Convert speech to text
    customer_text = speech_to_text(audio_file)
    print(f"Customer Text: {customer_text}")

    # Step 2: Detect language and translate to English
    detected_language, translated_text = detect_language_and_translate(customer_text)
    print(f"Detected Language: {detected_language}")
    print(f"Translated Text (to English): {translated_text}")

    # Step 3: Generate AI response in English
    ai_response = generate_ai_response(translated_text)
    print(f"AI Response: {ai_response}")

    # Step 4: Translate AI response back to the customer's language
    _, translated_response = detect_language_and_translate(ai_response, to_lang=detected_language)
    print(f"Translated Response (to Customer's Language): {translated_response}")

    # Step 5: Convert response text to speech
    response_audio = text_to_speech(translated_response, language="hi-IN" if detected_language == "hi" else "es-ES")
    print(f"Response audio saved at: {response_audio}")

    return response_audio