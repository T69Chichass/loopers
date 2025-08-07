"""
Simple script to check if the system is working.
"""
import requests
import json

def check_server():
    """Check if the server is running."""
    try:
        response = requests.get('http://localhost:8000/')
        if response.status_code == 200:
            data = response.json()
            print("✅ Server is running!")
            print(f"📝 System: {data['name']}")
            print(f"🔢 Version: {data['version']}")
            print("\n📚 Workflow:")
            for step in data['workflow']:
                print(f"   {step}")
            
            print("\n🔗 Available Endpoints:")
            for name, endpoint in data['endpoints'].items():
                print(f"   {name}: {endpoint}")
            
            print(f"\n📄 Supported Formats: {', '.join(data['supported_formats'])}")
            return True
        else:
            print(f"❌ Server responded with status: {response.status_code}")
            return False
    except requests.ConnectionError:
        print("❌ Server is not running")
        print("💡 Start the server with: python main.py")
        return False
    except Exception as e:
        print(f"❌ Error checking server: {e}")
        return False

def check_health():
    """Check system health."""
    try:
        response = requests.get('http://localhost:8000/health')
        if response.status_code == 200:
            data = response.json()
            print(f"\n🏥 Health Status: {data['status']}")
            print("🔧 Services:")
            for service, status in data['services'].items():
                emoji = "✅" if status == "healthy" else "❌"
                print(f"   {emoji} {service}: {status}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Checking LLM Document Query System...\n")
    
    server_ok = check_server()
    if server_ok:
        check_health()
    
    print("\n" + "="*50)
    if server_ok:
        print("🎉 System is ready to use!")
        print("📖 Next steps:")
        print("   1. Upload documents: POST /documents/upload")
        print("   2. Query documents: POST /query")
        print("   3. View docs: http://localhost:8000/docs")
    else:
        print("⚠️ System needs to be started")
        print("🚀 Run: python main.py")
