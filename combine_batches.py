import json
import os

# Directory containing the batch files
batch_directory = 'sample_batches'

# Output file
output_file = 'combined_samples.json'

# Initialize an empty list to hold all samples
all_samples = []

# Loop through all files in the directory
for filename in sorted(os.listdir(batch_directory)):
    if filename.endswith('.json'):
        file_path = os.path.join(batch_directory, filename)
        with open(file_path, 'r') as file:
            batch_samples = json.load(file)
            all_samples.extend(batch_samples)

# Write the combined samples to a single JSON file
with open(output_file, 'w') as outfile:
    json.dump(all_samples, outfile, indent=4)

print(f"Combined JSON file has been created: {output_file}")
