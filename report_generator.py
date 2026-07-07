from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer
)

from reportlab.lib.styles import getSampleStyleSheet

from datetime import datetime


def generate_report(
    report_path,
    evidence,
    custody_records
):

    doc = SimpleDocTemplate(report_path)

    styles = getSampleStyleSheet()

    content = []

    content.append(
        Paragraph(
            "Digital Forensic Evidence Report",
            styles["Title"]
        )
    )

    content.append(
        Spacer(1,12)
    )

    content.append(
        Paragraph(
            f"Generated: {datetime.now()}",
            styles["Normal"]
        )
    )

    content.append(
        Spacer(1,12)
    )

    content.append(
        Paragraph(
            "<b>Evidence Details</b>",
            styles["Heading2"]
        )
    )

    for item in evidence:

        content.append(
            Paragraph(
                str(item),
                styles["Normal"]
            )
        )

    content.append(
        Spacer(1,12)
    )

    content.append(
        Paragraph(
            "<b>Chain of Custody</b>",
            styles["Heading2"]
        )
    )

    for record in custody_records:

        content.append(
            Paragraph(
                str(record),
                styles["Normal"]
            )
        )

    doc.build(content)

    return report_path