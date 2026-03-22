import base64
import io
import pyotp
import qrcode
from qrcode.image.pure import PyPNGImage


def generate_secret() -> str:
    """Generate a random base32 TOTP secret."""
    return pyotp.random_base32()


def get_totp_uri(secret: str, email: str, app_name: str) -> str:
    """Generate the otpauth URI for TOTP registration."""
    totp = pyotp.TOTP(secret)
    return totp.provisioning_uri(name=email, issuer_name=app_name)


def get_qr_code_base64(uri: str) -> str:
    """Generate a QR code PNG image encoded as base64."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(uri)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    encoded = base64.b64encode(buffer.read()).decode("utf-8")
    return f"data:image/png;base64,{encoded}"


def verify_totp(secret: str, code: str) -> bool:
    """Verify a TOTP code against a secret. Allows 1 step window for clock drift."""
    totp = pyotp.TOTP(secret)
    return totp.verify(code, valid_window=1)
