import os
from typing import List, Optional
from dotenv import load_dotenv
from langchain_ollama import OllamaLLM
from langchain.chains import LLMChain
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferMemory

# Load environment variables
load_dotenv()

# Initialize Ollama
try:
    # Try different model options if available
    available_models = ["llama3.2:1b", "llama3:8b", "mistral:7b"]
    model_error = None
    
    for model in available_models:
        try:
            print(f"Trying to load model: {model}")
            llm = OllamaLLM(model=model)
            model_error = None
            print(f"Successfully loaded model: {model}")
            break
        except Exception as e:
            model_error = str(e)
            print(f"Failed to load model {model}: {e}")
    
    if model_error is not None:
        raise Exception(f"Could not load any models: {model_error}")
        
except Exception as e:
    print(f"Error initializing Ollama: {e}")
    exit(1)

# Set up memory
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

# Create a simple prompt template
prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a helpful AI assistant. You can answer questions, provide information, and have conversations.
    
Some things you can help with:
- General knowledge questions
- Writing and creative tasks
- Learning about specific topics
- Providing helpful advice

If you don't know something, just say so."""),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{question}")
])

# Create a simple chain
chain = LLMChain(
    llm=llm,
    prompt=prompt,
    memory=memory,
    verbose=True
)

# Function to process user messages
def process_message(user_message: str):
    """Process a message from the user and return a response."""
    try:
        print(f"Processing message: {user_message}")
        result = chain.invoke({"question": user_message})
        return result.get("text", "No response generated")
    except Exception as e:
        error_msg = f"Error processing request: {str(e)}"
        print(error_msg)
        return error_msg

# Example test
if __name__ == "__main__":
    print("Starting basic chatbot. Type 'exit' to quit.")
    print("This is a simple chatbot using your Ollama model.")
    print("The chatbot will remember your conversation history.")
    print()
    
    while True:
        query = input("\nYou: ")
        
        if query.lower() in ['exit', 'quit', 'bye']:
            print("Goodbye!")
            break
            
        print("\nProcessing...")
        response = process_message(query)
        print(f"\nAI: {response}")

"""
FUTURE DEVELOPMENT GUIDE

=== ADDING TOOLS ===
This simplified version doesn't include tools like search and Wikipedia.
To add them later, you'll need to:

1. Create a separate file for your tools:
   # tools.py
   # from langchain_community.utilities import WikipediaAPIWrapper
   # from langchain_community.utilities import DuckDuckGoSearchAPIWrapper
   # 
   # Define your tool functions here

2. Update your prompt to include instructions about tools:
   # system_message = \"\"\"You are a helpful AI assistant with access to tools.
   # When you need to look up information, say [USING TOOL: tool_name] before using the tool,
   # then say what you're searching for, then say [TOOL RESPONSE: response] with the result.
   # \"\"\"

3. Create a function to handle tool usage manually:
   # def handle_tools(message):
   #     if "[USING TOOL: search]" in message:
   #         # Extract search query and call search tool
   #         # Replace the placeholder with actual search results
   #     return message

=== VIDEO GENERATION INTEGRATION ===
To integrate video generation:

1. Create a separate videogen.py file with your video generation code:
   # from videogen import generate_video

2. Update the process_message function to handle video generation:
   # def process_message(user_message: str):
   #     if "video" in user_message.lower():
   #         # Add video instruction to the prompt
   #         video_message = f"The user wants a video about: {user_message}. Create a script with a title and content."
   #         result = chain.invoke({"question": video_message})
   #         # Parse result and generate video
   #         video_url = generate_video(result.get("text"))
   #         return f"Video generated: {video_url}\n\nScript: {result.get('text')}"
   #     else:
   #         # Process as regular chat
   #         result = chain.invoke({"question": user_message})
   #         return result.get("text", "No response generated")

=== MESSAGING PLATFORM INTEGRATION ===
To integrate with Telegram:

1. Create a separate messaging.py file:
   # pip install python-telegram-bot
   # from telegram.ext import Application, CommandHandler, MessageHandler, filters
   # from main import process_message

2. Create handlers that use your process_message function:
   # async def handle_message(update, context):
   #     user_text = update.message.text
   #     await update.message.chat.send_action(action="typing")
   #     response = process_message(user_text)
   #     await update.message.reply_text(response)
"""