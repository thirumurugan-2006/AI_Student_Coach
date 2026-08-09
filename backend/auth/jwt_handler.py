from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from config.settings import get_settings

settings = get_settings()


class JWTHandler:
    """
    Handler for JWT token creation and validation.
    """

    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """
        Create a JWT access token.
        
        Args:
            data: The payload data to encode in the token.
            expires_delta: Optional custom expiration time.
            
        Returns:
            Encoded JWT token string.
        """
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=60)
        
        to_encode.update({"exp": expire})
        
        encoded_jwt = jwt.encode(
            to_encode, 
            settings.SECRET_KEY, 
            algorithm="HS256"
        )
        
        return encoded_jwt

    @staticmethod
    def decode_access_token(token: str) -> Optional[dict]:
        """
        Decode and validate a JWT access token.
        
        Args:
            token: The JWT token string to decode.
            
        Returns:
            Decoded payload if valid, None otherwise.
        """
        try:
            payload = jwt.decode(
                token, 
                settings.SECRET_KEY, 
                algorithms=["HS256"]
            )
            return payload
        except JWTError:
            return None

    @staticmethod
    def verify_token(token: str) -> Optional[str]:
        """
        Verify a token and return the user ID if valid.
        
        Args:
            token: The JWT token string to verify.
            
        Returns:
            User ID if valid, None otherwise.
        """
        payload = JWTHandler.decode_access_token(token)
        if payload:
            return payload.get("sub")
        return None
