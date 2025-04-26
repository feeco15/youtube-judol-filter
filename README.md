<h1 align="center">Judol Comment Filter on YouTube</h1>

A Python tool to automatically detect and label YouTube comments that promote **judi online (online gambling)** using:
- DeepSeek's LLM via OpenRouter
- YouTube Data API v3
- Optional OAuth login for auto-deleting flagged comments

## 📦 Prerequisite

## Requirements

- Python 3.9+
- [YouTube Data API v3](https://console.cloud.google.com)
- [YouTube OAuth 2.0 Setup](https://console.cloud.google.com)
- [DeepSeek API via OpenRouter](https://openrouter.ai/deepseek/deepseek-chat:free)

## Setup

1. Clone the repository:

    ```bash
    git clone https://github.com/feeco15/youtube-judol-filter.git
    cd youtube-judol-filter
    ```

2. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

3. Create `config.json` and add your API keys:

    ```json
    {
        "youtube_api_key": "YOUR_YOUTUBE_API_KEY",
        "deepseek_api_key": "YOUR_OPENROUTER_API_KEY"
    }
    ```

4. Add your `client_secret.json` in the root directory for YouTube OAuth login.

## Parameters

```text
Flag / Option                       
    -u, --url                           YouTube video URL to analyze
    -s, --limit-scrap                   Number of comments to scrape (default: 100)        
    -o, --output                        Output CSV file path, auto-generated if not set
    -d, --delete-comments               Automatically delete flagged comments with login requires
```

## Usage

Basic detection:
```bash
python judol_filter.py -u YOUTUBE_VIDEO_URL -s 50
```

Auto delete mode:
```bash
python judol_filter.py -u YOUTUBE_VIDEO_URL -s 50 -d
```
