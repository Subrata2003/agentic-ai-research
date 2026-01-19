# Gemini API Setup Guide

## Quick Setup Steps

### 1. Get Your Free Gemini API Key

1. Visit: **https://makersuite.google.com/app/apikey**
2. Sign in with your Google account
3. Click **"Create API Key"** or **"Get API Key"**
4. Copy your API key (it starts with `AIza...`)

**Note:** Gemini API is completely FREE with generous rate limits!

### 2. Add to .env File

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=AIza-your-actual-key-here
TAVILY_API_KEY=your_tavily_key_here  # Optional
MODEL_NAME=gemini-3-flash-preview
TEMPERATURE=0.7
MAX_TOKENS=4000
```

### 3. Available Gemini Models

- `gemini-3-flash-preview` - Latest preview model (default)
- `gemini-pro` - Stable production model
- `gemini-1.5-pro` - More advanced (if available in your region)
- `gemini-1.5-flash` - Faster, lighter model

### 4. Test Your Setup

```bash
python example.py
```

## Why Gemini?

✅ **Free API** - No credit card required  
✅ **Generous Rate Limits** - Perfect for development  
✅ **High Quality** - Excellent for research and synthesis  
✅ **Easy Setup** - Just get an API key and go!

## Troubleshooting

### "GEMINI_API_KEY is required"
- Make sure your `.env` file exists in the project root
- Check that the key starts with `AIza`
- Verify there are no extra spaces in the `.env` file

### "Invalid API key"
- Regenerate your API key from https://makersuite.google.com/app/apikey
- Make sure you copied the entire key
- Check that the key hasn't expired

### Model not found
- Try using `gemini-3-flash-preview` (default) or `gemini-pro`
- Check if Gemini is available in your region
- Some models may require enabling in Google Cloud Console
- Preview models may have limited availability