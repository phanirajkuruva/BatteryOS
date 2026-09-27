import os
from datetime import datetime, timezone

from sqlalchemy.orm import Session
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
)
from backend.app.models.battery import Battery
from backend.app.models.inspection import Inspection
from backend.app.models.maintenance import Maintenance
from backend.app.models.user import User
REPORT_FOLDER = "backend/reports"

def generate_battery_health_report(
    db: Session,
    battery_id: int,
    current_user: User,
):
    # Tenant-safe battery lookup
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

    inspections = (
        db.query(Inspection)
        .filter(
            Inspection.battery_id == battery.id,
        )
        .order_by(
            Inspection.inspection_date.desc(),
            Inspection.id.desc(),
        )
        .all()
    )

    maintenance_records = (
        db.query(Maintenance)
        .filter(
            Maintenance.battery_id == battery.id,
        )
        .order_by(
            Maintenance.scheduled_date.desc(),
            Maintenance.id.desc(),
        )
        .all()
    )

    latest_inspection = inspections[0] if inspections else None

    return {
        "battery_id": battery.id,
        "serial_number": battery.serial_number,
        "manufacturer": battery.manufacturer,
        "model": battery.model,
        "chemistry": battery.chemistry,

        "capacity": battery.capacity,
        "rated_voltage": battery.voltage,

        "operational_status": battery.status,
        "lifecycle_status": battery.lifecycle_status,

        "manufacturing_date": battery.manufacturing_date,
        "installation_date": battery.installation_date,

        "purchase_date": battery.purchase_date,
        "warranty_start_date": battery.warranty_start_date,
        "warranty_end_date": battery.warranty_end_date,

        "latest_health_score": (
            latest_inspection.health_score
            if latest_inspection
            else None
        ),

        "latest_health_status": (
            latest_inspection.health_status
            if latest_inspection
            else None
        ),

        "total_inspections": len(inspections),
        "total_maintenance_records": len(maintenance_records),

        "inspections": inspections,
        "maintenance_records": maintenance_records,

        "generated_at": datetime.now(timezone.utc),
    }
