"""
Test all available Gemini models and find the most efficient one
This script will test each model and measure performance
"""

import os
import requests
import json
import time
from typing import Dict, List, Any
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
    exit(1)

TEST_PROMPT = "Explain photosynthesis in 2-3 sentences for a 10th grade student."

def list_models(api_version="v1") -> List[Dict]:
    """List available models for a given API version"""
    url = f"https://generativelanguage.googleapis.com/{api_version}/models?key={GEMINI_API_KEY}"
    
    try:
        response = requests.get(url, timeout=30)
        if response.ok:
            data = response.json()
            return data.get("models", [])
    except Exception as e:
        print(f"Error fetching models from {api_version}: {e}")
    return []

def test_model(model_id: str, api_version: str = "v1") -> Dict[str, Any]:
    """Test a single model and measure performance"""
    endpoint_url = f"https://generativelanguage.googleapis.com/{api_version}/models/{model_id}:generateContent?key={GEMINI_API_KEY}"
    
    payload = {
        "contents": [{
            "parts": [{
                "text": TEST_PROMPT
            }]
        }],
        "generationConfig": {
            "maxOutputTokens": 200,
            "temperature": 0.7
        }
    }
    
    result = {
        "model_id": model_id,
        "api_version": api_version,
        "success": False,
        "response_time": 0,
        "text_length": 0,
        "error": None,
        "text": ""
    }
    
    try:
        start_time = time.time()
        response = requests.post(
            endpoint_url,
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=30
        )
        end_time = time.time()
        
        result["response_time"] = round((end_time - start_time) * 1000, 2)  # in milliseconds
        
        if not response.ok:
            error_data = response.json() if response.headers.get("content-type", "").startswith("application/json") else {}
            result["error"] = error_data.get("error", {}).get("message", response.text)
            return result
        
        data = response.json()
        
        # Extract text
        if "candidates" in data and len(data["candidates"]) > 0:
            candidate = data["candidates"][0]
            if "content" in candidate and "parts" in candidate["content"]:
                result["text"] = candidate["content"]["parts"][0].get("text", "")
                result["text_length"] = len(result["text"])
                result["success"] = True
        
    except requests.exceptions.Timeout:
        result["error"] = "Request timeout"
    except Exception as e:
        result["error"] = str(e)
    
    return result

def main():
    print("🔍 Finding and testing available Gemini models...")
    print(f"Using API Key: {GEMINI_API_KEY[:10]}...{GEMINI_API_KEY[-4:] if len(GEMINI_API_KEY) > 14 else '****'}\n")
    print(f"Test Prompt: \"{TEST_PROMPT}\"\n")
    print("="*80)
    
    # Get all available models
    all_models = []
    
    print("\n📡 Fetching models from v1 API...")
    v1_models = list_models("v1")
    for model in v1_models:
        name = model.get("name", "")
        if "generateContent" in model.get("supportedGenerationMethods", []):
            model_id = name.replace("models/", "")
            all_models.append((model_id, "v1"))
    
    print(f"Found {len([m for m in all_models if m[1] == 'v1'])} model(s) in v1")
    
    print("\n📡 Fetching models from v1beta API...")
    v1beta_models = list_models("v1beta")
    for model in v1beta_models:
        name = model.get("name", "")
        if "generateContent" in model.get("supportedGenerationMethods", []):
            model_id = name.replace("models/", "")
            # Only add if not already in v1
            if (model_id, "v1") not in all_models:
                all_models.append((model_id, "v1beta"))
    
    print(f"Found {len([m for m in all_models if m[1] == 'v1beta'])} additional model(s) in v1beta")
    
    if not all_models:
        print("\n❌ No models found that support generateContent")
        print("Check your API key and ensure Gemini API is enabled")
        return
    
    print(f"\n🧪 Testing {len(all_models)} model(s)...\n")
    print("="*80)
    
    results = []
    
    for i, (model_id, api_version) in enumerate(all_models, 1):
        print(f"\n[{i}/{len(all_models)}] Testing: {model_id} ({api_version})")
        result = test_model(model_id, api_version)
        results.append(result)
        
        if result["success"]:
            print(f"   ✅ Success! Response time: {result['response_time']}ms, Text length: {result['text_length']} chars")
            print(f"   Preview: {result['text'][:100]}...")
        else:
            print(f"   ❌ Failed: {result['error']}")
    
    # Analyze results
    print("\n" + "="*80)
    print("📊 TEST RESULTS SUMMARY")
    print("="*80)
    
    successful_results = [r for r in results if r["success"]]
    
    if not successful_results:
        print("\n❌ No models succeeded. Check your API key and quotas.")
        return
    
    # Sort by response time (fastest first)
    successful_results.sort(key=lambda x: x["response_time"])
    
    print(f"\n✅ {len(successful_results)}/{len(results)} model(s) succeeded\n")
    
    print("🏆 PERFORMANCE RANKING (Fastest to Slowest):\n")
    for i, result in enumerate(successful_results, 1):
        speed_emoji = "⚡" if result["response_time"] < 1000 else "🐢"
        print(f"{i}. {result['model_id']} ({result['api_version']})")
        print(f"   {speed_emoji} Response Time: {result['response_time']}ms")
        print(f"   📝 Text Length: {result['text_length']} characters")
        print(f"   📊 Efficiency Score: {round(result['text_length'] / result['response_time'] * 1000, 2)} chars/sec")
        print()
    
    # Recommend best model
    best = successful_results[0]
    print("="*80)
    print("🎯 RECOMMENDATION")
    print("="*80)
    print(f"\n✅ Best Model: {best['model_id']}")
    print(f"   API Version: {best['api_version']}")
    print(f"   Response Time: {best['response_time']}ms")
    print(f"   Efficiency: {round(best['text_length'] / best['response_time'] * 1000, 2)} chars/sec")
    print(f"\n💡 Add this to your .env file:")
    print(f"   GEMINI_MODEL_ID={best['model_id']}")
    print(f"\n💡 Or update model_registry.yaml:")
    print(f"   active_model: \"{best['model_id']}\"")
    print()
    
    # Show sample response
    if best['text']:
        print("📄 Sample Response:")
        print("-" * 80)
        print(best['text'])
        print("-" * 80)
        print()

if __name__ == "__main__":
    main()

