import hashlib
import jwt
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
import os

class SecurityManager:
    def __init__(self):
        self.secret_key = os.getenv('SECRET_KEY', Fernet.generate_key())
        self.cipher_suite = Fernet(self.secret_key)
        self.users = {}
        self.roles = {
            'admin': ['read', 'write', 'configure', 'manage_users'],
            'operator': ['read', 'write'],
            'viewer': ['read']
        }

    def create_user(self, username: str, password: str, role: str):
        if role not in self.roles:
            raise ValueError(f"Invalid role: {role}")
        
        salt = os.urandom(16)
        password_hash = self._hash_password(password, salt)
        
        self.users[username] = {
            'password_hash': password_hash,
            'salt': salt,
            'role': role
        }

    def authenticate(self, username: str, password: str) -> str:
        if username not in self.users:
            return None

        user = self.users[username]
        password_hash = self._hash_password(password, user['salt'])
        
        if password_hash != user['password_hash']:
            return None

        return self._generate_token(username, user['role'])

    def verify_token(self, token: str) -> dict:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            return payload
        except jwt.InvalidTokenError:
            return None

    def check_permission(self, token: str, required_permission: str) -> bool:
        payload = self.verify_token(token)
        if not payload:
            return False

        role = payload['role']
        return required_permission in self.roles[role]

    def encrypt_data(self, data: str) -> bytes:
        return self.cipher_suite.encrypt(data.encode())

    def decrypt_data(self, encrypted_data: bytes) -> str:
        return self.cipher_suite.decrypt(encrypted_data).decode()

    def _hash_password(self, password: str, salt: bytes) -> bytes:
        return hashlib.pbkdf2_hmac(
            'sha256',
            password.encode(),
            salt,
            100000
        )

    def _generate_token(self, username: str, role: str) -> str:
        payload = {
            'username': username,
            'role': role,
            'exp': datetime.utcnow() + timedelta(hours=8)
        }
        return jwt.encode(payload, self.secret_key, algorithm='HS256')