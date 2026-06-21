import io
import os
import groq as AsyncGroq
from dotenv import load_dotenv
load_dotenv()
groq_api_key=os.getenv("GROQ_API_KEY")

#STT(Speech-To-Text)
async def transcribe_audio(raw_audio_bites:bytes)-> None:
        client=AsyncGroq(groq_api_key)
        #wrapping microphone input into a RAM buffer
        audio_buffer=io.BytesIO(raw_audio_bites)

        # 2. Trick the SDK by giving the buffer a spoofed filename and metadata
        # Format: ("filename.extension", file_like_object, "mime/type")
        audio_file_payload = ("microphone_input.wav", audio_buffer, "audio/wav")

        #Fire it to Groq smoothly from RAM
        transcription=await client.audio.transcriptions.create(
                file=audio_file_payload,
                model="whisper-large-v3"
            )
        return transcription.text

#TTS(Test-To-Speech) --> used Cartesia
"""Async streaming multiple transcripts with continuations."""
async def collect_cartesia_audio(ctx)-> bytes:
    # RAM bucket to collect Cartesia's sound replies
    audio_accumulator = io.BytesIO()
    
    # 3. CATCH CARTESIA'S SPEECH PACKETS INTO RAM
    async for response in ctx.receive():
        if response.type == "chunk" and response.audio:
            audio_accumulator.write(response.audio)
        elif response.type == "error":
            print(f"Cartesia Error: {response.message}")
                
    # Rewind our RAM bucket and return the whole completed asset to chat.py
    audio_accumulator.seek(0)
    return audio_accumulator.read()
    