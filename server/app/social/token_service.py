"""Token encryption helper for social tokens (MVP application-level encryption).

Uses Fernet symmetric encryption. Key must be provided via env var
`SOCIAL_TOKEN_ENCRYPTION_KEY` (URL-safe base64 32-byte key). In production
replace with KMS-based encryption.
"""
import os
import logging
from typing import Optional

from cryptography.fernet import Fernet, InvalidToken

logger = logging.getLogger(__name__)


def _get_fernet() -> Optional[Fernet]:
    key = os.environ.get("SOCIAL_TOKEN_ENCRYPTION_KEY")
    if not key:
        logger.warning("SOCIAL_TOKEN_ENCRYPTION_KEY not set; tokens will not be decryptable across restarts.")
        # generate ephemeral key to allow local dev running (not for production)
        key = Fernet.generate_key().decode()
    try:
        return Fernet(key.encode())
    except Exception:
        logger.exception("Invalid encryption key provided for SOCIAL_TOKEN_ENCRYPTION_KEY")
        return None


def encrypt_token(plaintext: str) -> str:
    """Encrypt a token string and return ciphertext (str).

    Args:
        plaintext: token value (access or refresh)

    Returns:
        ciphertext as str
    """
    f = _get_fernet()
    if not f:
        raise RuntimeError("Token encryption not configured")
    token = plaintext.encode()
    ct = f.encrypt(token)
    return ct.decode()


def decrypt_token(ciphertext: str) -> Optional[str]:
    """Decrypt ciphertext produced by `encrypt_token`.

    Returns None if decryption fails.
    """
    f = _get_fernet()
    if not f:
        raise RuntimeError("Token encryption not configured")
    try:
        pt = f.decrypt(ciphertext.encode())
        return pt.decode()
    except InvalidToken:
        logger.exception("Failed to decrypt token: invalid token")
        return None
