"""
List available Gemini models from Google's API
Run this to see what models are actually available for your API key
"""

import os
import requests
import json
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path, override=False)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

if not GEMINI_API_KEY:
    print("❌ ERROR: GEMINI_API_KEY not found in .env file")
    print("\nPlease add your Gemini API key to ai/.env file:")
    print("GEMINI_API_KEY=your_api_key_here")
    print("\nGet your key from: https://aistudio.google.com/app/apikey")
    exit(1)

def list_models(api_version="v1"):
    """List available models for a given API version"""
    url = f"https://generativelanguage.googleapis.com/{api_version}/models?key={GEMINI_API_KEY}"
    
    try:
        response = requests.get(url, timeout=30)
        
        if not response.ok:
            print(f"\n❌ Error fetching models from {api_version}:")
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
            return None
        
        data = response.json()
        return data.get("models", [])
    
    except Exception as e:
        print(f"\n❌ Error fetching models from {api_version}: {e}")
        return None

def print_model_info(models, api_version):
    """Print formatted model information"""
    if not models:
        print(f"\n⚠️  No models found in {api_version}")
        return
    
    print(f"\n{'='*80}")
    print(f"📋 Available Models in {api_version.upper()} API")
    print(f"{'='*80}\n")
    
    # Filter models that support generateContent
    generate_content_models = []
    for model in models:
        supported_methods = model.get("supportedGenerationMethods", [])
        if "generateContent" in supported_methods:
            generate_content_models.append(model)
    
    if not generate_content_models:
        print("⚠️  No models found that support generateContent")
        return
    
    print(f"Found {len(generate_content_models)} model(s) that support generateContent:\n")
    
    for i, model in enumerate(generate_content_models, 1):
        name = model.get("name", "Unknown")
        display_name = model.get("displayName", "N/A")
        description = model.get("description", "No description")
        version = model.get("version", "N/A")
        input_token_limit = model.get("inputTokenLimit", "N/A")
        output_token_limit = model.get("outputTokenLimit", "N/A")
        
        # Extract model ID from name (e.g., "models/gemini-pro" -> "gemini-pro")
        model_id = name.replace("models/", "") if name.startswith("models/") else name
        
        print(f"{i}. {model_id}")
        print(f"   Display Name: {display_name}")
        print(f"   Version: {version}")
        print(f"   Input Tokens: {input_token_limit:,}" if isinstance(input_token_limit, int) else f"   Input Tokens: {input_token_limit}")
        print(f"   Output Tokens: {output_token_limit:,}" if isinstance(output_token_limit, int) else f"   Output Tokens: {output_token_limit}")
        print(f"   Description: {description[:100]}..." if len(description) > 100 else f"   Description: {description}")
        print()
    
    print(f"{'='*80}")
    print("\n💡 Recommended model names to use in your config:")
    print("   (Copy these to your .env or model_registry.yaml)\n")
    
    for model in generate_content_models:
        name = model.get("name", "")
        model_id = name.replace("models/", "") if name.startswith("models/") else name
        print(f"   - {model_id}")
    
    print()

def main():
    print("🔍 Fetching available Gemini models...")
    print(f"Using API Key: {GEMINI_API_KEY[:10]}...{GEMINI_API_KEY[-4:] if len(GEMINI_API_KEY) > 14 else '****'}\n")
    
    # Try v1 API first
    print("📡 Checking v1 API...")
    v1_models = list_models("v1")
    if v1_models:
        print_model_info(v1_models, "v1")
    
    # Try v1beta API
    print("\n📡 Checking v1beta API...")
    v1beta_models = list_models("v1beta")
    if v1beta_models:
        print_model_info(v1beta_models, "v1beta")
    
    # Summary
    print(f"\n{'='*80}")
    print("✅ Model listing complete!")
    print(f"{'='*80}\n")
    
    if not v1_models and not v1beta_models:
        print("❌ No models found. Possible issues:")
        print("   1. Invalid API key")
        print("   2. API not enabled in Google Cloud Console")
        print("   3. Network/connectivity issues")
        print("\nCheck: https://ai.google.dev/")

if __name__ == "__main__":
    main()

