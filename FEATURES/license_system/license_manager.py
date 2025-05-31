import secrets

class LicenseGenerator:
    def create_code(self):
        return f"MULLER-{secrets.token_hex(4)}"
