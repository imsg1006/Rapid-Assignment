#!/usr/bin/env python3
"""
Script to help set up the environment file for Flux integration
"""
import os

def create_env_file():
    """Create or update the .env file with Flux configuration"""
    
    env_content = """# Database Configuration
DATABASE_URL=postgresql://image_ai_user:image_ai_password@localhost:5432/image_ai_db

# Security
SECRET_KEY=your-super-secret-key-here-change-in-production-12345
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=True

# CORS
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000

# Flux ImageGen MCP Server Configuration
# Get your API key from: https://flux.ai/
FLUX_API_KEY=your-actual-flux-api-key-here
# The base URL for the Flux MCP server (adjust if needed)
FLUX_BASE_URL=https://api.flux.ai
"""
    
    env_file = ".env"
    
    if os.path.exists(env_file):
        print(f"⚠️  {env_file} already exists!")
        response = input("Do you want to overwrite it? (y/N): ").strip().lower()
        if response != 'y':
            print("❌ Environment file not updated.")
            return False
    
    try:
        with open(env_file, 'w') as f:
            f.write(env_content)
        
        print(f"✅ {env_file} created successfully!")
        print("\n📝 IMPORTANT: You need to edit this file and:")
        print("1. Replace 'your-actual-flux-api-key-here' with your real Flux API key")
        print("2. Get your API key from: https://flux.ai/")
        print("3. Make sure the FLUX_BASE_URL is correct for your setup")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to create {env_file}: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Flux Environment Setup Script")
    print("=" * 40)
    
    if create_env_file():
        print("\n🎯 Next steps:")
        print("1. Edit the .env file and add your Flux API key")
        print("2. Test the integration: python3 test_flux_integration.py")
        print("3. Start the server: python3 start.py")
    else:
        print("\n❌ Setup failed. Please check the error messages above.")
