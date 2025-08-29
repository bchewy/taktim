"""
Debug script to test imports and identify initialization issues
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables first
load_dotenv(Path(__file__).parent.parent / ".env")

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

print("DEBUG: Debugging import issues...")

# Test 1: Environment variables
print("\n1. Testing Environment Variables:")
print(f"OPENAI_API_KEY exists: {'OPENAI_API_KEY' in os.environ}")
print(f"CONGRESS_API_KEY exists: {'CONGRESS_API_KEY' in os.environ}")

# Test 2: Legal research tools
print("\n2. Testing Legal Research Tools Import:")
try:
    from utils.legal_research_tools import create_legal_research_tools
    print("SUCCESS: Legal research tools imported successfully")
    
    # Test tool creation
    tools = create_legal_research_tools()
    print(f"SUCCESS: Created {len(tools)} legal research tools")
    
except Exception as e:
    print(f"ERROR: Legal research tools import failed: {e}")
    import traceback
    traceback.print_exc()

# Test 3: Geo-regulatory agent
print("\n3. Testing Geo-Regulatory Agent Import:")
try:
    from agents.geo_regulatory_agent import GeoRegulatoryAgent
    print("SUCCESS: GeoRegulatoryAgent imported successfully")
    
    # Test agent creation
    agent = GeoRegulatoryAgent()
    print("SUCCESS: GeoRegulatoryAgent created successfully")
    
except Exception as e:
    print(f"ERROR: GeoRegulatoryAgent import/creation failed: {e}")
    import traceback
    traceback.print_exc()

# Test 4: Individual dependencies
print("\n4. Testing Individual Dependencies:")
dependencies = [
    "crewai",
    "crewai_tools", 
    "langchain_openai",
    "httpx",
    "pydantic"
]

for dep in dependencies:
    try:
        __import__(dep)
        print(f"SUCCESS: {dep} imported successfully")
    except Exception as e:
        print(f"ERROR: {dep} import failed: {e}")

print("\nDEBUG: Debug complete!")