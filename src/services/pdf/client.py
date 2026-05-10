import re

from datetime import datetime

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    PageBreak
)

from reportlab.lib.styles import (
    getSampleStyleSheet,
    ParagraphStyle
)

from reportlab.lib.enums import (
    TA_CENTER,
    TA_JUSTIFY
)

from reportlab.lib.pagesizes import letter

from reportlab.lib import colors

from reportlab.platypus.flowables import (
    HRFlowable
)

from src.utils.logger import logger


# ---------------------------------------------------
# CLEAN TEXT
# ---------------------------------------------------

def clean_text(text):

    text = text.replace("```", "")

    text = text.replace("**", "")

    return text.strip()


# ---------------------------------------------------
# PAGE NUMBER
# ---------------------------------------------------

def add_page_number(canvas, doc):

    canvas.setFont(
        "Helvetica",
        9
    )

    canvas.setFillColor(
        colors.grey
    )

    canvas.drawRightString(
        570,
        20,
        f"Page {canvas.getPageNumber()}"
    )


# ---------------------------------------------------
# PDF GENERATOR
# ---------------------------------------------------

def generate_pdf(
    topic,
    report_text,
    output_path
):

    try:

        doc = SimpleDocTemplate(
            output_path,

            pagesize=letter,

            rightMargin=60,
            leftMargin=60,

            topMargin=55,
            bottomMargin=45
        )

        styles = getSampleStyleSheet()

        # ---------------------------------------------------
        # TITLE STYLE
        # ---------------------------------------------------

        title_style = ParagraphStyle(
            "TitleStyle",

            parent=styles["Title"],

            fontName="Helvetica-Bold",

            fontSize=30,

            leading=36,

            alignment=TA_CENTER,

            textColor=colors.HexColor(
                "#163A5F"
            ),

            spaceAfter=20
        )

        # ---------------------------------------------------
        # SUBTITLE
        # ---------------------------------------------------

        subtitle_style = ParagraphStyle(
            "SubtitleStyle",

            parent=styles["BodyText"],

            fontSize=12,

            alignment=TA_CENTER,

            textColor=colors.grey
        )

        # ---------------------------------------------------
        # MAIN HEADING
        # ---------------------------------------------------

        heading_style = ParagraphStyle(
            "HeadingStyle",

            parent=styles["Heading1"],

            fontName="Helvetica-Bold",

            fontSize=24,

            leading=30,

            textColor=colors.HexColor(
                "#163A5F"
            ),

            spaceBefore=30,

            spaceAfter=14
        )

        # ---------------------------------------------------
        # SUBHEADING
        # ---------------------------------------------------

        subheading_style = ParagraphStyle(
            "SubheadingStyle",

            parent=styles["Heading2"],

            fontName="Helvetica-Bold",

            fontSize=15,

            leading=22,

            textColor=colors.HexColor(
                "#365C7A"
            ),

            spaceBefore=18,

            spaceAfter=8
        )

        # ---------------------------------------------------
        # BODY STYLE
        # ---------------------------------------------------

        body_style = ParagraphStyle(
            "BodyStyle",

            parent=styles["BodyText"],

            fontName="Helvetica",

            fontSize=11.5,

            leading=22,

            alignment=TA_JUSTIFY,

            textColor=colors.black,

            spaceAfter=12
        )

        elements = []

        # ---------------------------------------------------
        # COVER PAGE
        # ---------------------------------------------------

        elements.append(
            Spacer(1, 200)
        )

        elements.append(
            Paragraph(
                topic,
                title_style
            )
        )

        elements.append(
            Spacer(1, 20)
        )

        elements.append(
            Paragraph(
                "Executive AI Report",
                subtitle_style
            )
        )

        elements.append(
            Spacer(1, 12)
        )

        elements.append(
            Paragraph(
                datetime.now().strftime(
                    "%B %d, %Y"
                ),
                subtitle_style
            )
        )

        elements.append(
            PageBreak()
        )

        # ---------------------------------------------------
        # CONTENT
        # ---------------------------------------------------

        lines = report_text.split("\n")

        for line in lines:

            line = clean_text(line)

            if not line.strip():

                elements.append(
                    Spacer(1, 8)
                )

                continue

            # Main Heading

            if line.startswith("# "):

                heading = line.replace(
                    "# ",
                    ""
                )

                elements.append(
                    Paragraph(
                        heading,
                        heading_style
                    )
                )

                elements.append(
                    HRFlowable(
                        width="100%",
                        thickness=1,
                        color=colors.HexColor(
                            "#D9D9D9"
                        )
                    )
                )

                elements.append(
                    Spacer(1, 10)
                )

            # Subheading

            elif line.startswith("## "):

                subheading = line.replace(
                    "## ",
                    ""
                )

                elements.append(
                    Paragraph(
                        subheading,
                        subheading_style
                    )
                )

            # Ignore references completely

            elif "References" in line:

                continue

            elif "Source" in line:

                continue

            elif "http" in line:

                continue

            # Body

            else:

                elements.append(
                    Paragraph(
                        line,
                        body_style
                    )
                )

        # ---------------------------------------------------
        # BUILD
        # ---------------------------------------------------

        doc.build(
            elements,

            onFirstPage=add_page_number,

            onLaterPages=add_page_number
        )

        logger.info(
            f"Premium PDF generated: {output_path}"
        )

    except Exception as e:

        logger.error(
            f"PDF generation failed: {e}"
        )

        raise