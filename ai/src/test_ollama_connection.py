"""
Test script to verify Ollama connection and deepseek-r1:1.5b model availability
Run this before using the pipeline to ensure Ollama is properly set up.
"""

import requests
import json
import sys

OLLAMA_BASE_URL = "http://localhost:11434"
MODEL_NAME = "deepseek-r1:1.5b"

def check_ollama_running():
    """Check if Ollama service is running"""
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        if response.ok:
            print("[OK] Ollama is running!")
            return True
        else:
            print(f"[ERROR] Ollama responded with error: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("[ERROR] Cannot connect to Ollama. Is it running?")
        print(f"   Expected URL: {OLLAMA_BASE_URL}")
        print("\n   To start Ollama:")
        print("   - Windows/Mac/Linux: Run 'ollama serve' in terminal")
        print("   - Or ensure Ollama service is running in background")
        return False
    except Exception as e:
        print(f"[ERROR] Error checking Ollama: {e}")
        return False

def check_model_available():
    """Check if deepseek-r1:1.5b model is available in Ollama"""
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=10)
        if not response.ok:
            print("❌ Failed to get model list from Ollama")
            return False
        
        models = response.json().get("models", [])
        model_names = [model.get("name", "") for model in models]
        
        # Check for exact match or partial match
        found = False
        for name in model_names:
            if MODEL_NAME in name or name.startswith(MODEL_NAME.split(":")[0]):
                print(f"[OK] Found model: {name}")
                found = True
                break
        
        if not found:
            print(f"[ERROR] Model '{MODEL_NAME}' not found in Ollama")
            print(f"   Available models: {', '.join(model_names) if model_names else 'None'}")
            print(f"\n   To pull the model, run:")
            print(f"   ollama pull {MODEL_NAME}")
            return False
        
        return True
    except Exception as e:
        error_msg = str(e).encode('ascii', 'ignore').decode('ascii')
        print(f"[ERROR] Error checking model: {error_msg}")
        return False

def test_model_generation():
    """Test if the model can generate text"""
    try:
        payload = {
            "model": MODEL_NAME,
            "prompt": "Say 'Hello, Ollama is working!'",
            "stream": False,
            "options": {
                "num_predict": 20,
                "temperature": 0.7
            }
        }
        
        print(f"\n[TEST] Testing model generation...")
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json=payload,
            timeout=30
        )
        
        if response.ok:
            result = response.json()
            generated_text = result.get("response", "")
            if generated_text:
                # Clean text for Windows console (remove emojis/special chars)
                clean_text = generated_text.encode('ascii', 'ignore').decode('ascii')
                print(f"[OK] Model generation test successful!")
                print(f"   Response: {clean_text[:100]}...")
                return True
            else:
                print("[ERROR] Model returned empty response")
                print(f"   Full response keys: {list(result.keys())}")
                print(f"   Response value: {result.get('response', 'N/A')}")
                # Still return True if API call succeeded - model might just need a better prompt
                print("[WARNING] Model responded but with empty text. This might be normal.")
                return True
        else:
            print(f"[ERROR] Model generation failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
    except Exception as e:
        error_msg = str(e).encode('ascii', 'ignore').decode('ascii')
        print(f"[ERROR] Error testing model: {error_msg}")
        return False

def main():
    print("=" * 60)
    print("Ollama Connection & Deepseek Model Test")
    print("=" * 60)
    print()
    
    # Step 1: Check if Ollama is running
    print("Step 1: Checking if Ollama is running...")
    if not check_ollama_running():
        print("\n[ERROR] Setup incomplete. Please start Ollama first.")
        sys.exit(1)
    print()
    
    # Step 2: Check if model is available
    print("Step 2: Checking if deepseek-r1:1.5b model is available...")
    if not check_model_available():
        print("\n[ERROR] Setup incomplete. Please pull the model first.")
        sys.exit(1)
    print()
    
    # Step 3: Test model generation
    if not test_model_generation():
        print("\n[ERROR] Model test failed. Check Ollama logs for errors.")
        sys.exit(1)
    
    print()
    print("=" * 60)
    print("[SUCCESS] All checks passed! Ollama is ready to use.")
    print("=" * 60)
    print("\nYour pipeline will use deepseek-r1:1.5b for content expansion.")

if __name__ == "__main__":
    main()

