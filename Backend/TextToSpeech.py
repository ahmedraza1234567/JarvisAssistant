import pygame
import random
import asyncio
import edge_tts
import os
from dotenv import dotenv_values

# Load environment variables
env_vars = dotenv_values(".env")
AssistantVoice = env_vars.get("AssistantVoice")

# --- ASYNC FUNCTION TO CONVERT TEXT TO AUDIO ---
async def TextToAudioFile(text) -> None:
    file_path = r"Data\speech.mp3"
    
    if os.path.exists(file_path):
        os.remove(file_path)
    
    # Create the communicate object to generate speech
    # Pitch aur Rate ko adjust kar sakte ho apni pasand ke hisaab se
    communicate = edge_tts.Communicate(text, AssistantVoice, pitch='+5Hz', rate='+13%')
    await communicate.save(r'Data\speech.mp3')

# --- TTS FUNCTION (Handles Playback) ---
def TTS(Text, func=lambda r=None: True):
    while True:
        try:
            # Convert text to audio file asynchronously
            asyncio.run(TextToAudioFile(Text))
            
            # Initialize pygame mixer for audio playback
            pygame.mixer.init()
            
            # Load the generated speech file
            pygame.mixer.music.load(r"Data\speech.mp3")
            pygame.mixer.music.play()
            
            # Loop until the audio is done playing or the function stops
            while pygame.mixer.music.get_busy():
                if func() == False: # Check if the external function returns false
                    break
                pygame.time.Clock().tick(10) # Limit the loop to 10 ticks per second
                
            return True # Return True if the audio played successfully
        
        except Exception as e:
            print(f"Error in TTS: {e}")
            
        finally:
            try:
                # Call the provided function with False to signal the end of TTS
                func(False)
                pygame.mixer.music.stop()
                pygame.mixer.quit()
            except Exception as e:
                print(f"Error in finally block: {e}")

# --- TEXT TO SPEECH (Handles Long Text) ---
def TextToSpeech(Text, func=lambda r=None: True):
    Data = str(Text).split(".")
    
    # List of responses for long text (taaki user bore na ho)
    responses = [
        "The rest of the result has been printed to the chat screen, kindly check it out sir.",
        "The rest of the text is now on the chat screen, sir, please check it.",
        "You can see the rest of the text on the chat screen, sir.",
        "The remaining text is printed, please check it sir.",
        "Sir, you'll find more text on the chat screen for you.",
        "The rest of the answer is now on the chat screen, sir.",
        "Sir, please check the chat screen, the rest of the text is there.",
        "There's more text on the chat screen for you, sir.",
        "Sir, take a look at the chat screen for additional text.",
        "You'll find the complete answer on the chat screen, sir.",
        "Sir, please check the chat screen for the rest of the text.",
        "I've printed the rest of the text on the chat screen, sir.",
        "There's more to see on the chat screen, sir, please check.",
        "Sir, the rest of the text is on the chat screen, check it out.",
        "Sir, the rest of the text is on the chat screen, please check it."
    ]

    # Agar text bohot lamba hai (more than 4 sentences and 250 chars)
    if len(Data) > 4 and len(Text) >= 250:
        TTS(" ".join(Text.split(".")[0:2]) + ". " + random.choice(responses), func)
    
    # Otherwise, play the whole text
    else:
        TTS(Text, func)

# --- MAIN EXECUTION LOOP (Testing) ---
if __name__ == "__main__":
    while True:
        Text = input("Enter the text: ")
        TextToSpeech(Text)