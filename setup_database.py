#!/usr/bin/env python3
"""
Database setup script for the LLM Query-Retrieval System.
This script helps set up PostgreSQL database and tables.
"""

import os
import sys
from sqlalchemy import create_engine, text
from database import create_tables, Base

def setup_database():
    """Set up the database and create tables."""
    
    # Database configuration - update these with your actual values
    DB_CONFIG = {
        'host': os.getenv('POSTGRES_HOST', 'localhost'),
        'port': os.getenv('POSTGRES_PORT', '5432'),
        'user': os.getenv('POSTGRES_USER', 'postgres'),
        'password': os.getenv('POSTGRES_PASSWORD', 'your_password_here'),
        'database': os.getenv('POSTGRES_DB', 'query_retrieval_db')
    }
    
    # Construct database URL
    database_url = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
    
    try:
        # Test connection
        print("Testing database connection...")
        engine = create_engine(database_url)
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ Database connection successful!")
        
        # Create tables
        print("Creating database tables...")
        create_tables(engine)
        print("✅ Database tables created successfully!")
        
        print("\n🎉 Database setup completed!")
        print(f"Database URL: postgresql://{DB_CONFIG['user']}:***@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}")
        
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        print("\n📋 To fix this, please:")
        print("1. Install PostgreSQL if not already installed")
        print("2. Create a database named 'query_retrieval_db'")
        print("3. Update the .env file with your PostgreSQL credentials")
        print("4. Run this script again")
        return False
    
    return True

def create_env_template():
    """Create a template .env file."""
    env_content = """# Database Configuration
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password_here
POSTGRES_DB=query_retrieval_db

# Pinecone Configuration
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_ENVIRONMENT=your_pinecone_environment
PINECONE_INDEX_NAME=your_pinecone_index_name

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4
OPENAI_MAX_TOKENS=1500
OPENAI_TEMPERATURE=0.1

# Embedding Model Configuration
EMBEDDING_MODEL=all-MiniLM-L6-v2

# Application Configuration
APP_ENV=development
LOG_LEVEL=INFO
DEBUG=True

# Security (Optional)
SECRET_KEY=your_secret_key_here
ALLOWED_HOSTS=localhost,127.0.0.1

# Rate Limiting (Optional)
RATE_LIMIT_REQUESTS_PER_MINUTE=100

# Cache Configuration (Optional)
REDIS_URL=redis://localhost:6379/0

# Monitoring (Optional)
SENTRY_DSN=your_sentry_dsn_here
"""
    
    try:
        with open('.env', 'w') as f:
            f.write(env_content)
        print("✅ .env template created successfully!")
        print("📝 Please update the .env file with your actual credentials")
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")

if __name__ == "__main__":
    print("🚀 LLM Query-Retrieval System - Database Setup")
    print("=" * 50)
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("📄 .env file not found. Creating template...")
        create_env_template()
        print("\n⚠️  Please update the .env file with your credentials before continuing.")
        print("   Then run this script again.")
        sys.exit(1)
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Setup database
    success = setup_database()
    
    if success:
        print("\n🎯 Next steps:")
        print("1. Configure Pinecone API key in .env file")
        print("2. Configure OpenAI API key in .env file")
        print("3. Run 'python main.py' to start the LLM system")
    else:
        sys.exit(1)
