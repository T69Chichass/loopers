#!/usr/bin/env python3
"""
Configuration script for Pinecone and OpenAI APIs.
This script helps set up the required API keys and test connections.
"""

import os
import sys
from dotenv import load_dotenv

def create_env_file():
    """Create or update .env file with API configurations."""
    
    # Check if .env exists
    env_exists = os.path.exists('.env')
    
    if env_exists:
        print("📄 .env file already exists. Updating with API configurations...")
        load_dotenv()
    else:
        print("📄 Creating new .env file...")
    
    # Get current values or use defaults
    current_config = {
        'POSTGRES_HOST': os.getenv('POSTGRES_HOST', 'localhost'),
        'POSTGRES_PORT': os.getenv('POSTGRES_PORT', '5432'),
        'POSTGRES_USER': os.getenv('POSTGRES_USER', 'postgres'),
        'POSTGRES_PASSWORD': os.getenv('POSTGRES_PASSWORD', 'your_password_here'),
        'POSTGRES_DB': os.getenv('POSTGRES_DB', 'query_retrieval_db'),
        'PINECONE_API_KEY': os.getenv('PINECONE_API_KEY', 'your_pinecone_api_key'),
        'PINECONE_INDEX_NAME': os.getenv('PINECONE_INDEX_NAME', 'your_pinecone_index_name'),
        'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY', 'your_openai_api_key_here'),
        'OPENAI_MODEL': os.getenv('OPENAI_MODEL', 'gpt-4'),
        'OPENAI_MAX_TOKENS': os.getenv('OPENAI_MAX_TOKENS', '1500'),
        'OPENAI_TEMPERATURE': os.getenv('OPENAI_TEMPERATURE', '0.1'),
        'EMBEDDING_MODEL': os.getenv('EMBEDDING_MODEL', 'all-MiniLM-L6-v2'),
        'APP_ENV': os.getenv('APP_ENV', 'development'),
        'LOG_LEVEL': os.getenv('LOG_LEVEL', 'INFO'),
        'DEBUG': os.getenv('DEBUG', 'True'),
        'SECRET_KEY': os.getenv('SECRET_KEY', 'your_secret_key_here'),
        'ALLOWED_HOSTS': os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1'),
        'RATE_LIMIT_REQUESTS_PER_MINUTE': os.getenv('RATE_LIMIT_REQUESTS_PER_MINUTE', '100'),
        'REDIS_URL': os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
        'SENTRY_DSN': os.getenv('SENTRY_DSN', 'your_sentry_dsn_here')
    }
    
    # Prompt for API keys
    print("\n🔑 API Configuration")
    print("=" * 50)
    
    # Pinecone Configuration
    print("\n🌲 Pinecone Configuration:")
    pinecone_api_key = input(f"Enter Pinecone API Key [{current_config['PINECONE_API_KEY']}]: ").strip()
    if pinecone_api_key:
        current_config['PINECONE_API_KEY'] = pinecone_api_key
    
    pinecone_index = input(f"Enter Pinecone Index Name [{current_config['PINECONE_INDEX_NAME']}]: ").strip()
    if pinecone_index:
        current_config['PINECONE_INDEX_NAME'] = pinecone_index
    
    # OpenAI Configuration
    print("\n🤖 OpenAI Configuration:")
    openai_api_key = input(f"Enter OpenAI API Key [{current_config['OPENAI_API_KEY']}]: ").strip()
    if openai_api_key:
        current_config['OPENAI_API_KEY'] = openai_api_key
    
    # PostgreSQL Configuration (if needed)
    print("\n🗄️ PostgreSQL Configuration:")
    postgres_password = input(f"Enter PostgreSQL Password [{current_config['POSTGRES_PASSWORD']}]: ").strip()
    if postgres_password:
        current_config['POSTGRES_PASSWORD'] = postgres_password
    
    # Write to .env file
    env_content = f"""# Database Configuration
POSTGRES_HOST={current_config['POSTGRES_HOST']}
POSTGRES_PORT={current_config['POSTGRES_PORT']}
POSTGRES_USER={current_config['POSTGRES_USER']}
POSTGRES_PASSWORD={current_config['POSTGRES_PASSWORD']}
POSTGRES_DB={current_config['POSTGRES_DB']}

# Pinecone Configuration
PINECONE_API_KEY={current_config['PINECONE_API_KEY']}
PINECONE_INDEX_NAME={current_config['PINECONE_INDEX_NAME']}

# OpenAI Configuration
OPENAI_API_KEY={current_config['OPENAI_API_KEY']}
OPENAI_MODEL={current_config['OPENAI_MODEL']}
OPENAI_MAX_TOKENS={current_config['OPENAI_MAX_TOKENS']}
OPENAI_TEMPERATURE={current_config['OPENAI_TEMPERATURE']}

# Embedding Model Configuration
EMBEDDING_MODEL={current_config['EMBEDDING_MODEL']}

# Application Configuration
APP_ENV={current_config['APP_ENV']}
LOG_LEVEL={current_config['LOG_LEVEL']}
DEBUG={current_config['DEBUG']}

# Security (Optional)
SECRET_KEY={current_config['SECRET_KEY']}
ALLOWED_HOSTS={current_config['ALLOWED_HOSTS']}

# Rate Limiting (Optional)
RATE_LIMIT_REQUESTS_PER_MINUTE={current_config['RATE_LIMIT_REQUESTS_PER_MINUTE']}

# Cache Configuration (Optional)
REDIS_URL={current_config['REDIS_URL']}

# Monitoring (Optional)
SENTRY_DSN={current_config['SENTRY_DSN']}
"""
    
    try:
        with open('.env', 'w') as f:
            f.write(env_content)
        print("\n✅ .env file updated successfully!")
        return True
    except Exception as e:
        print(f"❌ Failed to update .env file: {e}")
        return False

