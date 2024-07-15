import requests
import json
import random
import hashlib

# Ollama API endpoint
OLLAMA_API_URL = "http://localhost:11434/api/generate"

# Function to generate a prompt based on existing samples
def generate_prompt(samples):
    prompt = "Given the following examples, generate a new, bank related, similar sample with an instruction, input, and output:\n\n"
    for sample in samples:
        prompt += f"Instruction: {sample['instruction']}\n"
        prompt += f"Input: {sample['input']}\n"
        prompt += f"Output: {sample['output']}\n\n"
    prompt += "New sample:"
    return prompt

# Function to generate a new sample using Llama 3 70B
def generate_sample(prompt):
    payload = {
        "model": "llama3:70b-instruct",
        "prompt": prompt,
        "stream": False
    }
    
    response = requests.post(OLLAMA_API_URL, json=payload)
    if response.status_code == 200:
        return response.json()['response'].strip()
    else:
        print(f"Error: {response.status_code}")
        return None

# Function to parse the generated sample into the desired format
def parse_sample(sample_text):
    lines = sample_text.split('\n')
    parsed_sample = {}
    current_key = None
    for line in lines:
        if line.startswith("Instruction:"):
            current_key = "instruction"
            parsed_sample[current_key] = line.split(":", 1)[1].strip()
        elif line.startswith("Input:"):
            current_key = "input"
            parsed_sample[current_key] = line.split(":", 1)[1].strip()
        elif line.startswith("Output:"):
            current_key = "output"
            parsed_sample[current_key] = line.split(":", 1)[1].strip()
        elif current_key:
            parsed_sample[current_key] += " " + line.strip()
    return parsed_sample

# Function to create a hash of a sample
def hash_sample(sample):
    sample_str = json.dumps(sample, sort_keys=True)
    return hashlib.md5(sample_str.encode()).hexdigest()

# Main function to generate new dataset samples
def generate_dataset(existing_samples, num_new_samples, max_attempts=3):
    new_samples = []
    existing_hashes = set(hash_sample(sample) for sample in existing_samples)
    
    attempts = 0
    while len(new_samples) < num_new_samples and attempts < max_attempts * num_new_samples:
        # Select a random subset of existing samples to use as context
        context_samples = random.sample(existing_samples, min(3, len(existing_samples)))
        prompt = generate_prompt(context_samples)
        new_sample_text = generate_sample(prompt)
        if new_sample_text:
            parsed_sample = parse_sample(new_sample_text)
            if all(key in parsed_sample for key in ["instruction", "input", "output"]):
                sample_hash = hash_sample(parsed_sample)
                if sample_hash not in existing_hashes:
                    new_samples.append(parsed_sample)
                    existing_hashes.add(sample_hash)
                    print(f"Generated new unique sample {len(new_samples)}/{num_new_samples}")
                else:
                    print("Duplicate sample generated, skipping...")
            else:
                print(f"Skipping improperly formatted sample: {new_sample_text}")
        attempts += 1
    
    if len(new_samples) < num_new_samples:
        print(f"Warning: Only generated {len(new_samples)} unique samples out of {num_new_samples} requested.")
    
    return new_samples

# Function to save samples to a JSON file
def save_to_json(samples, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(samples, f, ensure_ascii=False, indent=2)

# Example usage
existing_samples = json.loads(open('paste.txt').read())

num_new_samples = 5
new_samples = generate_dataset(existing_samples, num_new_samples)

# Combine existing and new samples
all_samples = existing_samples + new_samples

# Save all samples to a JSON file
save_to_json(all_samples, "dataset_samples.json")

print(f"Generated {len(new_samples)} new samples.")
print(f"Total {len(all_samples)} samples saved to dataset_samples.json")
