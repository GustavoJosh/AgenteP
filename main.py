from ollama import chat
from ollama import ChatResponse
import langchain
from langchain.agents import create_tool_calling_agent

response: ChatResponse = chat(model='llama3.2:1b', messages=[
  {
    'role': 'user',
    'content': 'Send me a 100 word video script about facts from fish that live in the pacific ocean ',
  },
])
print(response['message']['content'])
# or access fields directly from the response object
print(response.message.content)

agent = create_tool_calling_agent(
    
)

