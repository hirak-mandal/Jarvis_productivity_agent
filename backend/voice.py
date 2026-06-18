import io
import os
import groq as asyncgroq
from cartesia import AsyncCartesia
from dotenv import load_dotenv
load_dotenv()
groq_api_key=os.getenv("GROQ_API_KEY")

#STT(Speech-To-Text)
async def transcribe_audio(raw_audio_bites:bytes)-> None:
        client=asyncgroq(groq_api_key)
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
async def stream_tokens_to_cartesia_voice(token_stream)-> bytes:
    """
    Accepts an active token generator from chat.py and pipes it
    directly into Cartesia's streaming WebSocket.
    """
    cartesia_api_key = os.getenv("CARTESIA_API_KEY", "PLACEHOLDER_UNTIL_ENV")
    client = AsyncCartesia(api_key=cartesia_api_key)

    # RAM bucket to collect Cartesia's sound replies
    audio_accumulator = io.BytesIO()

    async with client.tts.websocket_connect() as ws:
          ctx=ws.context(
                model_id="sonic_latest",
                voice={"mode": "id", "id": "6ccbfb76-1fc6-48f7-b71d-91ac6298247b"},
                output_format={"container": "raw", "encoding": "pcm_s16le", "sample_rate": 44100}
          )
    # 1. READ FROM CHAT.PY AND PUSH TO CARTESIA
    async for token in token_stream:
        # Send the single word/token immediately, keeping the stream open
        await ctx.push(transcript=token, continue_=True)
            
    # 2. SIGN OFF INPUTS
    # The chat loop finished! Tell Cartesia we are done feeding it words.
    await ctx.push(transcript="", continue_=False)
        
    # 3. CATCH CARTESIA'S SPEECH PACKETS INTO RAM
    async for response in ctx.receive():
        if response.type == "chunk" and response.audio:
            audio_accumulator.write(response.audio)
        elif response.type == "error":
            print(f"Cartesia Error: {response.message}")
                
    # Rewind our RAM bucket and return the whole completed asset to chat.py
    audio_accumulator.seek(0)
    return audio_accumulator.read()
    