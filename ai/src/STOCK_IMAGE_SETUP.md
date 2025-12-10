# Stock Image API Integration - Setup Guide

## Overview

The pipeline now uses **stock images by default** instead of AI image generation. The image generation module remains available but is detached from the main pipeline and only used as a fallback.

## Architecture

```
Media Integration Agent
  ↓
Stock Image Agent (Default) ✅
  ├─→ Unsplash API
  ├─→ Pexels API
  └─→ Pixabay API
  ↓
[If stock fails] → Image Generation Agent (Fallback)
  ├─→ Stability AI
  ├─→ HuggingFace
  └─→ Local Stable Diffusion
```

## Configuration

### 1. Environment Variables (.env file)

Add to `ai/.env`:

```env
# Stock Image API Configuration
STOCK_IMAGE_PROVIDER=unsplash  # Options: unsplash, pexels, pixabay
IMAGE_SOURCE=stock  # Options: stock (default), generate

# API Keys (get at least one)
UNSPLASH_API_KEY=your_unsplash_access_key
PEXELS_API_KEY=your_pexels_api_key
PIXABAY_API_KEY=your_pixabay_api_key
```

### 2. Get API Keys

#### Unsplash (Recommended)
1. Go to https://unsplash.com/developers
2. Create a new application
3. Copy your Access Key
4. Add to `.env` as `UNSPLASH_API_KEY`

#### Pexels
1. Go to https://www.pexels.com/api/
2. Sign up and get your API key
3. Add to `.env` as `PEXELS_API_KEY`

#### Pixabay
1. Go to https://pixabay.com/api/docs/
2. Sign up and get your API key
3. Add to `.env` as `PIXABAY_API_KEY`

### 3. Model Registry Config

The `config/model_registry.yaml` has been updated with stock image settings:

```yaml
image:
  source: "stock"  # Default: use stock images
  stock_image:
    provider: "unsplash"  # Default provider
```

## How It Works

### Default Flow (Stock Images)

1. **Slide Content Analysis**
   - Media Integration Agent analyzes slide title and content
   - Builds search query from key terms

2. **Stock Image Search**
   - Stock Image Agent searches selected provider (Unsplash/Pexels/Pixabay)
   - Returns relevant images based on query

3. **Image Selection**
   - First result is selected (can be enhanced with ranking logic)
   - Image metadata stored in MongoDB

4. **Integration**
   - Image URL added to slide
   - Attribution information stored

### Fallback Flow (If Stock Fails)

If stock image search fails or returns no results:
- Falls back to Image Generation Agent
- Uses AI generation (Stability AI, HuggingFace, or local SD)
- Only used when stock images unavailable

## Features

### ✅ Implemented

- **Multiple Providers**: Unsplash, Pexels, Pixabay
- **Smart Query Building**: Extracts keywords from slide content
- **Caching**: Search results cached for performance
- **Fallback**: Automatic fallback to AI generation if stock fails
- **Metadata Storage**: Stores image info, attribution, and source
- **Marker Support**: Works with image markers from slide generation

### Stock Image Agent Methods

```python
# Search for images
result = stock_agent.search(query="photosynthesis", provider="unsplash")

# Get image for a slide
result = stock_agent.get_image_for_slide(
    slide_title="Introduction to Photosynthesis",
    slide_content=["Process of converting sunlight", "Occurs in plants"],
    context={"subject": "biology"}
)

# Get images from markers
result = stock_agent.get_images_from_markers(
    markers=[{"prompt": "plant with sunlight", "slide_index": 0}],
    context={"grade_level": "10th"}
)
```

## Switching Between Stock and Generation

### Use Stock Images (Default)
```env
IMAGE_SOURCE=stock
STOCK_IMAGE_PROVIDER=unsplash
```

### Use AI Generation
```env
IMAGE_SOURCE=generate
```

### Per-Request Override

The media integration agent reads from config, but you can override in context:

```python
context = {
    "image_source": "stock",  # or "generate"
    "stock_provider": "pexels"  # Optional provider override
}
```

## Image Generation Module Status

✅ **Still Available**: The `ImageGenerationAgent` remains fully functional  
✅ **Detached**: Not used by default in the main pipeline  
✅ **Fallback**: Automatically used if stock images fail  
✅ **Accessible**: Can be called directly if needed  

## Benefits of Stock Images

1. **Faster**: No generation time, instant results
2. **Higher Quality**: Professional photography
3. **Cost Effective**: Free APIs with generous limits
4. **Reliable**: No GPU/compute requirements
5. **Attribution**: Proper photo credits included

## API Limits

- **Unsplash**: 50 requests/hour (free tier)
- **Pexels**: 200 requests/hour (free tier)
- **Pixabay**: 100 requests/hour (free tier)

Caching helps stay within limits by reusing search results.

## Testing

Test the stock image integration:

```python
from agents.stock_image_agent import StockImageAgent

agent = StockImageAgent()

# Test search
result = agent.search("photosynthesis", provider="unsplash")
print(result)

# Test slide image
result = agent.get_image_for_slide(
    slide_title="Photosynthesis",
    slide_content=["Process in plants", "Converts sunlight"]
)
print(result)
```

## Troubleshooting

### No Images Found
- Check API key is set correctly
- Verify provider name (lowercase: "unsplash", "pexels", "pixabay")
- Check API rate limits
- Try different search query

### API Errors
- Verify API key is valid
- Check network connectivity
- Review API documentation for changes
- Check rate limits

### Fallback to Generation
- Stock images will automatically fallback to generation if:
  - API key not configured
  - API returns no results
  - API request fails
  - Rate limit exceeded

## Next Steps

1. ✅ Add API keys to `.env`
2. ✅ Set `IMAGE_SOURCE=stock` in `.env`
3. ✅ Choose provider: `STOCK_IMAGE_PROVIDER=unsplash`
4. ✅ Test with a presentation generation
5. ✅ Monitor API usage and adjust as needed

The pipeline is now ready to use stock images by default! 🎉

