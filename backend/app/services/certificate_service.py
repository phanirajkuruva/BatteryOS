import os

from datetime import date
from uuid import uuid4

from reportlab.lib.colors import green, orange, red
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from sqlalchemy.orm import Session

from backend.app.models.battery import Battery
from backend.app.models.certificate import Certificate
from backend.app.models.inspection import Inspection
from backend.app.models.organization import Organization
from backend.app.models.user import User
from backend.app.utils.qr_generator import generate_qr_code


CERTIFICATE_FOLDER = "backend/certificates"

def generate_certificate_number() -> str:
    """
    Generate a unique certificate number.

    Example:
    BATCERT-A1B2C3D4E5F6
    """

    unique_part = uuid4().hex[:12].upper()

    return f"BATCERT-{unique_part}"

def create_certificate(
    db: Session,
    inspection_id: int,
    current_user: User,
):
    """
    Create a certificate record for an inspection.

    Only inspections belonging to the logged-in user's
    organization can be certified.
    """

    inspection = (
        db.query(Inspection)
        .join(Battery)
        .filter(
            Inspection.id == inspection_id,
            Battery.organization_id == current_user.organization_id,
        )
        .first()
    )

    if inspection is None:
        return None

    # Check whether a valid certificate already exists
    # for this inspection.
    existing_certificate = (
        db.query(Certificate)
        .filter(
            Certificate.inspection_id == inspection.id,
            Certificate.organization_id == current_user.organization_id,
            Certificate.status == "Valid",
        )
        .first()
    )

    if existing_certificate is not None:
        return existing_certificate

    certificate = Certificate(
        organization_id=current_user.organization_id,
        battery_id=inspection.battery_id,
        inspection_id=inspection.id,
        issued_by=current_user.id,
        certificate_number=generate_certificate_number(),
        issue_date=date.today(),
        status="Valid",
    )

    db.add(certificate)
    db.commit()
    db.refresh(certificate)

    return certificate
def get_certificate_by_id(
    db: Session,
    certificate_id: int,
    current_user: User,
):
    """
    Get one certificate belonging to the current user's organization.
    """

    return (
        db.query(Certificate)
        .filter(
            Certificate.id == certificate_id,
            Certificate.organization_id == current_user.organization_id,
        )
        .first()
    )
def get_battery_certificates(
    db: Session,
    battery_id: int,
    current_user: User,
):
    """
    Return certificate history for a battery.
    """

    battery = (
        db.query(Battery)
        .filter(
            Battery.id == battery_id,
            Battery.organization_id == current_user.organization_id,
        )
        .first()
    )

    if battery is None:
        return None

    certificates = (
        db.query(Certificate)
        .filter(
            Certificate.battery_id == battery.id,
            Certificate.organization_id == current_user.organization_id,
        )
        .order_by(
            Certificate.created_at.desc(),
            Certificate.id.desc(),
        )
        .all()
    )

    return certificates
def revoke_certificate(
    db: Session,
    certificate_id: int,
    current_user: User,
):
    """
    Revoke a certificate belonging to the current user's organization.
    """

    certificate = (
        db.query(Certificate)
        .filter(
            Certificate.id == certificate_id,
            Certificate.organization_id == current_user.organization_id,
        )
        .first()
    )

    if certificate is None:
        return None

    if certificate.status == "Revoked":
        return certificate

    certificate.status = "Revoked"

    db.commit()
    db.refresh(certificate)

    return certificate

