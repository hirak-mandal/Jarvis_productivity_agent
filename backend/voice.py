import tempfile
import os
import groq as asyncgroq
from dotenv import load_dotenv
load_dotenv()
api_key=os.getenv("GROQ_API_KEY")
client=asyncgroq(api_key)
#STT(Speech-To-Text)
async def transcribe_audio(binary_data:bytes)-> str:
    #creating a temperary file for the microphone to text
    with tempfile.NamedTemporaryFile(suffix=".wav",delete=False) as temp:
        #write the temporary bites in the audio file
        temp.write(binary_data)
        temp_file_path=temp.name

    try:
        #sending the temporary audio file to the Whisper AI model to convert speech to text
        with open(temp_file_path,"rb") as audio_file:
            transcription=await client.audio.transcriptions.create(
                file=(os.path.basename(temp_file_path),audio_file.read()),
                model="whisper-large-v3",
                response_format="text"
            )
        return transcription
    finally:
        #erasing the temporary file from harddrive
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)