def test_connections():
    """Test API connections."""
    print("\n🧪 Testing API Connections")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # Test Pinecone
    print("\n🌲 Testing Pinecone...")
    try:
        from pinecone import Pinecone
        api_key = os.getenv('PINECONE_API_KEY')
        index_name = os.getenv('PINECONE_INDEX_NAME')
        
        if api_key == 'your_pinecone_api_key':
            print("⚠️  Pinecone API key not configured")
        else:
            pc = Pinecone(api_key=api_key)
            index = pc.Index(index_name)
            stats = index.describe_index_stats()
            print("✅ Pinecone connection successful!")
            print(f"   Index: {index_name}")
            print(f"   Total vectors: {stats.total_vector_count}")
    except Exception as e:
        print(f"❌ Pinecone connection failed: {e}")
    
    # Test OpenAI
    print("\n🤖 Testing OpenAI...")
    try:
        from openai import OpenAI
        api_key = os.getenv('OPENAI_API_KEY')
        
        if api_key == 'your_openai_api_key_here':
            print("⚠️  OpenAI API key not configured")
        else:
            client = OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=5
            )
            print("✅ OpenAI connection successful!")
            print(f"   Model: gpt-3.5-turbo")
    except Exception as e:
        print(f"❌ OpenAI connection failed: {e}")
    
    # Test Database
    print("\n🗄️ Testing Database...")
    try:
        from sqlalchemy import create_engine, text
        host = os.getenv('POSTGRES_HOST')
        port = os.getenv('POSTGRES_PORT')
        user = os.getenv('POSTGRES_USER')
        password = os.getenv('POSTGRES_PASSWORD')
        database = os.getenv('POSTGRES_DB')
        
        if password == 'your_password_here':
            print("⚠️  Database password not configured")
        else:
            database_url = f"postgresql://{user}:{password}@{host}:{port}/{database}"
            engine = create_engine(database_url)
            with engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
            print("✅ Database connection successful!")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")

def main():
    """Main configuration function."""
    print("🚀 LLM Query-Retrieval System - API Configuration")
    print("=" * 60)
    
    # Create/update .env file
    success = create_env_file()
    
    if success:
        # Test connections
        test_connections()
        
        print("\n🎯 Next Steps:")
        print("1. If any connections failed, update the .env file with correct credentials")
        print("2. Run 'python setup_database.py' to set up the database")
        print("3. Run 'python main.py' to start the LLM system")
        print("4. Visit http://localhost:8000/docs to use the API")
    else:
        print("\n❌ Configuration failed. Please check the error messages above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