def generate_certificate_pdf(
    db: Session,
    certificate_id: int,
    current_user: User,
):
    """
    Generate a PDF for an existing certificate.

    The certificate must belong to the logged-in user's organization.
    """

    certificate = (
        db.query(Certificate)
        .filter(
            Certificate.id == certificate_id,
            Certificate.organization_id == current_user.organization_id,
        )
        .first()
    )

    if certificate is None:
        return None

    inspection = (
        db.query(Inspection)
        .filter(
            Inspection.id == certificate.inspection_id,
        )
        .first()
    )

    if inspection is None:
        return None

    battery = (
        db.query(Battery)
        .filter(
            Battery.id == certificate.battery_id,
        )
        .first()
    )

    if battery is None:
        return None

    organization = (
        db.query(Organization)
        .filter(
            Organization.id == certificate.organization_id,
        )
        .first()
    )

    if organization is None:
        return None

    inspector = (
        db.query(User)
        .filter(
            User.id == inspection.inspector_id,
        )
        .first()
    )

    if inspector is None:
        return None

    os.makedirs(
        CERTIFICATE_FOLDER,
        exist_ok=True,
    )

    # QR now represents the real certificate,
    # not just the inspection.
    qr_path = generate_qr_code(
        certificate.certificate_number
    )

    pdf_path = (
        f"{CERTIFICATE_FOLDER}/"
        f"{certificate.certificate_number}.pdf"
    )

    pdf = canvas.Canvas(
        pdf_path,
        pagesize=A4,
    )

    width, height = A4

    # -------------------------------------------------
    # HEADER
    # -------------------------------------------------

    pdf.setFont(
        "Helvetica-Bold",
        20,
    )

    pdf.drawCentredString(
        width / 2,
        height - 60,
        "BatteryOS",
    )

    pdf.setFont(
        "Helvetica",
        13,
    )

    pdf.drawCentredString(
        width / 2,
        height - 82,
        "Battery Health Inspection Certificate",
    )

    pdf.line(
        50,
        height - 100,
        width - 50,
        height - 100,
    )

    # -------------------------------------------------
    # CERTIFICATE DETAILS
    # -------------------------------------------------

    pdf.setFont(
        "Helvetica-Bold",
        14,
    )

    pdf.drawString(
        50,
        height - 130,
        "Certificate Details",
    )

    pdf.setFont(
        "Helvetica",
        11,
    )

    pdf.drawString(
        70,
        height - 150,
        f"Certificate Number: {certificate.certificate_number}",
    )

    pdf.drawString(
        70,
        height - 168,
        f"Issue Date: {certificate.issue_date}",
    )

    pdf.drawString(
        70,
        height - 186,
        f"Certificate Status: {certificate.status}",
    )

    # -------------------------------------------------
    # ORGANIZATION
    # -------------------------------------------------

    pdf.setFont(
        "Helvetica-Bold",
        14,
    )

    pdf.drawString(
        50,
        height - 220,
        "Organization",
    )

    pdf.setFont(
        "Helvetica",
        11,
    )

    pdf.drawString(
        70,
        height - 240,
        f"Name: {organization.name}",
    )

    # Organization fields can be nullable.
    if organization.email:
        pdf.drawString(
            70,
            height - 258,
            f"Email: {organization.email}",
        )

    if organization.phone:
        pdf.drawString(
            70,
            height - 276,
            f"Phone: {organization.phone}",
        )

    # -------------------------------------------------
    # BATTERY DETAILS
    # -------------------------------------------------

    pdf.setFont(
        "Helvetica-Bold",
        14,
    )

    pdf.drawString(
        50,
        height - 310,
        "Battery Details",
    )

    pdf.setFont(
        "Helvetica",
        11,
    )

    pdf.drawString(
        70,
        height - 330,
        f"Serial Number: {battery.serial_number}",
    )

    pdf.drawString(
        70,
        height - 348,
        f"Manufacturer: {battery.manufacturer}",
    )

    pdf.drawString(
        70,
        height - 366,
        f"Model: {battery.model}",
    )

    pdf.drawString(
        70,
        height - 384,
        f"Chemistry: {battery.chemistry}",
    )

    pdf.drawString(
        70,
        height - 402,
        f"Lifecycle Status: {battery.lifecycle_status}",
    )

    # -------------------------------------------------
    # INSPECTION DETAILS
    # -------------------------------------------------

    pdf.setFont(
        "Helvetica-Bold",
        14,
    )

    pdf.drawString(
        50,
        height - 440,
        "Inspection Details",
    )

    pdf.setFont(
        "Helvetica",
        11,
    )

    pdf.drawString(
        70,
        height - 460,
        f"Inspection ID: {inspection.id}",
    )

    pdf.drawString(
        70,
        height - 478,
        f"Inspection Date: {inspection.inspection_date}",
    )

    pdf.drawString(
        70,
        height - 496,
        f"Inspector: {inspector.full_name}",
    )

    pdf.drawString(
        70,
        height - 514,
        f"Voltage: {inspection.voltage} V",
    )

    pdf.drawString(
        70,
        height - 532,
        f"Temperature: {inspection.temperature} C",
    )

    pdf.drawString(
        70,
        height - 550,
        f"Cycle Count: {inspection.cycle_count}",
    )

    # -------------------------------------------------
    # HEALTH
    # -------------------------------------------------

    pdf.setFont(
        "Helvetica-Bold",
        14,
    )

    pdf.drawString(
        50,
        height - 590,
        "Battery Health",
    )

    pdf.setFont(
        "Helvetica-Bold",
        18,
    )

    if inspection.health_status == "Excellent":
        pdf.setFillColor(green)

    elif inspection.health_status == "Warning":
        pdf.setFillColor(orange)

    elif inspection.health_status == "Critical":
        pdf.setFillColor(red)

    else:
        pdf.setFillColorRGB(0, 0, 0)

    pdf.drawString(
        70,
        height - 615,
        (
            f"{inspection.health_status} "
            f"({inspection.health_score})"
        ),
    )

    pdf.setFillColorRGB(
        0,
        0,
        0,
    )

    # -------------------------------------------------
    # QR CODE
    # -------------------------------------------------

    pdf.setFont(
        "Helvetica-Bold",
        12,
    )

    pdf.drawString(
        390,
        height - 440,
        "Verify Certificate",
    )

    pdf.drawImage(
        qr_path,
        390,
        height - 575,
        width=110,
        height=110,
    )

    pdf.setFont(
        "Helvetica",
        8,
    )

    pdf.drawString(
        385,
        height - 590,
        "Scan QR to verify authenticity.",
    )

    # -------------------------------------------------
    # REMARKS
    # -------------------------------------------------

    pdf.setFont(
        "Helvetica-Bold",
        13,
    )

    pdf.drawString(
        50,
        height - 655,
        "Remarks",
    )

    pdf.setFont(
        "Helvetica",
        10,
    )

    pdf.drawString(
        70,
        height - 675,
        inspection.remarks or "No remarks provided.",
    )

    # -------------------------------------------------
    # FOOTER
    # -------------------------------------------------

    pdf.line(
        50,
        70,
        width - 50,
        70,
    )

    pdf.setFont(
        "Helvetica",
        9,
    )

    pdf.drawString(
        50,
        50,
        f"Certificate: {certificate.certificate_number}",
    )

    pdf.drawRightString(
        width - 50,
        50,
        "Generated by BatteryOS",
    )

    pdf.save()

    return pdf_path

