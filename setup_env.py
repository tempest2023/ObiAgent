import os
from pathlib import Path
from dotenv import load_dotenv

def setup_env():
    project_root = Path(__file__).parent
    env_file = project_root / '.env'
    
    if not env_file.exists():
        print("Error: .env file not found. Please create it and set environment variables first.")
        return
    
    # Load .env file
    load_dotenv(env_file)
    
    # Create activation script
    activate_script = project_root / '.env_activate.sh'
    with open(activate_script, 'w') as f:
        f.write('#!/bin/bash\n\n')
        f.write('# Save original environment variable\n')
        f.write('export POCKETFLOW_OLD_ENV="$OPENAI_API_KEY"\n\n')
        
        # Write environment variables
        for key, value in os.environ.items():
            if key.startswith(('OPENAI_', 'POCKETFLOW_')):
                f.write(f'export {key}="{value}"\n')
    
    # Create deactivation script
    deactivate_script = project_root / '.env_deactivate.sh'
    with open(deactivate_script, 'w') as f:
        f.write('#!/bin/bash\n\n')
        f.write('# Restore original environment variable\n')
        f.write('export OPENAI_API_KEY="$POCKETFLOW_OLD_ENV"\n')
        f.write('unset POCKETFLOW_OLD_ENV\n')
    
    # Set script permissions
    os.chmod(activate_script, 0o755)
    os.chmod(deactivate_script, 0o755)
    
    print("Environment setup complete! Use the following commands to activate and deactivate the environment:")
    print(f"\nActivate:\nsource {activate_script}")
    print(f"\nDeactivate:\nsource {deactivate_script}")

if __name__ == '__main__':
    setup_env()
