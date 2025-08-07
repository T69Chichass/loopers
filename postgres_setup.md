# 🐘 PostgreSQL Setup Guide for LLM Document Query System

## 🚀 Quick Setup Options

### **Option 1: Docker PostgreSQL (Recommended for Development)**

The fastest way to get PostgreSQL running for your document system:

```bash
# Run PostgreSQL in Docker
docker run --name postgres-llm \
  -e POSTGRES_PASSWORD=your_password \
  -e POSTGRES_DB=query_retrieval_db \
  -e POSTGRES_USER=llm_user \
  -p 5432:5432 \
  -d postgres:15

# Verify it's running
docker ps
```

**Environment Variables for .env:**
```env
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=llm_user
POSTGRES_PASSWORD=your_password
POSTGRES_DB=query_retrieval_db
```

### **Option 2: Local Installation on Windows**

**Step 1: Download PostgreSQL**
- Visit: https://www.postgresql.org/download/windows/
- Download the Windows x86-64 installer (latest version)

**Step 2: Install PostgreSQL**
1. Run the installer as Administrator
2. Choose installation directory (default: `C:\Program Files\PostgreSQL\16\`)
3. Select components (keep all selected)
4. Set data directory (default: `C:\Program Files\PostgreSQL\16\data\`)
5. **Set password for postgres user** (remember this!)
6. Set port (default: 5432)
7. Complete installation

**Step 3: Add to PATH**
```bash
# Add to your PATH environment variable:
C:\Program Files\PostgreSQL\16\bin
```

**Step 4: Create Database for Your System**
```bash
# Open Command Prompt as Administrator
createdb -U postgres query_retrieval_db

# Or using psql:
psql -U postgres
CREATE DATABASE query_retrieval_db;
CREATE USER llm_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE query_retrieval_db TO llm_user;
\q
```

### **Option 3: Docker Compose (Full Stack)**

Use the provided `docker-compose.yml`:

```bash
# Start all services (PostgreSQL + Redis + App)
docker-compose up -d

# View logs
docker-compose logs postgres

# Access PostgreSQL
docker exec -it loopers-db-1 psql -U postgres -d query_retrieval_db
```

## 🔧 Configure Your Application

### **Update .env File**

```env
# Database Configuration
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=llm_user  # or postgres
POSTGRES_PASSWORD=your_strong_password
POSTGRES_DB=query_retrieval_db

# Other required variables
PINECONE_API_KEY=your_pinecone_key
PINECONE_ENVIRONMENT=your_environment
PINECONE_INDEX_NAME=your_index
OPENAI_API_KEY=your_openai_key
```

## 🗄️ Database Schema

Your system will automatically create these tables:

### **1. Document Metadata**
```sql
CREATE TABLE document_metadata (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id VARCHAR(100) UNIQUE NOT NULL,
    title VARCHAR(500),
    document_type VARCHAR(50),  -- insurance, legal, hr, etc.
    category VARCHAR(100),
    filename VARCHAR(255),
    file_path VARCHAR(1000),
    file_size INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP,
    chunk_count INTEGER,
    processing_status VARCHAR(20) DEFAULT 'pending',
    is_active BOOLEAN DEFAULT TRUE
);
```

### **2. Document Chunks**
```sql
CREATE TABLE document_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    chunk_id VARCHAR(100) UNIQUE NOT NULL,
    document_id VARCHAR(100) NOT NULL,
    chunk_text TEXT NOT NULL,
    chunk_index INTEGER NOT NULL,
    chunk_size INTEGER NOT NULL,
    page_number INTEGER,
    section_title VARCHAR(500),
    section_type VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    embedding_generated BOOLEAN DEFAULT FALSE,
    pinecone_id VARCHAR(100) UNIQUE
);
```

### **3. Query Logs**
```sql
CREATE TABLE query_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    query_id VARCHAR(50) UNIQUE NOT NULL,
    query_text TEXT NOT NULL,
    user_id VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processing_time FLOAT,
    embedding_time FLOAT,
    search_time FLOAT,
    llm_time FLOAT,
    success BOOLEAN DEFAULT FALSE,
    results_count INTEGER,
    confidence_level VARCHAR(10),
    answer TEXT,
    explanation TEXT,
    error_message TEXT,
    error_code VARCHAR(50)
);
```

## 🧪 Test Your Database Connection

Create a test script:

```python
# test_postgres.py
import psycopg2
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

