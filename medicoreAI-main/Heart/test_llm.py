import asyncio
import os
import sys

# Ensure the project root is in sys.path
# Since this script is in the root, we can just use the current directory
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from services.llm_service import llm_service
    from dotenv import load_dotenv
    import config
except ImportError as e:
    print(f"Import Error: {e}")
    print("Please ensure you are running this script from the project root and dependencies are installed.")
    sys.exit(1)

# Load environment variables
load_dotenv()

async def test_llm_connection():
    print("--- Testing Featherless AI Connection ---")
    
    # Check config values derived from .env
    api_key = config.FEATHERLESS_API_KEY
    model = config.FEATHERLESS_MODEL
    base_url = config.FEATHERLESS_BASE_URL
    
    if not api_key:
        print("ERROR: FEATHERLESS_API_KEY not found in .env or config")
        return

    print(f"Model: {model}")
    print(f"Base URL: {base_url}")
    
    url = f"{base_url.rstrip('/')}/chat/completions"
    print(f"Full Endpoint URL: {url}")
    
    test_message = "Hello JARVIS, are you there? Provide a brief medical disclaimer and confirm your status."
    print(f"User: {test_message}")
    print("Waiting for response...")
    
    try:
        # Debug the actual call
        headers = {
            "Authorization": f"Bearer {api_key[:5]}...{api_key[-5:]}",
            "Content-Type": "application/json"
        }
        print(f"Request Headers (Sanitized): {headers}")
        
        response = await llm_service.get_jarvis_response(test_message)
        
        if response:
            print(f"\nJARVIS: {response}")
            print("\nSUCCESS: Connection verified!")
        else:
            print("\nFAILED: No response from LLM (potentially 404 or other error).")
    except Exception as e:
        print(f"\nERROR: An unexpected error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(test_llm_connection())
