# src/presentation/cli.py
"""
CLI interface for cryptographic operations
"""
import argparse
import sys
import json
import base64
from typing import Optional
from datetime import datetime, timedelta

from ..application.services import (
    PasswordService, TokenService, EncryptionService, HMACService
)
from ..application.dto import (
    PasswordDTO, EncryptDTO, DecryptDTO, HMACDTO
)


class CryptoCLI:
    """CLI для криптографических операций"""
    
    def __init__(self):
        self.password_service = PasswordService()
        self.token_service = TokenService()
        self.encryption_service = EncryptionService()
        self.hmac_service = HMACService()
    
    def run(self, args: Optional[list] = None) -> None:
        """Запуск CLI"""
        parser = argparse.ArgumentParser(description='Cryptographic operations CLI')
        subparsers = parser.add_subparsers(dest='command', help='Command to execute')
        
        # Hash password command
        hash_parser = subparsers.add_parser('hash', help='Hash a password')
        hash_parser.add_argument('password', help='Password to hash')
        hash_parser.add_argument('--salt', help='Salt (optional)')
        
        # Verify password command
        verify_parser = subparsers.add_parser('verify', help='Verify a password')
        verify_parser.add_argument('password', help='Password to verify')
        verify_parser.add_argument('hash', help='Hash to compare')
        verify_parser.add_argument('salt', help='Salt used for hashing')
        
        # Generate token command
        token_parser = subparsers.add_parser('token', help='Generate a token')
        token_parser.add_argument('user_id', type=int, help='User ID')
        token_parser.add_argument('secret', help='Secret key')
        token_parser.add_argument('--expires', type=int, default=24, help='Expires in hours')
        
        # Verify token command
        verify_token_parser = subparsers.add_parser('verify-token', help='Verify a token')
        verify_token_parser.add_argument('token', help='Token to verify')
        verify_token_parser.add_argument('secret', help='Secret key')
        
        # Encrypt command
        encrypt_parser = subparsers.add_parser('encrypt', help='Encrypt data')
        encrypt_parser.add_argument('data', help='Data to encrypt')
        encrypt_parser.add_argument('key', help='Encryption key')
        
        # Decrypt command
        decrypt_parser = subparsers.add_parser('decrypt', help='Decrypt data')
        decrypt_parser.add_argument('encrypted', help='Encrypted data')
        decrypt_parser.add_argument('key', help='Decryption key')
        
        # Parse arguments
        parsed_args = parser.parse_args(args)
        
        if not parsed_args.command:
            parser.print_help()
            return
        
        # Execute command
        try:
            if parsed_args.command == 'hash':
                self._hash_command(parsed_args)
            elif parsed_args.command == 'verify':
                self._verify_command(parsed_args)
            elif parsed_args.command == 'token':
                self._token_command(parsed_args)
            elif parsed_args.command == 'verify-token':
                self._verify_token_command(parsed_args)
            elif parsed_args.command == 'encrypt':
                self._encrypt_command(parsed_args)
            elif parsed_args.command == 'decrypt':
                self._decrypt_command(parsed_args)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
    
    def _hash_command(self, args) -> None:
        result = self.password_service.hash_password(
            PasswordDTO(password=args.password, salt=args.salt)
        )
        print(json.dumps({
            'hash': result.hash,
            'salt': result.salt,
            'algorithm': result.algorithm
        }, indent=2))
    
    def _verify_command(self, args) -> None:
        is_valid = self.password_service.verify_password(
            args.password, args.hash, args.salt
        )
        print(json.dumps({'is_valid': is_valid}, indent=2))
    
    def _token_command(self, args) -> None:
        token = self.token_service.generate_token(
            args.user_id, args.secret, args.expires
        )
        print(json.dumps({'token': token}, indent=2))
    
    def _verify_token_command(self, args) -> None:
        result = self.token_service.verify_token(args.token, args.secret)
        print(json.dumps({
            'is_valid': result.is_valid,
            'user_id': result.user_id,
            'error': result.error
        }, indent=2))
    
    def _encrypt_command(self, args) -> None:
        encrypted = self.encryption_service.encrypt(
            EncryptDTO(data=args.data, key=args.key)
        )
        print(json.dumps({'encrypted': encrypted}, indent=2))
    
    def _decrypt_command(self, args) -> None:
        decrypted = self.encryption_service.decrypt(
            DecryptDTO(encrypted_data=args.encrypted, key=args.key)
        )
        print(json.dumps({'decrypted': decrypted}, indent=2))


def main():
    cli = CryptoCLI()
    cli.run()


if __name__ == '__main__':
    main()