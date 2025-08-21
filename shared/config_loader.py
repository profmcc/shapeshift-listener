#!/usr/bin/env python3
"""
Configuration Loader for ShapeShift Affiliate Tracker
Centralized configuration management for all listeners
"""

import os
import yaml
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

class ConfigLoader:
    """Centralized configuration loader for all listeners"""
    
    def __init__(self, config_path: str = None):
        """Initialize config loader with path to config file"""
        # Use environment variable if available, otherwise use default
        if config_path is None:
            # Get the directory where this script is located
            script_dir = os.path.dirname(os.path.abspath(__file__))
            # Go up one level to the project root
            project_root = os.path.dirname(script_dir)
            config_path = os.path.join(project_root, "config", "shapeshift_config.yaml")
        
        self.config_path = config_path
        self.config = None
        
        # Load configuration
        self._load_config()
    
    def _load_config(self):
        """Load configuration from YAML file and resolve environment variables"""
        try:
            # Load environment variables first
            load_dotenv()
            
            # Read config file
            with open(self.config_path, 'r') as file:
                config_content = file.read()
            
            # Replace environment variables
            config_content = os.path.expandvars(config_content)
            
            # Parse YAML
            self.config = yaml.safe_load(config_content)
            
            if not self.config:
                self.config = {}
                
            print(f"✅ Configuration loaded successfully from {self.config_path}")
                
        except FileNotFoundError:
            print(f"⚠️  Configuration file not found: {self.config_path}")
            print(f"💡 Creating empty configuration")
            self.config = {}
        except yaml.YAMLError as e:
            print(f"⚠️  Invalid YAML in configuration file: {e}")
            print(f"💡 Creating empty configuration")
            self.config = {}
        except Exception as e:
            print(f"⚠️  Error loading configuration: {e}")
            print(f"💡 Creating empty configuration")
            self.config = {}
    
    def get_api_key(self, key_name: str) -> str:
        """Get API key from environment or config"""
        # Try environment variable first
        env_key = os.getenv(key_name)
        if env_key:
            return env_key
        
        # Fall back to config
        if self.config and 'api' in self.config:
            return self.config['api'].get(key_name.lower(), '')
        
        return ""
    
    def get_alchemy_api_key(self) -> str:
        """Get Alchemy API key"""
        return self.get_api_key('ALCHEMY_API_KEY')
    
    def get_shapeshift_affiliate_address(self, protocol: str = "primary") -> str:
        """Get ShapeShift affiliate address for specific protocol"""
        if not self.config or 'shapeshift_affiliates' not in self.config:
            return ""
        
        affiliates = self.config['shapeshift_affiliates']
        
        # Try specific protocol first
        if protocol in affiliates:
            return affiliates[protocol]
        
        # Fall back to primary
        return affiliates.get('primary', '')
    
    def get_all_shapeshift_addresses(self) -> List[str]:
        """Get all known ShapeShift affiliate addresses"""
        if not self.config or 'shapeshift_affiliates' not in self.config:
            return []
        
        addresses = []
        affiliates = self.config['shapeshift_affiliates']
        
        # Add specific addresses
        for key, value in affiliates.items():
            if key != 'variations' and isinstance(value, str) and value.startswith('0x'):
                addresses.append(value)
        
        # Add variations
        if 'variations' in affiliates:
            addresses.extend([addr for addr in affiliates['variations'] if addr.startswith('0x')])
        
        # Remove duplicates while preserving order
        seen = set()
        unique_addresses = []
        for addr in addresses:
            if addr.lower() not in seen:
                seen.add(addr.lower())
                unique_addresses.append(addr)
        
        return unique_addresses
    
    def get_chain_config(self, chain_name: str) -> Dict[str, Any]:
        """Get configuration for specific chain"""
        if not self.config or 'chains' not in self.config:
            return {}
        
        return self.config['chains'].get(chain_name, {})
    
    def get_contract_address(self, protocol: str, chain: str) -> str:
        """Get contract address for specific protocol and chain"""
        if not self.config or 'contracts' not in self.config:
            return ""
        
        contracts = self.config['contracts']
        if protocol not in contracts:
            return ""
        
        protocol_contracts = contracts[protocol]
        
        # Try chain-specific address
        if chain in protocol_contracts:
            return protocol_contracts[chain]
        
        # Try alternative names
        chain_aliases = {
            'ethereum': ['eth', 'mainnet'],
            'polygon': ['matic', 'polygon_pos'],
            'arbitrum': ['arb', 'arbitrum_one'],
            'optimism': ['opt', 'optimistic_ethereum'],
            'base': ['base_mainnet'],
            'avalanche': ['avax', 'avalanche_c']
        }
        
        for alias in chain_aliases.get(chain, []):
            if alias in protocol_contracts:
                return protocol_contracts[alias]
        
        return ""
    
    def get_event_signature(self, protocol: str, event_type: str) -> str:
        """Get event signature for specific protocol and event type"""
        if not self.config or 'contracts' not in self.config:
            return ""
        
        contracts = self.config['contracts']
        if protocol not in contracts:
            return ""
        
        protocol_contracts = contracts[protocol]
        
        # Try direct event name
        if event_type in protocol_contracts:
            return protocol_contracts[event_type]
        
        # Try with _event suffix
        event_key = f"{event_type}_event"
        if event_key in protocol_contracts:
            return protocol_contracts[event_key]
        
        return ""
    
    def get_storage_path(self, path_type: str, protocol: str = "") -> str:
        """Get storage path for specific type and protocol"""
        if not self.config or 'storage' not in self.config:
            return ""
        
        storage = self.config['storage']
        
        if path_type == 'csv_directory':
            return storage.get('csv_directory', 'csv_data')
        elif path_type == 'database_directory':
            return storage.get('database_directory', 'databases')
        elif path_type == 'backup_directory':
            return storage.get('backup_directory', 'backups')
        elif path_type == 'file_pattern':
            patterns = storage.get('file_patterns', {})
            if protocol in patterns:
                return patterns[protocol]
            return ""
        
        return ""
    
    def get_listener_config(self, protocol: str) -> Dict[str, Any]:
        """Get listener configuration for specific protocol"""
        if not self.config or 'listeners' not in self.config:
            return {}
        
        listeners = self.config['listeners']
        
        # Start with common settings
        config = listeners.get('common', {}).copy()
        
        # Override with protocol-specific settings
        if protocol in listeners:
            config.update(listeners[protocol])
        
        return config
    
    def get_threshold(self, threshold_type: str) -> float:
        """Get threshold value for specific type"""
        if not self.config or 'thresholds' not in self.config:
            return 0.0
        
        thresholds = self.config['thresholds']
        return thresholds.get(threshold_type, 0.0)
    
    def get_logging_config(self) -> Dict[str, Any]:
        """Get logging configuration"""
        if not self.config or 'logging' not in self.config:
            return {}
        
        return self.config['logging']
    
    def reload_config(self):
        """Reload configuration from file"""
        self._load_config()
    
    def get_config_summary(self) -> Dict[str, Any]:
        """Get summary of current configuration"""
        if not self.config:
            return {}
        
        summary = {
            'api_keys': {
                'alchemy': bool(self.get_alchemy_api_key()),
                'infura': bool(self.get_api_key('INFURA_API_KEY')),
                'coinmarketcap': bool(self.get_api_key('COINMARKETCAP_API_KEY'))
            },
            'shapeshift_addresses': len(self.get_all_shapeshift_addresses()),
            'supported_chains': list(self.config.get('chains', {}).keys()),
            'supported_protocols': list(self.config.get('contracts', {}).keys()),
            'storage_paths': {
                'csv': self.get_storage_path('csv_directory'),
                'database': self.get_storage_path('database_directory'),
                'backup': self.get_storage_path('backup_directory')
            }
        }
        
        return summary

