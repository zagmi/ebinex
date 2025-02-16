import os
import hashlib
import jwt, json
import time, base64
from win32 import win32crypt
from typing import Any, Dict, Optional
from iykyk import Credentials, EbinexConfig, DEFAULT_VAULT


class Security:
    def __init__(self, vault: str = DEFAULT_VAULT):
        self.vault = vault

    def encrypt_data(self, data: str):
        encrypted_data = win32crypt.CryptProtectData(data.encode(), None, None, None, None, 0)
        return base64.b64encode(encrypted_data).decode()

    def decrypt_data(self, data: str):
        encrypted_data_bytes = base64.b64decode(data)
        return win32crypt.CryptUnprotectData(encrypted_data_bytes, None, None, None, 0)[1].decode()

    def sign(self, huzz: str) -> str:
        return hashlib.sha256(huzz.encode()).hexdigest()

    def load_credentials(self, sign: str) -> Optional[Credentials]:
        if os.path.exists(self.vault):
            with open(self.vault, "r") as f:
                try:
                    credencials_dict: Dict[str, Any] = json.load(f)
                    credentials = Credentials.from_dict(credencials_dict)
                    if credentials.sign == sign:
                        if credentials.expiration and time.time() > credentials.expiration:
                            return None

                        if credentials.account_id and credentials.access_token:
                            credentials.account_id = self.decrypt_data(credentials.account_id)
                            credentials.access_token = self.decrypt_data(credentials.access_token)
                            return credentials
                except:
                    pass
        return None

    def save_credentials(self, huzz: str, **kwargs):
        if "access_token" not in kwargs:
            return

        try:
            account_id = kwargs.get("account_id")
            access_token = kwargs.get("access_token")
            config = EbinexConfig.from_dict(kwargs.get("config"))
            payload: Dict[str, Any] = jwt.decode(access_token, options={"verify_signature": False})

            sign = self.sign(huzz)
            account_id = self.encrypt_data(account_id)
            access_token = self.encrypt_data(access_token)

            credentials = Credentials(sign, account_id, access_token, config, payload.get("exp"))

            with open(self.vault, "w") as f:
                json.dump(credentials.to_dict(), f, indent=4)

        except:
            return
