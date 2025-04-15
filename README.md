<h1 align="center">Judol Comment Filter on Youtube</h1>

This is a Python tool to automatically detect and label YouTube comments that promote online gambling (judi online) using the YouTube Data API and DeepSeek's LLM via OpenRouter.

## Prerequisite

## Requirements
 - Python3
 - [Youtube Data API v3](https://console.cloud.google.com)
 - Deepseek V3 API via [OpenRouter](https://openrouter.ai/deepseek/deepseek-chat:free)

## Setup
1. Clone or download this repo.

    ```sh
    git clone https://github.com/feeco15/youtube-judol-filter.git
    cd youtube-judol-filter
    ```

2. Install depedencies.

    ```sh
    pip install requirements.txt
    ```

3. Replace API keys to `config.json`:

    ```sh
    {
        "youtube_api_key": "YOUR_API_KEY",
        "deepseek_api_key": "YOUR_API_KEY"
    }
    ```

## Usage

```
python judol_filter.py -u YOUTUBE_VIDEO_LINK -s 50
```

### Parameter

```
-u, --url               YouTube video URL
-o, --output            Output CSV file (autogenerated if not set)
-s, --limit-scrap       Number of comments to scrape (default: 100)
```
