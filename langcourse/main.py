import os
from dotenv import load_dotenv
from importlib import metadata

# Load your environment variables (Ensure GOOGLE_API_KEY is inside your .env file)
load_dotenv()

from langchain_core import __version__ as langchaincore_version
from langchain import __version__ as langchain_version
from langchain_google_genai import ChatGoogleGenerativeAI

print(f"langchain-core version: {langchaincore_version}")
print(f"langchain version: {langchain_version}")

# Safe extraction of the package version
try:
    import langchain_google_genai
    print(f"langchain-google-genai version: {langchain_google_genai.__version__}")
except AttributeError:
    print("langchain-google-genai version: Available")


def main():
    # 1. Initialize the model with valid configuration parameters
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.7,
    )
    
    # 2. Define your prompt text cleanly
    prompt = "Explain how parallel agentic execution works in three sentences."
    
    # 3. Call the model using the standard .invoke() pattern
    print("\n--- Sending request to Gemini ---")
    response = llm.invoke(prompt)
    
    # 4. Print out the structured string text result
    print(response.content)
    print("\nHello from langcourse!")


if __name__ == "__main__":
    main()