# Global config instance
config = ConfigLoader()

# Convenience functions for easy access
def get_config() -> ConfigLoader:
    """Get global config instance"""
    return config

def get_shapeshift_address(protocol: str = "primary") -> str:
    """Get ShapeShift affiliate address"""
    return config.get_shapeshift_address(protocol)

def get_chain_config(chain_name: str) -> Dict[str, Any]:
    """Get chain configuration"""
    return config.get_chain_config(chain_name)

def get_contract_address(protocol: str, chain: str) -> str:
    """Get contract address"""
    return config.get_contract_address(protocol, chain)

def get_storage_path(path_type: str, protocol: str = "") -> str:
    """Get storage path"""
    return config.get_storage_path(path_type, protocol)

def get_listener_config(protocol: str) -> Dict[str, Any]:
    """Get listener configuration for specific protocol"""
    return config.get_listener_config(protocol)

def get_event_signature(protocol: str, event_type: str) -> str:
    """Get event signature for specific type"""
    return config.get_event_signature(protocol, event_type)

def get_threshold(threshold_type: str) -> float:
    """Get threshold value for specific type"""
    return config.get_threshold(threshold_type)

if __name__ == "__main__":
    # Test configuration loading
    try:
        print("🔧 Configuration Loader Test")
        print("=" * 40)
        
        # Test basic loading
        print(f"✅ Config loaded: {config.config is not None}")
        
        # Test API keys
        alchemy_key = config.get_alchemy_api_key()
        print(f"🔑 Alchemy API Key: {'✅ Set' if alchemy_key else '❌ Not set'}")
        
        # Test ShapeShift addresses
        addresses = config.get_all_shapeshift_addresses()
        print(f"🎯 ShapeShift Addresses: {len(addresses)} found")
        for addr in addresses[:3]:  # Show first 3
            print(f"   {addr}")
        
        # Test chain configs
        chains = list(config.config.get('chains', {}).keys())
        print(f"⛓️  Supported Chains: {len(chains)}")
        for chain in chains[:3]:  # Show first 3
            print(f"   {chain}")
        
        # Test contract addresses
        relay_base = config.get_contract_address('relay', 'base')
        print(f"📋 Relay Base Contract: {relay_base}")
        
        # Test storage paths
        csv_dir = config.get_storage_path('csv_directory')
        print(f"💾 CSV Directory: {csv_dir}")
        
        # Test thresholds
        min_volume = config.get_threshold('minimum_volume_usd')
        print(f"💰 Min Volume Threshold: ${min_volume}")
        
        print(f"\n✅ Configuration test completed successfully!")
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
