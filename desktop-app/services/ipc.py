"""
IPC (Inter-Process Communication) service for communicating with the Node.js API server
Handles starting/stopping the API server and syncing account data
"""
import asyncio
import json
import subprocess
import requests
from pathlib import Path
import config

class IPCService:
    def __init__(self):
        self.process = None
        self.api_url = config.API_SERVER_URL
    
    def is_server_running(self) -> bool:
        """Check if API server is running"""
        try:
            response = requests.get(f"{self.api_url}/health", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    async def start_server(self):
        """Start the API server as a subprocess"""
        if self.is_server_running():
            print("API server is already running")
            return True
        
        # Find api-server path
        api_server_path = Path(__file__).parent.parent.parent / "api-server"
        
        # Start server
        process = subprocess.Popen(
            ["node", "src/index.js"],
            cwd=str(api_server_path),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        
        # Wait for server to start
        for _ in range(30):
            await asyncio.sleep(0.5)
            if self.is_server_running():
                print(f"API server started at {self.api_url}")
                self.process = process
                return True
        
        # If we get here, server didn't start
        process.terminate()
        raise Exception("Failed to start API server")
    
    async def stop_server(self):
        """Stop the API server"""
        if self.process:
            self.process.terminate()
            self.process.wait()
            self.process = None
            print("API server stopped")
        else:
            print("No server process to stop")
    
    # Account sync methods
    async def sync_account_to_api(self, account_data: dict):
        """
        Sync account data to API server
        
        Args:
            account_data: { id, provider, email, session_token, ... }
        """
        response = requests.post(
            f"{self.api_url}/v1/accounts",
            json={
                "provider": account_data["provider"],
                "email": account_data.get("email"),
                "session_token": account_data["session_token"],
                "refresh_token": account_data.get("refresh_token"),
                "access_token": account_data.get("access_token"),
                "expires_at": account_data.get("expires_at"),
            }
        )
        
        if response.status_code != 201:
            raise Exception(f"Failed to sync account: {response.text}")
        
        return response.json()
    
    async def get_account_quota(self, account_id: str) -> dict:
        """Get quota status for an account"""
        response = requests.get(f"{self.api_url}/v1/accounts/{account_id}/quota")
        
        if response.status_code != 200:
            raise Exception(f"Failed to get quota: {response.text}")
        
        return response.json()
    
    async def create_api_key(self, account_id: str, label: str = None) -> str:
        """Create API key for an account"""
        response = requests.post(
            f"{self.api_url}/v1/keys",
            json={
                "account_id": account_id,
                "label": label,
            }
        )
        
        if response.status_code != 201:
            raise Exception(f"Failed to create API key: {response.text}")
        
        return response.json()["key"]
    
    async def get_api_keys(self) -> list:
        """Get all API keys"""
        response = requests.get(f"{self.api_url}/v1/keys")
        
        if response.status_code != 200:
            raise Exception(f"Failed to get API keys: {response.text}")
        
        return response.json()["data"]
    
    async def delete_api_key(self, key: str):
        """Delete an API key"""
        response = requests.delete(f"{self.api_url}/v1/keys/{key}")
        
        if response.status_code != 200:
            raise Exception(f"Failed to delete API key: {response.text}")
    
    async def get_accounts_from_api(self) -> list:
        """Get all accounts from API server"""
        response = requests.get(f"{self.api_url}/v1/accounts")
        
        if response.status_code != 200:
            raise Exception(f"Failed to get accounts: {response.text}")
        
        return response.json()["data"]
    
    async def update_account_session(self, account_id: str, session_token: str):
        """Update session token for an account on API server"""
        response = requests.put(
            f"{self.api_url}/v1/accounts/{account_id}",
            json={"session_token": session_token}
        )
        
        if response.status_code != 200:
            raise Exception(f"Failed to update session: {response.text}")

# Global IPC service instance
ipc = IPCService()

async def start_api_server():
    """Start the API server"""
    await ipc.start_server()

async def stop_api_server():
    """Stop the API server"""
    await ipc.stop_server()

def is_api_server_running() -> bool:
    """Check if API server is running"""
    return ipc.is_server_running()

def get_api_url() -> str:
    """Get API server URL"""
    return ipc.api_url