load_dotenv()

def test_connection():
    try:
        # Test with psycopg2
        conn = psycopg2.connect(
            host=os.getenv('POSTGRES_HOST'),
            port=os.getenv('POSTGRES_PORT'),
            database=os.getenv('POSTGRES_DB'),
            user=os.getenv('POSTGRES_USER'),
            password=os.getenv('POSTGRES_PASSWORD')
        )
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"✅ PostgreSQL connected: {version[0]}")
        
        # Test with SQLAlchemy (used by your app)
        database_url = f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}"
        engine = create_engine(database_url)
        
        with engine.connect() as connection:
            result = connection.execute("SELECT current_database();")
            db_name = result.fetchone()[0]
            print(f"✅ SQLAlchemy connected to: {db_name}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

if __name__ == "__main__":
    test_connection()
```

Run the test:
```bash
pip install psycopg2-binary sqlalchemy python-dotenv
python test_postgres.py
```

## 🔍 Manage Your Database

### **Using pgAdmin (GUI)**
1. Open pgAdmin (installed with PostgreSQL)
2. Create new server connection:
   - Host: localhost
   - Port: 5432
   - Database: query_retrieval_db
   - Username: llm_user (or postgres)
   - Password: your_password

### **Using Command Line (psql)**
```bash
# Connect to your database
psql -h localhost -p 5432 -U llm_user -d query_retrieval_db

# Useful commands:
\l                      # List databases
\dt                     # List tables
\d table_name          # Describe table
SELECT * FROM document_metadata LIMIT 5;  # Query data
\q                      # Quit
```

### **Common Operations**

```sql
-- View uploaded documents
SELECT document_id, title, document_type, processing_status, chunk_count 
FROM document_metadata 
ORDER BY created_at DESC;

-- View recent queries
SELECT query_id, query_text, success, confidence_level, processing_time
FROM query_logs 
ORDER BY created_at DESC 
LIMIT 10;

-- Check document chunks
SELECT d.title, COUNT(c.chunk_id) as chunk_count
FROM document_metadata d
LEFT JOIN document_chunks c ON d.document_id = c.document_id
GROUP BY d.document_id, d.title;

-- Clear all data (if needed)
TRUNCATE TABLE query_logs, document_chunks, document_metadata;
```

## 🚨 Troubleshooting

### **Connection Issues**
```bash
# Check if PostgreSQL is running
# Windows:
net start postgresql-x64-16

# Docker:
docker ps | grep postgres

# Check port availability
netstat -an | findstr :5432
```

### **Permission Issues**
```sql
-- Grant all permissions to your user
GRANT ALL PRIVILEGES ON DATABASE query_retrieval_db TO llm_user;
GRANT ALL ON SCHEMA public TO llm_user;
```

### **Reset Everything**
```bash
# Drop and recreate database
dropdb -U postgres query_retrieval_db
createdb -U postgres query_retrieval_db
```

## 🔒 Security Considerations

### **For Development:**
- Use strong passwords
- Limit access to localhost
- Use separate user (not postgres)

### **For Production:**
```sql
-- Create limited user
CREATE USER app_user WITH PASSWORD 'strong_password';
GRANT CONNECT ON DATABASE query_retrieval_db TO app_user;
GRANT USAGE ON SCHEMA public TO app_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO app_user;
```

## 📈 Performance Tips

### **Optimization for Document System:**
```sql
-- Add indexes for better performance
CREATE INDEX idx_document_metadata_type ON document_metadata(document_type);
CREATE INDEX idx_document_chunks_doc_id ON document_chunks(document_id);
CREATE INDEX idx_query_logs_created_at ON query_logs(created_at);
CREATE INDEX idx_document_metadata_status ON document_metadata(processing_status);
```

### **Database Maintenance:**
```sql
-- Regular maintenance
VACUUM ANALYZE;

-- Update statistics
ANALYZE;
```

Your PostgreSQL database is now ready for the LLM Document Query System! 🎉
