import argparse
import requests
import json
import time
import sys
import pandas as pd
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse, parse_qs
from tqdm import tqdm
from colorama import init, Fore

init(autoreset=True)

def load_api_keys():
    print("[+] Loading API keys...", end=' ')
    with open("config.json", "r") as f:
        keys = json.load(f)
    print(Fore.GREEN + "ok")
    return keys["youtube_api_key"], keys["deepseek_api_key"]

def extract_video_id(url):
    print("[+] Parsing YouTube video ID...", end=' ')
    parsed_url = urlparse(url)
    if parsed_url.hostname in ["www.youtube.com", "youtube.com"]:
        video_id = parse_qs(parsed_url.query).get("v", [None])[0]
    elif parsed_url.hostname in ["youtu.be"]:
        video_id = parsed_url.path[1:]
    else:
        video_id = None

    if video_id:
        print(Fore.GREEN + "ok")
    else:
        print(Fore.RED + "failed")
    return video_id

def scrape_comments(video_id, api_key, limit=100):
    print(f"[+] Accessing YouTube video comments...", end=' ')
    comments = []
    url = f"https://www.googleapis.com/youtube/v3/commentThreads"
    params = {
        "part": "snippet",
        "videoId": video_id,
        "key": api_key,
        "textFormat": "plainText",
        "maxResults": 100
    }

    next_page_token = ""
    total_scraped = 0
    print(Fore.GREEN + "ok")
    print(f"[+] Start scraping comments [{total_scraped}/{limit}]")

    while next_page_token is not None and total_scraped < limit:
        if next_page_token:
            params["pageToken"] = next_page_token

        response = requests.get(url, params=params)
        data = response.json()

        for item in data.get("items", []):
            comment = item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
            comments.append(comment)
            total_scraped += 1
            
            sys.stdout.write(f"\r[+] Scraping comments... [{total_scraped}/{limit}]")
            sys.stdout.flush()

            if total_scraped >= limit:
                break

        next_page_token = data.get("nextPageToken", None)
    return comments

def auto_labeling(comments_batch, deepseek_api_key):
    prompt_lines = [
        "Classify the following YouTube comments as promoting judi online (online gambling) or not.",
        "Add the sequence and (only) reply by number 1 (yes) or 0 (no) every sentence each line.",
        "Expected answer:\n1. YOUR_ANSWER\n2. YOUR_ANSWER\n3. YOUR_ANSWER\nso on...",
        "Please remove any symbol like * or #. Make it clean!"
    ]

    for idx, comment in enumerate(comments_batch, start=1):
        prompt_lines.append(f"{idx}. {comment}")
    prompt = "\n".join(prompt_lines)
    # print(prompt)

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {deepseek_api_key}"
    }

    data = {
        "model": "deepseek/deepseek-chat:free",
        "messages": [
            {
                "role": "user", 
                "content": prompt
            }
        ],
    }

    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", 
                                 headers=headers, 
                                 json=data
                                 )
        if response.status_code == 200:
            res = response.json()

            if "choices" not in res:
                print(Fore.RED + "\n[!] 'choices' not found in DeepSeek response")
                print(Fore.YELLOW + str(res))
                return [None] * len(comments_batch)

            content = res["choices"][0]["message"]["content"].strip()
            # print(content)
            raw_lines = content.splitlines()
            
            labels = []
            for line in raw_lines:
                if "." in line:
                    line = str(line.split(".", 1)[1].strip())
                labels.append(1 if line == "1" else 0)
                    # if line.endswith(1):
                    #     labels.append(1)
                    # elif line.endswith(0):
                    #     labels.append(0)
                    # else:
                    #     labels.append(None)

            if len(labels) < len(comments_batch):
                labels.extend([None] * (len(comments_batch) - len(labels)))
            elif len(labels) > len(comments_batch):
                labels = labels[:len(comments_batch)]
            
            return labels
        else:
            print(Fore.RED + f"\nDeepSeek API error: {response.status_code}")
            return [None] * len(comments_batch)
    except Exception as e:
        print(Fore.RED + f"\nDeepSeek exception: {e}")
        return [None] * len(comments_batch)

def save_to_csv(comments, labels, output_file):
    if len(comments) != len(labels):
        # print(Fore.YELLOW + f"[!] Length mismatch — comments: {len(comments)}, labels: {len(labels)}")

        if len(labels) < len(comments):
            labels.extend([None] * (len(comments) - len(labels)))
        elif len(labels) > len(comments):
            labels = labels[:len(comments)]

    df = pd.DataFrame({
        "text": comments,
        "label": labels
    })
    df.to_csv(output_file, index=False)

    none_count = labels.count(None)
    if none_count > 0:
        print(Fore.YELLOW + f"[!] {none_count} comments couldn't be labeled by DeepSeek")

    print("[+] Saving output file...", end=' ')
    print(Fore.GREEN + "ok")
    print(f"\nLabeled results saved to: {output_file}")

def main():
    parser = argparse.ArgumentParser(description="Scrape and detect judol YouTube comments")
    parser.add_argument("-u", "--url", required=True, help="YouTube video URL")
    parser.add_argument("-o", "--output", help="Output CSV file")
    parser.add_argument("-s", "--limit-scrap", type=int, default=100, help="Comment limit (default: 100)")
    args = parser.parse_args()

    youtube_api_key, deepseek_api_key = load_api_keys()
    video_id = extract_video_id(args.url)
    if not video_id:
        print("Invalid YouTube URL.")
        return

    output_path = Path("outputs")
    output_path.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    output_file = args.output or f"outputs/labeled_{video_id}_{timestamp}.csv"

    comments = scrape_comments(video_id, youtube_api_key, args.limit_scrap)
    if not comments:
        print("No comments scraped.")
        return

    print("\n[+] Start labeling comments using DeepSeek...", end=' ')
    print(Fore.GREEN + "ok")

    labels = []
    for i in tqdm(range(0, len(comments), 20), desc="[Labeling]"):
        batch = comments[i:i+20]
        batch_labels = auto_labeling(batch, deepseek_api_key)
        labels.extend(batch_labels)
        time.sleep(5)

    save_to_csv(comments, labels, output_file)


main() if __name__ == "__main__" else exit(1)
