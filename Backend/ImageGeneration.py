import asyncio
import requests
import os
from time import sleep
from random import randint

# Function to open images (Windows specific)
def open_images(prompt):
    folder_path = r"Data"
    prompt = prompt.replace(" ", "_")
    
    # Hum ek hi file generate karenge quality wali
    files = [f"{prompt}.jpg"]

    for jpg_file in files:
        image_path = os.path.join(folder_path, jpg_file)
        try:
            if os.path.exists(image_path):
                print(f"Opening image: {image_path}")
                os.startfile(image_path) # Windows me direct open karne ke liye best hai
                sleep(1)
            else:
                print(f"File not found: {image_path}")
        except IOError:
            print(f"Unable to open image: {image_path}")

# --- NEW API LOGIC (Pollinations AI) ---
# Ye API free hai, fast hai, aur key nahi mangti
async def generate_images(prompt: str):
    print(f"Generating image for: {prompt}...")
    
    # Prompt ko URL safe banao
    prompt_formatted = prompt.replace(" ", "%20")
    
    # Pollinations AI URL (Direct Image Generation)
    # Seed add kiya taaki har baar alag image bane
    seed = randint(1, 10000)
    url = f"https://image.pollinations.ai/prompt/{prompt_formatted}?width=1024&height=1024&seed={seed}&nologo=true"

    try:
        # Request bhejo (Sync request is fine here as it's fast)
        response = requests.get(url)
        
        if response.status_code == 200:
            # Folder check
            if not os.path.exists("Data"):
                os.makedirs("Data")
            
            # Save Image
            file_name = f"Data/{prompt.replace(' ', '_')}.jpg"
            with open(file_name, "wb") as f:
                f.write(response.content)
            
            print(f"Image Saved: {file_name}")
            open_images(prompt)
        else:
            print(f"Error: {response.status_code} - Failed to generate.")
            
    except Exception as e:
        print(f"Connection Error: {e}")

# Wrapper Function
def GenerateImages(prompt: str):
    asyncio.run(generate_images(prompt))

# --- Main Listener Loop ---
if __name__ == "__main__":
    print("Image Generation Module Started (Powered by Pollinations AI)...")
    
    # File Checks
    file_path = r"Frontend\Files\ImageGeneration.data"
    if not os.path.exists("Frontend/Files"):
        os.makedirs("Frontend/Files")
    
    if not os.path.exists(file_path):
        with open(file_path, "w") as f:
            f.write("False,False")

    while True:
        try:
            with open(file_path, "r") as f:
                Data = f.read()
            
            if not Data:
                continue
                
            Prompt, Status = Data.split(",")

            if Status.strip() == "True":
                print("Request Received...")
                GenerateImages(prompt=Prompt)
                
                # Reset Status
                with open(file_path, "w") as f:
                    f.write("False,False")
                
                # Video ke hisaab se break hatana hai to hata dena
                # break 
            
            else:
                sleep(1)
        
        except Exception as e:
            # print(f"Error: {e}") # Debugging ke liye uncomment kar sakte ho
            sleep(1)