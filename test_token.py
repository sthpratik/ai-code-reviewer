#!/usr/bin/env python3
"""Test Bitbucket token validity"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

def test_token():
    token = os.getenv('BITBUCKET_TOKEN')
    base_url = os.getenv('BITBUCKET_URL', 'https://git.cnvrmedia.net/rest/api/1.0')
    is_server = 'rest/api/1.0' in base_url
    
    print(f"Testing token: {token[:10]}...")
    print(f"Base URL: {base_url}")
    print(f"Type: {'Bitbucket Server' if is_server else 'Bitbucket Cloud'}")
    
    headers = {'Authorization': f'Bearer {token}'}
    
    if is_server:
        # Test 1: Get server info (Bitbucket Server)
        try:
            response = requests.get(f"{base_url}/application-properties", headers=headers)
            print(f"\nServer info test: {response.status_code}")
            if response.status_code == 200:
                server_data = response.json()
                print(f"✓ Server version: {server_data.get('version', 'Unknown')}")
            else:
                print(f"✗ Error: {response.text}")
                
        except Exception as e:
            print(f"✗ Server info failed: {e}")
        
        # Test 2: List projects (Server)
        try:
            response = requests.get(f"{base_url}/projects", headers=headers)
            print(f"\nProjects access test: {response.status_code}")
            if response.status_code == 200:
                projects = response.json()
                print(f"✓ Can access projects. Found {projects.get('size', 0)} projects")
                for project in projects.get('values', [])[:3]:
                    print(f"  - {project.get('key', 'Unknown')}: {project.get('name', 'No name')}")
            else:
                print(f"✗ Cannot access projects: {response.text}")
                
        except Exception as e:
            print(f"✗ Projects test failed: {e}")
            
        # Test 3: Check specific project access
        try:
            response = requests.get(f"{base_url}/projects/CTAPPS", headers=headers)
            print(f"\nCTAPPS project test: {response.status_code}")
            if response.status_code == 200:
                project_data = response.json()
                print(f"✓ Can access CTAPPS project: {project_data.get('name', 'Unknown')}")
            else:
                print(f"✗ Cannot access CTAPPS project: {response.text}")
                
        except Exception as e:
            print(f"✗ CTAPPS project test failed: {e}")
            
    else:
        # Test 1: Get user info (Bitbucket Cloud)
        try:
            response = requests.get(f"{base_url}/user", headers=headers)
            print(f"\nUser API test: {response.status_code}")
            if response.status_code == 200:
                user_data = response.json()
                print(f"✓ Authenticated as: {user_data.get('display_name', 'Unknown')}")
            else:
                print(f"✗ Error: {response.text}")
                
        except Exception as e:
            print(f"✗ Request failed: {e}")
        
        # Test 2: List repositories (Cloud)
        try:
            response = requests.get(f"{base_url}/repositories/CTAPPS", headers=headers)
            print(f"\nWorkspace access test: {response.status_code}")
            if response.status_code == 200:
                print("✓ Can access CTAPPS workspace")
            else:
                print(f"✗ Cannot access CTAPPS workspace: {response.text}")
                
        except Exception as e:
            print(f"✗ Workspace test failed: {e}")

if __name__ == '__main__':
    test_token()
