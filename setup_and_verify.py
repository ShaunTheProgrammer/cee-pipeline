#!/usr/bin/env python3
"""
Setup and Verification Script for CEE Pipeline
Checks installation, configuration, and runs basic tests
"""
import sys
import os
from pathlib import Path


def print_header(text):
    """Print formatted header"""
    print("\n" + "="*80)
    print(f"  {text}")
    print("="*80)


def print_step(text, status=None):
    """Print step with status"""
    if status is None:
        print(f"\n{text}")
    elif status == "ok":
        print(f"✓ {text}")
    elif status == "error":
        print(f"✗ {text}")
    elif status == "warning":
        print(f"⚠ {text}")


def check_python_version():
    """Check Python version"""
    print_step("Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print_step(f"Python {version.major}.{version.minor}.{version.micro}", "ok")
        return True
    else:
        print_step(f"Python {version.major}.{version.minor} - Need 3.8+", "error")
        return False


def check_dependencies():
    """Check if all dependencies are installed"""
    print_step("Checking dependencies...")

    required = [
        "fastapi", "uvicorn", "pydantic", "sqlalchemy",
        "openai", "anthropic", "nltk", "pandas"
    ]

    missing = []
    for package in required:
        try:
            __import__(package)
            print_step(f"{package}", "ok")
        except ImportError:
            print_step(f"{package} - NOT INSTALLED", "error")
            missing.append(package)

    if missing:
        print_step("\nInstall missing packages with:", "warning")
        print(f"  pip install -r requirements.txt")
        return False

    return True


def check_env_file():
    """Check if .env file exists and has required keys"""
    print_step("Checking environment configuration...")

    env_path = Path(".env")

    if not env_path.exists():
        print_step(".env file not found", "error")
        print_step("Create .env file with:", "warning")
        print("  cp .env.example .env")
        print("  # Then edit .env and add your API key")
        return False

    print_step(".env file exists", "ok")

    # Check for API keys
    with open(env_path) as f:
        content = f.read()

    has_openai = "OPENAI_API_KEY" in content and "your_openai" not in content
    has_anthropic = "ANTHROPIC_API_KEY" in content and "your_anthropic" not in content

    if has_openai:
        print_step("OpenAI API key configured", "ok")
    if has_anthropic:
        print_step("Anthropic API key configured", "ok")

    if not (has_openai or has_anthropic):
        print_step("No valid API keys found", "error")
        print_step("Add at least one API key to .env file", "warning")
        return False

    return True


def check_project_structure():
    """Check if all required directories and files exist"""
    print_step("Checking project structure...")

    required_paths = [
        "cee_pipeline/",
        "cee_pipeline/api/main.py",
        "cee_pipeline/core/pipeline.py",
        "cee_pipeline/core/tier1_evaluator.py",
        "cee_pipeline/core/tier2_evaluator.py",
        "cee_pipeline/core/tier3_evaluator.py",
        "cee_pipeline/core/trust_score.py",
        "cee_pipeline/database/models.py",
        "cee_pipeline/dashboard/dashboard.html",
        "examples/",
        "requirements.txt",
        "README.md"
    ]

    all_exist = True
    for path in required_paths:
        if Path(path).exists():
            print_step(f"{path}", "ok")
        else:
            print_step(f"{path} - MISSING", "error")
            all_exist = False

    return all_exist


def initialize_database():
    """Initialize database tables"""
    print_step("Initializing database...")

    try:
        from cee_pipeline.database.database import db
        db.create_tables()
        print_step("Database tables created", "ok")
        return True
    except Exception as e:
        print_step(f"Database initialization failed: {e}", "error")
        return False


def run_basic_test():
    """Run a basic functionality test"""
    print_step("Running basic functionality test...")

    try:
        from cee_pipeline.core.tier1_evaluator import Tier1Evaluator

        evaluator = Tier1Evaluator()
        result = evaluator.evaluate("This is a clean test message")

        if result.passed:
            print_step("Tier 1 evaluation works", "ok")
        else:
            print_step("Tier 1 evaluation returned unexpected result", "warning")

        from cee_pipeline.core.trust_score import TrustScoreCalculator
        calculator = TrustScoreCalculator()
        print_step("Trust Score calculator initialized", "ok")

        return True

    except Exception as e:
        print_step(f"Basic test failed: {e}", "error")
        return False


def download_nltk_data():
    """Download required NLTK data"""
    print_step("Downloading NLTK data...")

    try:
        import nltk
        nltk.download('punkt', quiet=True)
        print_step("NLTK data downloaded", "ok")
        return True
    except Exception as e:
        print_step(f"NLTK download failed: {e}", "warning")
        return False


def print_next_steps():
    """Print next steps for the user"""
    print_header("SETUP COMPLETE!")

    print("\n🎉 Your CEE Pipeline is ready to use!\n")

    print("Next steps:\n")

    print("1. Run the interactive pipeline:")
    print("   python run_pipeline.py\n")

    print("2. Try the examples:")
    print("   python examples/basic_usage.py")
    print("   python examples/batch_evaluation.py\n")

    print("3. Start the API server:")
    print("   python -m cee_pipeline.api.main")
    print("   Then visit: http://localhost:8000/docs\n")

    print("4. View the dashboard:")
    print("   Open cee_pipeline/dashboard/dashboard.html in your browser\n")

    print("5. Read the documentation:")
    print("   QUICKSTART.md - Quick start guide")
    print("   README.md - Full documentation")
    print("   ARCHITECTURE.md - Technical details\n")

    print("="*80)


def main():
    """Main setup and verification"""
    print_header("CEE Pipeline - Setup and Verification")

    print("\nThis script will:")
    print("  • Check your Python version")
    print("  • Verify dependencies are installed")
    print("  • Check environment configuration")
    print("  • Verify project structure")
    print("  • Initialize the database")
    print("  • Run basic functionality tests")

    input("\nPress Enter to continue...")

    # Run all checks
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Environment Config", check_env_file),
        ("Project Structure", check_project_structure),
        ("NLTK Data", download_nltk_data),
        ("Database", initialize_database),
        ("Basic Tests", run_basic_test),
    ]

    results = []
    for name, check_func in checks:
        print_header(name)
        result = check_func()
        results.append((name, result))

    # Summary
    print_header("VERIFICATION SUMMARY")

    all_passed = True
    for name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{name:.<50} {status}")
        if not result:
            all_passed = False

    if all_passed:
        print_next_steps()
        return 0
    else:
        print("\n⚠️  Some checks failed. Please resolve the issues above.")
        print("\nFor help, see:")
        print("  • QUICKSTART.md")
        print("  • README.md")
        return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n✗ Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Setup failed with error: {e}")
        sys.exit(1)
