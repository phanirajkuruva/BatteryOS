import os
import qrcode


CERTIFICATE_FOLDER = "backend/certificates"


def generate_qr_code(inspection_id: int):
    os.makedirs(CERTIFICATE_FOLDER, exist_ok=True)

    verification_url = (
        f"http://127.0.0.1:8000/certificates/verify/{inspection_id}"
    )

    qr = qrcode.QRCode(
        version=1,
        box_size=8,
        border=3,
    )

    qr.add_data(verification_url)
    qr.make(fit=True)

    image = qr.make_image(fill_color="black", back_color="white")

    qr_path = (
        f"{CERTIFICATE_FOLDER}/qr_{inspection_id}.png"
    )

    image.save(qr_path)

    return qr_path