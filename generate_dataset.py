import requests
import json
import random
import hashlib
import os

# TO-DO
# -> Make previous generations reusable (with the actual code, in order to ensure that new samples are crated, all previously created samples must be loaded as initial samples)
# -> ...


# Constant Variables
OLLAMA_API_URL = "http://localhost:11434/api/generate"
INITIAL_SAMPLES = "initial_samples.txt"
NUM_NEW_SAMPLES = 5000 
BATCH_SIZE = 10
SAVE_DIR = "sample_batches"

# Ensure the save directory exists
os.makedirs(SAVE_DIR, exist_ok=True)

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

# Function to save a batch of samples to a JSON file
def save_batch(batch, batch_number):
    filename = os.path.join(SAVE_DIR, f"sample_batch_{batch_number}.json")
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(batch, f, ensure_ascii=False, indent=2)
    print(f"Saved batch {batch_number} to {filename}")

# Main function to generate new dataset samples
def generate_dataset(existing_samples, num_new_samples, max_attempts=3):
    existing_hashes = set(hash_sample(sample) for sample in existing_samples)
    
    attempts = 0
    batch = []
    batch_number = 1
    generated_count = 0

    while generated_count < num_new_samples and attempts < max_attempts * num_new_samples:
        # Select a random subset of existing samples to use as context
        context_samples = random.sample(existing_samples, min(5, len(existing_samples)))
        prompt = generate_prompt(context_samples)
        new_sample_text = generate_sample(prompt)
        if new_sample_text:
            parsed_sample = parse_sample(new_sample_text)
            if all(key in parsed_sample for key in ["instruction", "input", "output"]):
                sample_hash = hash_sample(parsed_sample)
                if sample_hash not in existing_hashes:
                    batch.append(parsed_sample)
                    existing_hashes.add(sample_hash)
                    generated_count += 1
                    print(f"Generated new unique sample {generated_count}/{num_new_samples}")

                    if len(batch) == BATCH_SIZE:
                        save_batch(batch, batch_number)
                        batch = []
                        batch_number += 1
                else:
                    print("Duplicate sample generated, skipping...")
            else:
                print(f"Skipping improperly formatted sample: {new_sample_text}")
        attempts += 1

    # Save any remaining samples in the last batch
    if batch:
        save_batch(batch, batch_number)

    if generated_count < num_new_samples:
        print(f"Warning: Only generated {generated_count} unique samples out of {num_new_samples} requested.")
    
    return generated_count

# Load existing samples
existing_samples = json.loads(open(INITIAL_SAMPLES).read())

# Generate new samples
new_samples_count = generate_dataset(existing_samples, NUM_NEW_SAMPLES)

print(f"Generated {new_samples_count} new samples in total.")
print(f"Samples are saved in batches of {BATCH_SIZE} in the '{SAVE_DIR}' directory.")