def generate_battery_health_report_pdf(
    db: Session,
    battery_id: int,
    current_user: User,
):
    """
    Generate a complete battery health report as a PDF.
    """

    report = generate_battery_health_report(
        db=db,
        battery_id=battery_id,
        current_user=current_user,
    )

    if report is None:
        return None

    os.makedirs(
        REPORT_FOLDER,
        exist_ok=True,
    )

    file_name = (
        f"battery_health_report_{battery_id}.pdf"
    )

    pdf_path = os.path.join(
        REPORT_FOLDER,
        file_name,
    )

    document = SimpleDocTemplate(
        pdf_path,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        alignment=TA_CENTER,
        fontSize=20,
        spaceAfter=6,
    )

    subtitle_style = ParagraphStyle(
        "ReportSubtitle",
        parent=styles["Normal"],
        alignment=TA_CENTER,
        fontSize=10,
        spaceAfter=18,
    )

    section_style = ParagraphStyle(
        "SectionTitle",
        parent=styles["Heading2"],
        fontSize=14,
        spaceBefore=12,
        spaceAfter=8,
    )

    story = []

    # -------------------------------------------------
    # HEADER
    # -------------------------------------------------

    story.append(
        Paragraph(
            "BatteryOS",
            title_style,
        )
    )

    story.append(
        Paragraph(
            "Battery Health Report",
            subtitle_style,
        )
    )

    story.append(
        Paragraph(
            (
                "Generated: "
                f"{report['generated_at'].strftime('%Y-%m-%d %H:%M:%S UTC')}"
            ),
            styles["Normal"],
        )
    )

    story.append(
        Spacer(1, 12)
    )

    # -------------------------------------------------
    # BATTERY INFORMATION
    # -------------------------------------------------

    story.append(
        Paragraph(
            "Battery Information",
            section_style,
        )
    )

    battery_data = [
        ["Field", "Value"],
        ["Battery ID", str(report["battery_id"])],
        ["Serial Number", report["serial_number"]],
        ["Manufacturer", report["manufacturer"]],
        ["Model", report["model"]],
        ["Chemistry", report["chemistry"]],
        ["Capacity", str(report["capacity"])],
        ["Rated Voltage", str(report["rated_voltage"])],
        [
            "Operational Status",
            report["operational_status"],
        ],
        [
            "Lifecycle Status",
            report["lifecycle_status"],
        ],
        [
            "Manufacturing Date",
            str(report["manufacturing_date"]),
        ],
        [
            "Installation Date",
            str(report["installation_date"] or "-"),
        ],
    ]

    battery_table = Table(
        battery_data,
        colWidths=[
            55 * mm,
            105 * mm,
        ],
    )

    battery_table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.lightgrey,
                ),
                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold",
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.grey,
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP",
                ),
                (
                    "PADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),
            ]
        )
    )

    story.append(battery_table)

    # -------------------------------------------------
    # WARRANTY
    # -------------------------------------------------

    story.append(
        Paragraph(
            "Warranty Information",
            section_style,
        )
    )

    warranty_data = [
        ["Field", "Value"],
        [
            "Purchase Date",
            str(report["purchase_date"] or "-"),
        ],
        [
            "Warranty Start Date",
            str(report["warranty_start_date"] or "-"),
        ],
        [
            "Warranty End Date",
            str(report["warranty_end_date"] or "-"),
        ],
    ]

    warranty_table = Table(
        warranty_data,
        colWidths=[
            55 * mm,
            105 * mm,
        ],
    )

    warranty_table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.lightgrey,
                ),
                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold",
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.grey,
                ),
                (
                    "PADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),
            ]
        )
    )

    story.append(warranty_table)

    # -------------------------------------------------
    # HEALTH SUMMARY
    # -------------------------------------------------

    story.append(
        Paragraph(
            "Health Summary",
            section_style,
        )
    )

    health_data = [
        ["Metric", "Value"],
        [
            "Latest Health Score",
            str(
                report["latest_health_score"]
                if report["latest_health_score"] is not None
                else "-"
            ),
        ],
        [
            "Latest Health Status",
            report["latest_health_status"] or "-",
        ],
        [
            "Total Inspections",
            str(report["total_inspections"]),
        ],
        [
            "Maintenance Records",
            str(report["total_maintenance_records"]),
        ],
    ]

    health_table = Table(
        health_data,
        colWidths=[
            80 * mm,
            80 * mm,
        ],
    )

    health_table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.lightgrey,
                ),
                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold",
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.grey,
                ),
                (
                    "PADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),
            ]
        )
    )

    story.append(health_table)

    # -------------------------------------------------
    # INSPECTION HISTORY
    # -------------------------------------------------

    story.append(
        PageBreak()
    )

    story.append(
        Paragraph(
            "Inspection History",
            section_style,
        )
    )

    inspections = report["inspections"]

    if inspections:
        inspection_data = [
            [
                "Date",
                "Health",
                "Status",
                "Temp",
                "Voltage",
                "Cycles",
            ]
        ]

        for inspection in inspections:
            inspection_data.append(
                [
                    str(inspection.inspection_date),
                    str(inspection.health_score),
                    inspection.health_status,
                    str(inspection.temperature),
                    str(inspection.voltage),
                    str(inspection.cycle_count),
                ]
            )

        inspection_table = Table(
            inspection_data,
            repeatRows=1,
            colWidths=[
                30 * mm,
                23 * mm,
                30 * mm,
                24 * mm,
                25 * mm,
                25 * mm,
            ],
        )

        inspection_table.setStyle(
            TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, 0),
                        colors.lightgrey,
                    ),
                    (
                        "FONTNAME",
                        (0, 0),
                        (-1, 0),
                        "Helvetica-Bold",
                    ),
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.5,
                        colors.grey,
                    ),
                    (
                        "FONTSIZE",
                        (0, 0),
                        (-1, -1),
                        8,
                    ),
                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "TOP",
                    ),
                    (
                        "PADDING",
                        (0, 0),
                        (-1, -1),
                        4,
                    ),
                ]
            )
        )

        story.append(inspection_table)

    else:
        story.append(
            Paragraph(
                "No inspection records available.",
                styles["Normal"],
            )
        )

    # -------------------------------------------------
    # MAINTENANCE HISTORY
    # -------------------------------------------------

    story.append(
        Paragraph(
            "Maintenance History",
            section_style,
        )
    )

    maintenance_records = report["maintenance_records"]

    if maintenance_records:
        maintenance_data = [
            [
                "Type",
                "Status",
                "Scheduled",
                "Completed",
                "Cost",
            ]
        ]

        for maintenance in maintenance_records:
            maintenance_data.append(
                [
                    maintenance.maintenance_type,
                    maintenance.status,
                    str(maintenance.scheduled_date),
                    str(
                        maintenance.completed_date
                        or "-"
                    ),
                    str(
                        maintenance.cost
                        if maintenance.cost is not None
                        else "-"
                    ),
                ]
            )

        maintenance_table = Table(
            maintenance_data,
            repeatRows=1,
            colWidths=[
                45 * mm,
                30 * mm,
                32 * mm,
                32 * mm,
                25 * mm,
            ],
        )

        maintenance_table.setStyle(
            TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, 0),
                        colors.lightgrey,
                    ),
                    (
                        "FONTNAME",
                        (0, 0),
                        (-1, 0),
                        "Helvetica-Bold",
                    ),
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.5,
                        colors.grey,
                    ),
                    (
                        "FONTSIZE",
                        (0, 0),
                        (-1, -1),
                        8,
                    ),
                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "TOP",
                    ),
                    (
                        "PADDING",
                        (0, 0),
                        (-1, -1),
                        4,
                    ),
                ]
            )
        )

        story.append(maintenance_table)

    else:
        story.append(
            Paragraph(
                "No maintenance records available.",
                styles["Normal"],
            )
        )

    # -------------------------------------------------
    # BUILD PDF
    # -------------------------------------------------

    document.build(story)

    return pdf_path