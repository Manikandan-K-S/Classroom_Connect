#!/usr/bin/env python
"""
Gemini API Debug Script for Classroom Connect.

This script helps debug issues with the Gemini API connection.
It checks API key validity, available models, and other configuration issues.
"""

import os
import sys
import json
from dotenv import load_dotenv
import requests
import google.generativeai as genai

def main():
    print("=" * 60)
    print("Gemini API Debug Tool for Classroom Connect")
    print("=" * 60)
    
    # Load environment variables
    env_path = "classroom_connect/.env"
    print(f"Looking for .env file at: {env_path}")
    
    if os.path.exists(env_path):
        print("✓ Found .env file")
        load_dotenv(env_path)
    else:
        print("✗ .env file not found!")
        print(f"  Please create {env_path} with your GEMINI_API_KEY")
        return
    
    # Check API key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("✗ GEMINI_API_KEY not set in .env file")
        return
    elif api_key == "your_gemini_api_key_here" or api_key == "your_actual_api_key_here":
        print("✗ GEMINI_API_KEY contains placeholder value")
        print("  Please update it with your actual API key")
        return
    else:
        masked_key = f"{api_key[:8]}...{api_key[-4:]}" if len(api_key) > 12 else "***masked***"
        print(f"✓ Found API key: {masked_key}")
    
    # Check Google Generative AI module
    try:
        print("\nConfiguring Gemini API...")
        genai.configure(api_key=api_key)
        print("✓ Successfully configured Gemini API")
    except Exception as e:
        print(f"✗ Failed to configure Gemini API: {str(e)}")
        return
    
    # Get available models
    try:
        print("\nChecking available models...")
        models = genai.list_models()
        model_names = [model.name for model in models]
        
        if not model_names:
            print("✗ No models returned from API")
        else:
            print(f"✓ Found {len(model_names)} available models:")
            for name in model_names:
                if "gemini" in name.lower():
                    print(f"  • {name} (RECOMMENDED)")
                else:
                    print(f"  • {name}")
        
        # Find best Gemini model
        gemini_models = [m for m in model_names if "gemini" in m.lower()]
        if gemini_models:
            recommended_model = sorted(gemini_models, reverse=True)[0]
        else:
            recommended_model = "gemini-1.5-flash"  # Default to known model
            print(f"✗ No Gemini models found, will try with: {recommended_model}")
    
    except Exception as e:
        print(f"✗ Failed to list models: {str(e)}")
        print("  Will attempt generation with default model")
        recommended_model = "gemini-1.5-flash"  # Default to known model
    
    # Test generation with SDK
    print("\nTesting text generation with SDK...")
    try:
        model = genai.GenerativeModel(recommended_model)
        response = model.generate_content("Say 'Hello, Classroom Connect!' in a short sentence.")
        
        if response.text:
            print("✓ SDK generation successful!")
            print(f"  Response: \"{response.text}\"")
        else:
            print("✗ SDK generation returned empty response")
    except Exception as e:
        print(f"✗ SDK generation failed: {str(e)}")
    
    # Test generation with direct API
    print("\nTesting text generation with direct API...")
    try:
        model_id = recommended_model.split("/")[-1] if "/" in recommended_model else recommended_model
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_id}:generateContent?key={api_key}"
        
        payload = {
            "contents": [{"parts": [{"text": "Say 'Hello, Classroom Connect!' in a short sentence."}]}],
            "generationConfig": {"temperature": 0.7, "maxOutputTokens": 200}
        }
        
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            data = response.json()
            if "candidates" in data and data["candidates"] and "content" in data["candidates"][0]:
                text = data["candidates"][0]["content"]["parts"][0]["text"]
                print("✓ Direct API generation successful!")
                print(f"  Response: \"{text}\"")
            else:
                print("✗ Direct API returned unexpected response format:")
                print(json.dumps(data, indent=2))
        else:
            print(f"✗ Direct API returned status {response.status_code}:")
            print(response.text)
    except Exception as e:
        print(f"✗ Direct API generation failed: {str(e)}")
    
    # Troubleshooting advice
    print("\n" + "=" * 60)
    print("TROUBLESHOOTING ADVICE")
    print("=" * 60)
    
    print("If you're experiencing issues:")
    print("1. Check your API key is valid and has access to Gemini")
    print("2. Verify the model name is correct and available to you")
    print("3. Check your internet connection and firewall settings")
    print("4. Try updating the google-generativeai package:")
    print("   pip install --upgrade google-generativeai")
    print("5. Check the Google AI API status page for service disruptions")
    print("   https://status.generativeai.google/")

if __name__ == "__main__":
    main()