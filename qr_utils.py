import os
import uuid

import qrcode


def generate_ticket_code() -> str:
    """Generate a unique, unguessable ticket code for one attendee."""
    return str(uuid.uuid4())


def generate_qr_code(data: str, filename: str, out_dir: str) -> str:
    """
    Render `data` as a QR PNG inside `out_dir`.
    Kept high-contrast (black on white) so it stays reliably scannable
    on both printed tickets and phone screens.
    """
    os.makedirs(out_dir, exist_ok=True)

    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=3,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="#101828", back_color="#FFFFFF")
    path = os.path.join(out_dir, filename)
    img.save(path)
    return path
