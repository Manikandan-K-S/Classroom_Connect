# Gemini API Troubleshooting Guide

This guide will help you resolve common issues with the Google Gemini API integration in Classroom Connect.

## Common Errors

### 404 Not Found Error

```
404 Client Error: Not Found for url: https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=YOUR_API_KEY
```

**Possible Causes:**
- Outdated model name (the model name may have changed since the code was written)
- API key does not have access to the specified model
- API endpoint has changed

**Solutions:**
1. Run `python gemini_debug.py` to see available models
2. Update your API key with the correct permissions
3. Make sure you're using the correct API version

### API Key Issues

```
Error: ApiKeyError: API key not found. Please set the key with genai.configure(api_key=...), or by setting the GOOGLE_API_KEY environment variable.
```

**Solutions:**
1. Make sure you've added your API key to `classroom_connect/.env`
2. Verify the key is correctly formatted with no extra spaces
3. Check that the environment file is being loaded correctly

### Empty Responses or Generation Failures

**Possible Causes:**
- Content safety filters are blocking the request
- Model doesn't understand the prompt format
- Rate limiting or quota issues

**Solutions:**
1. Simplify your initial test prompts
2. Check your API usage in Google Cloud Console
3. Try a different model (run `gemini_debug.py` to see available models)

## Advanced Troubleshooting

If you're still experiencing issues after trying the solutions above:

1. **Check Network Connectivity**
   - Make sure your computer can reach Google's APIs
   - Verify no firewall or proxy is blocking the connection

2. **Update the Google Generative AI Package**
   ```
   pip install --upgrade google-generativeai
   ```

3. **Check API Status**
   - Visit Google's status page: https://status.generativeai.google/

4. **Debug API Calls**
   Run the debug script with more verbose output:
   ```
   python gemini_debug.py --verbose
   ```

5. **Check Google Cloud Console**
   - Verify API is enabled for your project
   - Check quota usage and limits

## Getting Help

If you continue to experience issues:
1. Reach out to the course instructor
2. Check the Google Generative AI documentation
3. Post on Google Cloud Support forums