def verify_certificate(
    db: Session,
    certificate_number: str,
):
    """
    Publicly verify a certificate using its unique certificate number.
    """

    certificate = (
        db.query(Certificate)
        .filter(
            Certificate.certificate_number == certificate_number,
        )
        .first()
    )

    if certificate is None:
        return None

    inspection = (
        db.query(Inspection)
        .filter(
            Inspection.id == certificate.inspection_id,
        )
        .first()
    )

    battery = (
        db.query(Battery)
        .filter(
            Battery.id == certificate.battery_id,
        )
        .first()
    )

    organization = (
        db.query(Organization)
        .filter(
            Organization.id == certificate.organization_id,
        )
        .first()
    )

    inspector = (
        db.query(User)
        .filter(
            User.id == inspection.inspector_id,
        )
        .first()
    )

    return {
        "certificate_valid": certificate.status == "Valid",
        "certificate_number": certificate.certificate_number,
        "certificate_status": certificate.status,
        "issue_date": certificate.issue_date,
        "organization": organization.name,
        "battery_serial": battery.serial_number,
        "manufacturer": battery.manufacturer,
        "model": battery.model,
        "inspection_id": inspection.id,
        "inspection_date": inspection.inspection_date,
        "inspector": inspector.full_name,
        "health_score": inspection.health_score,
        "health_status": inspection.health_status,
    }