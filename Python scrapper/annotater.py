import pandas as pd
import time
import os
import requests
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_DIR = Path(r"E:\Semester\Python scrapper")

HUGGINGFACE_API_TOKEN = os.getenv("HUGGINGFACE_API_TOKEN1")
if not HUGGINGFACE_API_TOKEN:
    HUGGINGFACE_API_TOKEN = input("Enter your HuggingFace API token: ").strip()

MAX_WORKERS = 5
API_DELAY = 0.1


def classify_paper(title, abstract):
    """Classify paper using HuggingFace API."""
    domains = [
        "Machine Learning and Deep Learning",
        "AI and Applications",
        "Theoretical Foundations",
        "Neuroscience and Cognitive Science",
        "Ethics and Fairness in AI"
    ]

    text = f"Title: {title}\nAbstract: {abstract}\n\nClassify this paper into ONE of these domains give just name nothing else: {', '.join(domains)}"

    API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-mnli"
    headers = {"Authorization": f"Bearer {HUGGINGFACE_API_TOKEN}"}

    max_retries = 3
    retry_delay = 5

    for attempt in range(max_retries):
        try:
            payload = {
                "inputs": text,
                "parameters": {"candidate_labels": domains}
            }

            response = requests.post(API_URL, headers=headers, json=payload)

            if response.status_code == 200:
                result = response.json()
                return result['labels'][0]

            elif response.status_code == 503:
                time.sleep(20)
                continue

            elif response.status_code == 429:
                retry_after = int(response.headers.get('Retry-After', 10))
                time.sleep(retry_after)
                continue

            else:
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                continue

        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
            continue

    return rule_based_classify(title, abstract)


def rule_based_classify(title, abstract):
    """Simple rule-based classification as fallback."""
    text = (title + " " + abstract).lower()

    domain_keywords = {
        "Machine Learning and Deep Learning": ["neural network", "deep learning", "machine learning", "transformer", "cnn"],
        "AI and Applications": ["artificial intelligence", "robotics", "computer vision", "nlp", "application"],
        "Theoretical Foundations": ["theory", "mathematical", "proof", "algorithm", "optimization"],
        "Neuroscience and Cognitive Science": ["brain", "neuroscience", "cognitive", "psychology", "neuron"],
        "Ethics and Fairness in AI": ["ethics", "fairness", "bias", "privacy", "responsibility"]
    }

    scores = {domain: 0 for domain in domain_keywords}

    for domain, keywords in domain_keywords.items():
        for keyword in keywords:
            if keyword in text:
                scores[domain] += 1
            if keyword in title.lower():
                scores[domain] += 2

    max_score = max(scores.values())
    return max((domain for domain, score in scores.items() if score == max_score),
               default="AI and Applications")


def process_papers(input_file):
    """Process papers from input CSV and save results."""
    output_dir = ensure_directory()
    output_file = output_dir / f"classified_{input_file.name}"
    log_file = output_dir / "processing_log.txt"

    try:
        print(f"\nReading CSV file: {input_file}")
        df = pd.read_csv(input_file, encoding='utf-8', on_bad_lines='skip')
        print(f"Found {len(df)} papers to process")

        if 'title' not in df.columns or 'abstract' not in df.columns:
            print("❌ Missing required columns: title and abstract")
            return

        if 'domain' not in df.columns:
            df['domain'] = ''

        tasks = []
        for index, row in df.iterrows():
            if pd.notna(row['abstract']) and row['abstract'].strip() != '' and df.at[index, 'domain'] == '':
                tasks.append((index, row['title'], row['abstract']))

        print(f"Processing {len(tasks)} papers with {MAX_WORKERS} workers...")

        start_time = time.time()
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = {executor.submit(classify_paper, title, abstract): (index, title)
                       for index, title, abstract in tasks}

            for future in as_completed(futures):
                index, title = futures[future]
                try:
                    domain = future.result()
                    df.at[index, 'domain'] = domain
                    log = f"✅ Paper {index + 1}: {title} -> {domain}\n"
                except Exception as e:
                    domain = rule_based_classify(
                        title, df.iloc[index]['abstract'])
                    df.at[index, 'domain'] = domain
                    log = f"⚠️ Paper {index + 1}: {title} -> Fallback to {domain}\n"

                with open(log_file, 'a', encoding='utf-8') as f:
                    f.write(log)

                if (index + 1) % 50 == 0:
                    df.to_csv(output_file, index=False)
                    print(f"💾 Interim save after {index + 1} papers")

                time.sleep(API_DELAY)

        df.to_csv(output_file, index=False)
        print(
            f"\n✅ Classification complete! Processed {len(tasks)} papers in {time.time()-start_time:.2f}s")
        print(f"Results saved to {output_file}")

    except Exception as e:
        print(f"❌ Error processing file: {str(e)}")


def ensure_directory():
    """Ensure the required directory structure exists."""
    BASE_DIR.mkdir(parents=True, exist_ok=True)
    output_dir = BASE_DIR / "output"
    output_dir.mkdir(exist_ok=True)
    return output_dir


def main():
    """Main function to process all input CSV files."""
    input_files = list(BASE_DIR.glob("*.csv"))

    if not input_files:
        print("❌ No CSV files found in the input directory")
        return

    for input_file in input_files:
        print(f"\n📄 Processing file: {input_file.name}")
        process_papers(input_file)


if __name__ == "__main__":
    main()
