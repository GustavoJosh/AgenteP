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

# Set up memory with user IDs to handle multiple conversations
conversations = {}

# Create a simple prompt template
base_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a helpful AI assistant available through Telegram. You can answer questions, provide information, and have conversations.
    
Some things you can help with:
- General knowledge questions
- Writing and creative tasks
- Learning about specific topics
- Providing helpful advice

If you don't know something, just say so. Keep your responses concise and friendly."""),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{question}")
])

# Function to get or create a conversation chain for a user
def get_user_chain(user_id=None):
    """Get or create a conversation chain for a specific user."""
    if user_id is None:
        user_id = "default"
        
    if user_id not in conversations:
        # Create new memory and chain for this user
        memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        chain = LLMChain(
            llm=llm,
            prompt=base_prompt,
            memory=memory,
            verbose=False
        )
        conversations[user_id] = chain
        
    return conversations[user_id]

# Function to process user messages
def process_message(user_message: str, user_id=None):
    """Process a message from the user and return a response."""
    try:
        print(f"Processing message from user {user_id}: {user_message}")
        
        # Get the chain for this user
        chain = get_user_chain(user_id)
        
        # Invoke the chain with the user's message
        result = chain.invoke({"question": user_message})
        return result.get("text", "No response generated")
    except Exception as e:
        error_msg = f"Error processing request: {str(e)}"
        print(error_msg)
        return error_msg

# Example test for local CLI usage
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