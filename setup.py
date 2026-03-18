"""
Setup script to verify installation and test model loading
"""

import sys
import subprocess

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("✗ Python 3.8+ required. Current version:", sys.version)
        return False
    print(f"✓ Python version: {sys.version.split()[0]}")
    return True

def check_package(package_name):
    """Check if a package is installed"""
    try:
        __import__(package_name)
        return True
    except ImportError:
        return False

def install_packages():
    """Install required packages"""
    print("\nInstalling required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ Packages installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("✗ Failed to install packages")
        return False

def verify_installation():
    """Verify all required packages are installed"""
    print("\nVerifying installation...")
    required_packages = {
        "torch": "PyTorch",
        "transformers": "Transformers",
        "PIL": "Pillow",
        "numpy": "NumPy",
        "huggingface_hub": "Hugging Face Hub"
    }
    
    all_installed = True
    for package, name in required_packages.items():
        if check_package(package):
            print(f"✓ {name} installed")
        else:
            print(f"✗ {name} not installed")
            all_installed = False
    
    return all_installed

def main():
    print("=" * 60)
    print("Medical Disease Classification System - Setup")
    print("=" * 60)
    
    # Check Python version
    if not check_python_version():
        print("\nPlease upgrade Python to 3.8 or higher")
        return
    
    # Check if packages are installed
    if not verify_installation():
        install = input("\nSome packages are missing. Install now? (y/n): ").strip().lower()
        if install == "y":
            if not install_packages():
                return
        else:
            print("Please install packages manually: pip install -r requirements.txt")
            return
    
    # Test Hugging Face login
    print("\nTesting Hugging Face authentication...")
    try:
        from huggingface_hub import login
        HF_TOKEN = os.getenv("HF_TOKEN")
        login(token=HF_TOKEN)
        print("✓ Hugging Face authentication successful")
    except Exception as e:
        print(f"✗ Hugging Face authentication failed: {e}")
        return
    
    # Test Groq API
    print("\nTesting Groq API...")
    try:
        from groq import Groq
        GROQ_API_KEY = os.getenv("GROQ_API_KEY")
        client = Groq(api_key=GROQ_API_KEY)
        print("✓ Groq API client initialized")
    except Exception as e:
        print(f"⚠ Groq API warning: {e}")
        print("  Report generation may not work, but classification will still function")
    
    print("\n" + "=" * 60)
    print("Setup complete! You can now run:")
    print("  python quick_start.py  - Interactive interface")
    print("  python medical_classifier.py  - Command line interface")
    print("=" * 60)

if __name__ == "__main__":
    main()




