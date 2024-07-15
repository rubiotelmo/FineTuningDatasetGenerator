#!/bin/bash
# Execute this command using: nohup ./background_execution.sh &

# Record the start time
start_time=$(date +%s)

# Source the virtual environment
source ./venv/bin/activate

# Run the Python script
python generate_dataset.py

# Record the end time
end_time=$(date +%s)

# Calculate the duration
duration=$((end_time - start_time))

# Log the execution time
echo "Script execution completed in $duration seconds." >> execution_time.log

# Optionally, you can also log the start and end times
echo "Started at: $(date -d @$start_time)" >> execution_time.log
echo "Ended at: $(date -d @$end_time)" >> execution_time.log
echo "----------------------------------------" >> execution_time.log
