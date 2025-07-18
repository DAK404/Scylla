import os
import secrets

# Optional: force overwrite or check for existing key
env_file = ".env"

print("Generating a new secret key...")

# Generate a random 32-character (128-bit) hex key
secret_key = secrets.token_hex(16)

# Write the SECRET_KEY to .env file
with open(env_file, "w") as f:
    f.write(f'SECRET_KEY="{secret_key}"\n')

print(f"Secret key written to {env_file}")
