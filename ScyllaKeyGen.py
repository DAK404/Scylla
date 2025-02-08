import os
import secrets

print("RUN THE PROGRAM AS ROOT!")

# Generate the secret key
secret_key = secrets.token_hex(16)
print(f"Generated Secret Key: {secret_key}")

# Set the environment variables in /etc/environment
env_file_path = '/etc/environment'
env_var_entries = [
    f'SECRET_KEY="{secret_key}"\n'
]

# Read the current /etc/environment file
with open(env_file_path, 'r') as env_file:
    lines = env_file.readlines()

# Update or add the environment variables
for entry in env_var_entries:
    key = entry.split('=')[0]
    found = False
    for i, line in enumerate(lines):
        if line.startswith(key):
            lines[i] = entry
            found = True
            break
    if not found:
        lines.append(entry)

# Write the changes back to /etc/environment
with open(env_file_path, 'w') as env_file:
    env_file.writelines(lines)

print("Environment variables set in /etc/environment\nRun the following command to apply the changes:\n\nsource /etc/environment\n")
