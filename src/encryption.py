from pathlib import Path

from cryptography.fernet import Fernet

INSTANCE_DIR = Path(__file__).resolve().parent.parent / "instance"
KEY_FILE = INSTANCE_DIR / "encryption.key"
def _load_or_create_fernet_key() -> bytes:
    if KEY_FILE.exists():
        stored_key = KEY_FILE.read_text(encoding="utf-8").strip()
        if stored_key:
            return stored_key.encode("utf-8")

    fernet_key = Fernet.generate_key()

    INSTANCE_DIR.mkdir(parents=True, exist_ok=True)
    KEY_FILE.write_text(fernet_key.decode("utf-8"), encoding="utf-8")
    return fernet_key


fernet = Fernet(_load_or_create_fernet_key())

class EncryptionService:
    def encrypt(self, data: str) -> str:
        """Criptografa uma string."""
        if not data:
            return data
        return fernet.encrypt(data.encode('utf-8')).decode('utf-8')

    def decrypt(self, encrypted_data: str) -> str:
        """Decriptografa uma string."""
        if not encrypted_data:
            return encrypted_data
        return fernet.decrypt(encrypted_data.encode('utf-8')).decode('utf-8')