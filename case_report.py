import sqlite3
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
DB = "forensic.db"

def generate_case_report(case_id, filename):
    conn = sqlite3.connect(DB)
    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(filename)
    story = []
    case = conn.execute("""
            SELECT *
            FROM cases
            WHERE case_id=?
            """,(case_id,)).fetchone()
    story.append(
        Paragraph(
            "<b>Digital Forensic Investigation Report</b>",
            styles["Title"]
        )
    )
    story.append(Spacer(1,20))
    story.append(
        Paragraph(f"<b>Case ID:</b> {case[1]}",styles["BodyText"])
    )
    story.append(
        Paragraph(f"<b>Case Name:</b> {case[2]}",styles["BodyText"])
    )
    story.append(
        Paragraph(f"<b>Investigator:</b> {case[4]}",styles["BodyText"])
    )
    story.append(
        Paragraph(f"<b>Priority:</b> {case[5]}",styles["BodyText"])
    )
    story.append(
        Paragraph(f"<b>Status:</b> {case[6]}",styles["BodyText"])
    )
    story.append(Spacer(1,20))

    evidence = conn.execute("""
    SELECT
        id,
        title,
        filename,
        uploaded_by,
        sha256
    FROM evidence
    WHERE case_id=?
    """,(case_id,)).fetchall()

    data = [
        [
            "ID",
            "Title",
            "Filename",
            "Uploaded By",
            "SHA256"
        ]
    ]

    for e in evidence:
        data.append([
            e[0],
            e[1],
            e[2],
            e[3],
            e[4][:25]+"..."
        ])

    table = Table(data)
    table.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0),colors.darkblue),
        ("TEXTCOLOR",(0,0),(-1,0),colors.white),
        ("GRID",(0,0),(-1,-1),1,colors.black),
        ("BACKGROUND",(0,1),(-1,-1),colors.beige),
        ("FONTSIZE",(0,0),(-1,-1),8),
        ("BOTTOMPADDING",(0,0),(-1,0),10)
    ]))
    story.append(table)
    story.append(Spacer(1,20))

    custody = conn.execute("""
    SELECT
        timestamp,
        action,
        person
    FROM custody
    WHERE evidence_id IN(
        SELECT id
        FROM evidence
        WHERE case_id=?
    )
    ORDER BY timestamp
    """,(case_id,)).fetchall()

    story.append(
        Paragraph(
            "<b>Chain of Custody</b>",
            styles["Heading2"]
        )
    )

    for c in custody:
        story.append(
            Paragraph(
                f"{c[0]} | {c[1]} | {c[2]}",
                styles["BodyText"]
            )
        )

    verification = conn.execute("""
    SELECT
        verification_time,
        verified_by,
        status
    FROM verification_logs
    WHERE evidence_id IN(
        SELECT id
        FROM evidence
        WHERE case_id=?
    )
    """,(case_id,)).fetchall()
    story.append(
        Spacer(1,20)
    )
    story.append(
        Paragraph(
            "<b>Verification History</b>",
            styles["Heading2"]
        )
    )
    for v in verification:
        story.append(
            Paragraph(
                f"{v[0]} | {v[1]} | {v[2]}",
                styles["BodyText"]
            )
        )

    alerts = conn.execute("""
    SELECT
        detection_time,
        severity,
        status
    FROM tamper_alerts
    WHERE evidence_id IN(
        SELECT id
        FROM evidence
        WHERE case_id=?
    )
    """,(case_id,)).fetchall()

    story.append(
        Spacer(1,20)
    )
    story.append(
        Paragraph(
            "<b>Tamper Alerts</b>",
            styles["Heading2"]
        )
    )
    if alerts:
        for a in alerts:
            story.append(
                Paragraph(
                    f"{a[0]} | {a[1]} | {a[2]}",
                    styles["BodyText"]
                )
            )
    else:
        story.append(
            Paragraph(
                "No tamper alerts detected.",
                styles["BodyText"]
            )
        )

    conn.close()
    doc.build(story)