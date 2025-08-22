#!/usr/bin/env python3
import requests
import json
import csv
import os
from datetime import datetime

class SimpleChainflipListener:
    def __init__(self):
        self.api_url = "http://localhost:10997"
        self.brokers = [
            "cFMeDPtPHccVYdBSJKTtCYuy7rewFNpro3xZBKaCGbSS2xhRi",
            "cFK6mYjpajcwPDZ7JUsac8XUoVSJnhjL43ZMZW7YoN8HE4dD8"
        ]
    
    def test_api(self):
        print("🔗 Testing Chainflip API connection...")
        try:
            response = requests.post(self.api_url, json={"id": 1, "jsonrpc": "2.0", "method": "broker_getInfo", "params": [self.brokers[0]]}, timeout=10)
            if response.status_code == 200:
                print("✅ API connection successful!")
                return True
            else:
                print(f"❌ API error: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False
    
    def run(self):
        print("🚀 Simple Chainflip Listener")
        print(f"📡 API URL: {self.api_url}")
        print(f"📊 Monitoring {len(self.brokers)} brokers")
        
        if self.test_api():
            print("🎯 Ready to collect data!")
        else:
            print("⚠️  API not available - check if Chainflip APIs are running")

if __name__ == "__main__":
    listener = SimpleChainflipListener()
    listener.run()

