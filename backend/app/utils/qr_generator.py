import os

import qrcode


QR_FOLDER = "backend/qr_codes"


def generate_qr_code(
    certificate_number: str,
):
    os.makedirs(
        QR_FOLDER,
        exist_ok=True,
    )

    verification_url = (
        "http://127.0.0.1:8000/"
        f"certificates/verify/{certificate_number}"
    )

    qr = qrcode.make(
        verification_url
    )

    qr_path = (
        f"{QR_FOLDER}/"
        f"{certificate_number}.png"
    )

    qr.save(qr_path)

    return qr_path