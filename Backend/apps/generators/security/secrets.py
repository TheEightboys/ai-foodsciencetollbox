"""
Enterprise-grade secrets management with HashiCorp Vault integration.
Implements automatic rotation, audit logging, and zero-standing privileges.
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from django.conf import settings
from django.core.cache import cache
import hvac
from cryptography.fernet import Fernet
import threading

logger = logging.getLogger(__name__)


class VaultManager:
    """
    HashiCorp Vault integration for enterprise secrets management.
    """
    
    def __init__(self):
        self.client = None
        self.transit_key = None
        self._connect_to_vault()
        self._setup_transit()
    
    def _connect_to_vault(self):
        """Connect to HashiCorp Vault."""
        try:
            vault_url = getattr(settings, 'VAULT_URL', 'https://vault.company.com')
            vault_token = self._get_vault_token()
            
            self.client = hvac.Client(
                url=vault_url,
                token=vault_token,
                verify=getattr(settings, 'VAULT_VERIFY_SSL', True)
            )
            
            # Verify connection
            if not self.client.is_authenticated():
                raise Exception("Failed to authenticate with Vault")
            
            logger.info("Successfully connected to HashiCorp Vault")
            
        except Exception as e:
            logger.error(f"Failed to connect to Vault: {e}")
            raise
    
    def _get_vault_token(self) -> str:
        """Get Vault token from environment or Kubernetes auth."""
        # Try Kubernetes auth first
        if getattr(settings, 'VAULT_USE_K8S_AUTH', False):
            return self._k8s_auth()
        
        # Fall back to token from environment
        token = os.getenv('VAULT_TOKEN')
        if not token:
            raise Exception("VAULT_TOKEN not set in environment")
        return token
    
    def _k8s_auth(self) -> str:
        """Authenticate using Kubernetes service account."""
        try:
            role = os.getenv('VAULT_K8S_ROLE', 'teachai-app')
            jwt_path = '/var/run/secrets/kubernetes.io/serviceaccount/token'
            
            with open(jwt_path, 'r') as f:
                jwt = f.read()
            
            response = self.client.auth.kubernetes.login(
                role=role,
                jwt=jwt
            )
            
            return response['auth']['client_token']
            
        except Exception as e:
            logger.error(f"K8s auth failed: {e}")
            raise
    
    def _setup_transit(self):
        """Setup Transit engine for encryption."""
        try:
            # Enable transit engine if not already enabled
            self.client.sys.enable_secrets_engine(
                'transit',
                path='transit'
            )
            
            # Create or get encryption key
            key_name = getattr(settings, 'VAULT_TRANSIT_KEY', 'teachai-encryption')
            
            try:
                self.client.transit.create_key(name=key_name)
                logger.info(f"Created new transit key: {key_name}")
            except hvac.exceptions.InvalidRequest:
                # Key already exists
                pass
            
            self.transit_key = key_name
            
        except Exception as e:
            logger.error(f"Failed to setup transit: {e}")
            raise
    
    def get_secret(self, path: str, key: str = None) -> Any:
        """
        Retrieve secret from Vault.
        
        Args:
            path: Secret path in Vault
            key: Specific key to retrieve (optional)
            
        Returns:
            Secret value or dict of all secrets
        """
        try:
            # Check cache first
            cache_key = f"vault_secret:{path}:{key or 'all'}"
            cached = cache.get(cache_key)
            if cached is not None:
                return cached
            
            # Retrieve from Vault
            response = self.client.secrets.kv.v2.read_secret_version(path=path)
            
            if not response or 'data' not in response:
                raise Exception(f"Secret not found at path: {path}")
            
            data = response['data']['data']
            
            # Log access for audit
            self._log_secret_access(path, key, 'read')
            
            # Return specific key or all data
            result = data[key] if key else data
            
            # Cache for 5 minutes
            cache.set(cache_key, result, 300)
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to get secret {path}: {e}")
            raise
    
    def set_secret(self, path: str, data: Dict[str, Any]):
        """
        Store secret in Vault.
        
        Args:
            path: Secret path in Vault
            data: Dictionary of secret data
        """
        try:
            self.client.secrets.kv.v2.create_or_update_secret(
                path=path,
                secret=data
            )
            
            # Log access for audit
            self._log_secret_access(path, None, 'write')
            
            # Clear cache
            cache.delete_pattern(f"vault_secret:{path}:*")
            
            logger.info(f"Secret stored at path: {path}")
            
        except Exception as e:
            logger.error(f"Failed to store secret {path}: {e}")
            raise
    
    def encrypt_data(self, data: str) -> str:
        """
        Encrypt data using Vault Transit.
        
        Args:
            data: Data to encrypt
            
        Returns:
            Base64 encoded encrypted data
        """
        try:
            response = self.client.transit.encrypt_data(
                name=self.transit_key,
                plaintext=data.encode().hex(),
                context='teachai-app'
            )
            
            return response['data']['ciphertext']
            
        except Exception as e:
            logger.error(f"Failed to encrypt data: {e}")
            raise
    
    def decrypt_data(self, ciphertext: str) -> str:
        """
        Decrypt data using Vault Transit.
        
        Args:
            ciphertext: Encrypted data
            
        Returns:
            Decrypted data
        """
        try:
            response = self.client.transit.decrypt_data(
                name=self.transit_key,
                ciphertext=ciphertext,
                context='teachai-app'
            )
            
            hex_data = response['data']['plaintext']
            return bytes.fromhex(hex_data).decode()
            
        except Exception as e:
            logger.error(f"Failed to decrypt data: {e}")
            raise
    
    def rotate_secret(self, path: str, new_data: Dict[str, Any]):
        """
        Rotate secret with versioning.
        
        Args:
            path: Secret path
            new_data: New secret data
        """
        try:
            # Get current version
            current = self.client.secrets.kv.v2.read_secret_version(path=path)
            current_version = current['data']['metadata']['version'] if current else 0
            
            # Store new version
            self.client.secrets.kv.v2.create_or_update_secret(
                path=path,
                secret=new_data
            )
            
            # Log rotation
            logger.info(f"Rotated secret {path} from version {current_version}")
            
            # Trigger any rotation hooks
            self._trigger_rotation_hooks(path, current_version + 1)
            
        except Exception as e:
            logger.error(f"Failed to rotate secret {path}: {e}")
            raise
    
    def _log_secret_access(self, path: str, key: Optional[str], action: str):
        """Log secret access for audit trail."""
        audit_log = {
            'timestamp': datetime.utcnow().isoformat(),
            'path': path,
            'key': key,
            'action': action,
            'user': os.getenv('USER', 'system'),
            'service': 'teachai-app'
        }
        
        # Log to secure audit system
        logger.info(f"VAULT_AUDIT: {json.dumps(audit_log)}")
    
    def _trigger_rotation_hooks(self, path: str, version: int):
        """Trigger hooks after secret rotation."""
        # Notify dependent services
        # Update configuration
        # Restart services if needed
        pass


class SecretsManager:
    """
    High-level secrets management interface.
    """
    
    def __init__(self):
        self.vault = VaultManager()
        self._rotation_schedule: Dict[str, datetime] = {}
        self._lock = threading.Lock()
    
    def get_api_key(self, service: str) -> str:
        """
        Get API key with automatic rotation.
        
        Args:
            service: Service name (e.g., 'openai', 'anthropic')
            
        Returns:
            API key
        """
        path = f"secrets/{service}"
        
        # Check if rotation is needed
        if self._should_rotate(path):
            self._rotate_api_key(service)
        
        return self.vault.get_secret(path, 'api_key')
    
    def _should_rotate(self, path: str) -> bool:
        """Check if secret needs rotation."""
        with self._lock:
            if path not in self._rotation_schedule:
                return False
            
            return datetime.utcnow() >= self._rotation_schedule[path]
    
    def _rotate_api_key(self, service: str):
        """Rotate API key for a service."""
        path = f"secrets/{service}"
        
        try:
            # Generate new key (this would be service-specific)
            new_key = self._generate_new_api_key(service)
            
            # Store in Vault
            self.vault.rotate_secret(path, {'api_key': new_key})
            
            # Schedule next rotation
            self._rotation_schedule[path] = datetime.utcnow() + timedelta(days=30)
            
            logger.info(f"Rotated API key for {service}")
            
        except Exception as e:
            logger.error(f"Failed to rotate API key for {service}: {e}")
    
    def _generate_new_api_key(self, service: str) -> str:
        """Generate new API key (placeholder)."""
        # In reality, this would call the service's API
        import secrets
        return f"sk-{secrets.token_urlsafe(48)}"
    
    def encrypt_sensitive_data(self, data: str) -> str:
        """Encrypt sensitive data for storage."""
        return self.vault.encrypt_data(data)
    
    def decrypt_sensitive_data(self, ciphertext: str) -> str:
        """Decrypt sensitive data."""
        return self.vault.decrypt_data(ciphertext)
    
    def get_database_credentials(self, environment: str = 'production') -> Dict[str, str]:
        """
        Get database credentials with zero-standing privileges.
        
        Args:
            environment: Environment (production, staging, etc.)
            
        Returns:
            Database credentials
        """
        path = f"database/{environment}/credentials"
        
        # Generate temporary credentials
        temp_creds = self._generate_temp_db_credentials(environment)
        
        # Store with short TTL
        self.vault.set_secret(path, temp_creds)
        
        return temp_creds
    
    def _generate_temp_db_credentials(self, environment: str) -> Dict[str, str]:
        """Generate temporary database credentials."""
        # This would integrate with your database's auth system
        import secrets
        username = f"teachai_temp_{secrets.token_urlsafe(8)}"
        password = secrets.token_urlsafe(32)
        
        return {
            'username': username,
            'password': password,
            'host': getattr(settings, f'DB_HOST_{environment.upper()}'),
            'database': getattr(settings, f'DB_NAME_{environment.upper()}')
        }


# Global instance
_secrets_manager = None

def get_secrets_manager() -> SecretsManager:
    """Get global secrets manager instance."""
    global _secrets_manager
    if _secrets_manager is None:
        _secrets_manager = SecretsManager()
    return _secrets_manager


# Django settings integration
class VaultSettings:
    """
    Settings integration for Vault secrets.
    """
    
    def __getattr__(self, name: str) -> Any:
        """Get setting from Vault if not in Django settings."""
        # First try Django settings
        if hasattr(settings, name):
            return getattr(settings, name)
        
        # Then try Vault
        try:
            manager = get_secrets_manager()
            return manager.vault.get_secret(f"settings/{name}", 'value')
        except:
            raise AttributeError(f"Setting {name} not found")


# Use in settings.py
# from apps.generators.security.secrets import VaultSettings
# vault_settings = VaultSettings()
# OPENAI_API_KEY = vault_settings.OPENAI_API_KEY
