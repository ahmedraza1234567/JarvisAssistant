import requests
from groq import Groq
from json import load, dump, dumps
import datetime
from dotenv import dotenv_values

# Load environment variables
env_vars = dotenv_values(".env")

# Retrieve keys
Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
GroqAPIKey = env_vars.get("GroqAPIKey")
SerperAPIKey = env_vars.get("SerperAPIKey")

# Initialize Groq client
client = Groq(api_key=GroqAPIKey)

# Define System Prompt
System = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which has real-time up-to-date information from the internet.
*** Provide Answers In a Professional Way, make sure to add full stops, commas, question marks, and use proper grammar.***
*** Just answer the question from the provided data in a professional way. ***"""

# Load Chat Logs
try:
    with open(r"Data\ChatLog.json", "r") as f:
        messages = load(f)
except FileNotFoundError:
    with open(r"Data\ChatLog.json", "w") as f:
        dump([], f)

# --- SERPER.DEV SEARCH FUNCTION (100% Working) ---
def GoogleSearch(query):
    try:
        url = "https://google.serper.dev/search"
        
        payload = dumps({
            "q": query,
            "num": 5  # Number of results
        })
        
        headers = {
            'X-API-KEY': SerperAPIKey,
            'Content-Type': 'application/json'
        }
        
        response = requests.request("POST", url, headers=headers, data=payload)
        
        if response.status_code != 200:
            return "Error: Serper API request failed. Check your API Key."
            
        data = response.json()
        
        # Check if organic results exist
        if 'organic' not in data:
            return "No search results found."
            
        results = data['organic']
        
        Answer = f"The search results for '{query}' are:\n[start]\n"
        
        for result in results:
            title = result.get('title', 'No Title')
            snippet = result.get('snippet', 'No Description')
            link = result.get('link', '#')
            Answer += f"Title: {title}\nDescription: {snippet}\nLink: {link}\n\n"
            
        Answer += "[end]"
        return Answer
        
    except Exception as e:
        print(f"Error details: {e}")
        return "Sorry, I encountered an error while searching."

# Function to clean up the answer
def AnswerModifier(Answer):
    lines = Answer.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    modified_answer = '\n'.join(non_empty_lines)
    return modified_answer

# Initial System ChatBot context
SystemChatBot = [
    {"role": "system", "content": System},
    {"role": "user", "content": "Hi"},
    {"role": "assistant", "content": "Hello, how can I help you?"}
]

# Function to get real-time info
def Information():
    data = ""
    current_date_time = datetime.datetime.now()
    day = current_date_time.strftime("%A")
    date = current_date_time.strftime("%d")
    month = current_date_time.strftime("%B")
    year = current_date_time.strftime("%Y")
    hour = current_date_time.strftime("%H")
    minute = current_date_time.strftime("%M")
    second = current_date_time.strftime("%S")
    data += f"Use This Real-time Information if needed:\n"
    data += f"Day: {day}\nDate: {date}\nMonth: {month}\nYear: {year}\n"
    data += f"Time: {hour} hours, {minute} minutes, {second} seconds.\n"
    return data

# Main Realtime Search Engine Function
def RealtimeSearchEngine(prompt):
    global SystemChatBot, messages
    
    with open(r"Data\ChatLog.json", "r") as f:
        messages = load(f)
    
    messages.append({"role": "user", "content": f"{prompt}"})
    
    #print(f"Searching via Serper for: {prompt}...") # Debug msg
    
    search_results = GoogleSearch(prompt)
    
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile", 
        messages=SystemChatBot + [{"role": "system", "content": search_results}] + [{"role": "system", "content": Information()}] + messages,
        max_tokens=2048,
        temperature=0.7,
        top_p=1,
        stream=True,
        stop=None
    )
    
    Answer = ""
    for chunk in completion:
        if chunk.choices[0].delta.content:
            Answer += chunk.choices[0].delta.content
            
    Answer = Answer.strip().replace("</s>", "")
    messages.append({"role": "assistant", "content": Answer})
    
    with open(r"Data\ChatLog.json", "w") as f:
        dump(messages, f, indent=4)
        
    return AnswerModifier(Answer=Answer)

if __name__ == "__main__":
    while True:
        prompt = input("Enter your query: ")
        print(RealtimeSearchEngine(prompt))