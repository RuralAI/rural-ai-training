#!/usr/bin/env python3
"""Generate a donor-facing PDF for The Center for Rural AI (CRAI)."""

from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak,
    KeepTogether,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT

# ── Colours ──────────────────────────────────────────────────────────────────
GREEN_DARK = HexColor("#1a5d1a")
GREEN_MED = HexColor("#4a7c2e")
GREEN_LIGHT = HexColor("#e8f5e9")
ACCENT = HexColor("#e94560")
BLACK = HexColor("#1e1e1e")
GREY = HexColor("#646464")
WHITE = HexColor("#ffffff")

WIDTH, HEIGHT = A4


def _styles():
    """Return a dict of custom paragraph styles."""
    ss = getSampleStyleSheet()
    return {
        "cover_title": ParagraphStyle(
            "cover_title", parent=ss["Title"],
            fontSize=30, leading=36, textColor=WHITE, alignment=TA_CENTER,
            spaceAfter=6,
        ),
        "cover_sub": ParagraphStyle(
            "cover_sub", parent=ss["Normal"],
            fontSize=14, leading=18, textColor=HexColor("#c8e6c8"),
            alignment=TA_CENTER, spaceAfter=4,
        ),
        "cover_tag": ParagraphStyle(
            "cover_tag", parent=ss["Normal"],
            fontSize=11, leading=14, textColor=HexColor("#b4d2b4"),
            alignment=TA_CENTER, fontName="Helvetica-Oblique",
        ),
        "section": ParagraphStyle(
            "section", parent=ss["Heading1"],
            fontSize=18, leading=22, textColor=GREEN_DARK,
            spaceBefore=18, spaceAfter=8,
            borderWidth=0, borderPadding=0,
        ),
        "body": ParagraphStyle(
            "body", parent=ss["Normal"],
            fontSize=10.5, leading=15, textColor=BLACK, spaceAfter=6,
        ),
        "body_center": ParagraphStyle(
            "body_center", parent=ss["Normal"],
            fontSize=10.5, leading=15, textColor=BLACK, spaceAfter=6,
            alignment=TA_CENTER,
        ),
        "bullet": ParagraphStyle(
            "bullet", parent=ss["Normal"],
            fontSize=10.5, leading=15, textColor=BLACK,
            leftIndent=18, bulletIndent=6, spaceAfter=3,
            bulletFontName="Helvetica", bulletFontSize=10.5,
        ),
        "sub_heading": ParagraphStyle(
            "sub_heading", parent=ss["Heading2"],
            fontSize=13, leading=17, textColor=GREEN_DARK,
            spaceBefore=10, spaceAfter=4,
        ),
        "program_heading": ParagraphStyle(
            "program_heading", parent=ss["Heading2"],
            fontSize=12, leading=16, textColor=GREEN_DARK,
            spaceBefore=8, spaceAfter=3,
            fontName="Helvetica-Bold",
        ),
        "stat_val": ParagraphStyle(
            "stat_val", parent=ss["Normal"],
            fontSize=18, leading=22, textColor=GREEN_DARK,
            alignment=TA_CENTER, fontName="Helvetica-Bold",
        ),
        "stat_label": ParagraphStyle(
            "stat_label", parent=ss["Normal"],
            fontSize=9, leading=11, textColor=GREY,
            alignment=TA_CENTER,
        ),
        "closing": ParagraphStyle(
            "closing", parent=ss["Normal"],
            fontSize=12, leading=17, textColor=GREEN_DARK,
            alignment=TA_CENTER, fontName="Helvetica-Oblique",
        ),
        "link": ParagraphStyle(
            "link", parent=ss["Normal"],
            fontSize=12, leading=16, textColor=GREEN_DARK,
            alignment=TA_CENTER, fontName="Helvetica-Bold", spaceAfter=4,
        ),
    }


def _stat_table(stats, styles):
    """Build a stat-box row as a Table."""
    val_row = [Paragraph(v, styles["stat_val"]) for _, v in stats]
    lbl_row = [Paragraph(l, styles["stat_label"]) for l, _ in stats]
    t = Table([val_row, lbl_row], colWidths=[42 * mm] * len(stats))
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), GREEN_LIGHT),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, 0), 8),
        ("BOTTOMPADDING", (0, -1), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
    ]))
    return t


def _cover_bg(canvas, doc):
    """Draw the green cover banner."""
    canvas.saveState()
    canvas.setFillColor(GREEN_DARK)
    canvas.rect(0, HEIGHT - 110 * mm, WIDTH, 110 * mm, fill=True, stroke=False)
    canvas.restoreState()


def _normal_page(canvas, doc):
    """Header/footer for non-cover pages."""
    canvas.saveState()
    canvas.setStrokeColor(GREEN_LIGHT)
    canvas.setLineWidth(0.5)
    canvas.line(20 * mm, HEIGHT - 12 * mm, WIDTH - 20 * mm, HEIGHT - 12 * mm)
    canvas.setFont("Helvetica-Oblique", 8)
    canvas.setFillColor(GREY)
    canvas.drawRightString(
        WIDTH - 20 * mm, HEIGHT - 10 * mm,
        "The Center for Rural AI \u2014 Philanthropic Partnership",
    )
    canvas.setFont("Helvetica-Oblique", 8)
    canvas.drawCentredString(WIDTH / 2, 10 * mm, f"Page {doc.page}")
    canvas.restoreState()


def build_pdf(output_path="donor_materials.pdf"):
    doc = SimpleDocTemplate(
        output_path, pagesize=A4,
        topMargin=20 * mm, bottomMargin=20 * mm,
        leftMargin=20 * mm, rightMargin=20 * mm,
    )
    S = _styles()
    story = []

    # ── Page 1: Cover ────────────────────────────────────────────────────────
    story.append(Spacer(1, 25 * mm))
    story.append(Paragraph("The Center for Rural AI", S["cover_title"]))
    story.append(Spacer(1, 4 * mm))
    story.append(Paragraph(
        "Building Rural Capacity in the AI Economy", S["cover_sub"],
    ))
    story.append(Spacer(1, 8 * mm))
    story.append(Paragraph("Philanthropic Partnership", S["cover_tag"]))
    story.append(Spacer(1, 20 * mm))

    stats = [
        ("Rural Americans", "60M+"),
        ("Share of U.S. GDP", "10%+"),
        ("Partnership Ask", "$5M"),
        ("Timeline", "24 Mo"),
    ]
    story.append(_stat_table(stats, S))
    story.append(Spacer(1, 12 * mm))

    story.append(Paragraph(
        "The Center for Rural AI (CRAI) is a newly formed 501(c)(3) nonprofit "
        "focused on a structural economic disparity in the United States: the "
        "lagging participation of rural communities in artificial intelligence.",
        S["body_center"],
    ))
    story.append(Spacer(1, 10 * mm))
    story.append(Paragraph("ruralai.org", S["link"]))
    story.append(PageBreak())

    # ── Page 2: About CRAI ───────────────────────────────────────────────────
    story.append(Paragraph("About CRAI", S["section"]))
    story.append(Paragraph(
        "Rural America comprises a significant portion of the nation\u2019s "
        "population and economy, yet it has historically lagged in access to "
        "digital infrastructure, tech jobs, and innovation networks. The rise "
        "of AI has exacerbated these challenges.",
        S["body"],
    ))
    story.append(Paragraph(
        "Over 60 million citizens live in rural areas. Rural ecosystems "
        "contribute over 10% of U.S. GDP but are underrepresented in "
        "high-growth tech sectors compared with urban regions.",
        S["body"],
    ))
    story.append(Paragraph(
        "CRAI exists to shift this trajectory by building the institutional "
        "capacity rural regions need to adopt, deploy, and influence AI "
        "systems in ways that create economic opportunities and enhance "
        "community outcomes. Global economic analyses project that AI and "
        "related technologies will generate tens of trillions of dollars in "
        "value across industries by 2030 \u2014 we want to enable rural "
        "communities to capture their share.",
        S["body"],
    ))

    story.append(Spacer(1, 4 * mm))
    story.append(Paragraph("Founding Team", S["sub_heading"]))
    story.append(Paragraph(
        "<b>Andrew Aitken, Executive Director</b> \u2014 Has advised "
        "institutions including the U.S. White House, Microsoft, and Capital "
        "One, and has served on the boards of numerous technology foundations.",
        S["body"],
    ))
    story.append(Paragraph(
        "<b>Adam Markham, Technology Adviser</b> \u2014 Has directed AI "
        "research and systems engineering in government and critical "
        "infrastructure contexts.",
        S["body"],
    ))
    story.append(Paragraph(
        "<b>Marc Nager, Adviser</b> \u2014 Co-founded Startup Weekend and "
        "led community programs at Techstars; partner at one of the only "
        "VCs focused on rural ecosystems.",
        S["body"],
    ))

    story.append(Spacer(1, 4 * mm))
    story.append(Paragraph("Strategic Partnerships", S["sub_heading"]))
    story.append(Paragraph(
        "CRAI and the AI Institute at Fort Lewis College in Durango, "
        "Colorado \u2014 a rural public institution advancing comprehensive "
        "AI education and engagement \u2014 have initiated discussions on "
        "collaborative pathways. This provides direct insight into the "
        "opportunities and constraints rural institutions face. In parallel, "
        "CRAI is engaging with frontier AI companies so that rural use cases "
        "inform product design while the technology is still evolving.",
        S["body"],
    ))

    story.append(PageBreak())

    # ── Page 3: The Investment Thesis ─────────────────────────────────────────
    story.append(Paragraph("The Investment Thesis", S["section"]))
    story.append(Paragraph(
        "Rural regions possess underutilized competitive advantages, "
        "including lower operating costs, stronger long-term community "
        "retention, and rich real-world data environments in agriculture, "
        "healthcare, and logistics that are relevant to AI use cases. While "
        "rural communities have these strengths, persistent training, "
        "infrastructure, and digital adoption gaps curtail their ability to "
        "participate at scale in the emerging AI economy.",
        S["body"],
    ))
    story.append(Spacer(1, 4 * mm))
    story.append(Paragraph(
        "Federal Policy Alignment", S["sub_heading"],
    ))
    story.append(Paragraph(
        "Federal policy is increasingly aligned with addressing regional "
        "disparities. The CHIPS and Science Act and related place-based "
        "programs authorized under it are designed to build technology "
        "capacity and innovation ecosystems outside of traditional tech "
        "centers. The Regional Technology and Innovation Hubs (Tech Hubs) "
        "program, for example, directs up to ~$10 billion over five years "
        "to support distributed technology innovation networks across the "
        "U.S., with appropriated funding already underway. Such federal "
        "initiatives provide structural support for innovation ecosystems "
        "that include rural and underserved communities.",
        S["body"],
    ))

    story.append(PageBreak())

    # ── Pages 4-5: Our Programs ──────────────────────────────────────────────
    story.append(Paragraph("Our Programs", S["section"]))

    # AI 101
    story.append(Paragraph(
        "AI 101 \u2014 Artificial Intelligence for Rural Communities (Q1/26)",
        S["program_heading"],
    ))
    story.append(Paragraph(
        "A plain-language, hands-on half-day workshop designed for small "
        "business owners, municipal staff, nonprofit leaders, farmers, and "
        "anyone serving a rural community \u2014 no technical background "
        "required. Participants leave with:",
        S["body"],
    ))
    for b in [
        "A working understanding of what AI is and where it falls short",
        "Hands-on practice using real tools on tasks they actually face",
        "A personal 30-day action plan tailored to their specific context",
    ]:
        story.append(Paragraph(b, S["bullet"], bulletText="\u2022"))

    story.append(Spacer(1, 2 * mm))

    # AI Ignition
    story.append(Paragraph(
        "AI Ignition (Q2/26)", S["program_heading"],
    ))
    story.append(Paragraph(
        "A capacity-building initiative for rural higher education "
        "institutions and nonprofits. It begins with AI readiness "
        "assessments to identify high-impact, low-risk opportunities, and "
        "then advances to focused 90-day pilots that deliver measurable "
        "outcomes in student engagement, operational performance, and "
        "service delivery.",
        S["body"],
    ))

    # Rural AI Innovation & Training Lab
    story.append(Paragraph(
        "Rural AI Innovation &amp; Training Lab (Q3/26)",
        S["program_heading"],
    ))
    story.append(Paragraph(
        "The first program of its kind in the United States \u2014 a "
        "physical lab and structured training infrastructure hosted at the "
        "Fort Lewis College Innovation Center. Each 90-day cohort trains "
        "approximately 15 faculty, staff, and institutional leaders from "
        "rural colleges, tribal institutions, and mission-aligned nonprofits "
        "to serve as internal AI evangelists at their home organizations.",
        S["body"],
    ))
    story.append(Paragraph(
        "The program structure blends an intensive in-person launch week, "
        "a remote applied-pilot phase, and an in-person capstone week to "
        "finalize deployments, document outcomes, and produce repeatable "
        "playbooks. Each cohort indirectly influences more than 5,000 "
        "students annually through the institutional multiplier effect.",
        S["body"],
    ))
    story.append(Paragraph(
        "The Lab also convenes AI builders for time-bound, structured "
        "field engagements that produce jointly published use cases and "
        "generate rural deployment insights that directly inform model "
        "development and tooling priorities.",
        S["body"],
    ))

    # Peer Council
    story.append(Paragraph(
        "Peer Council (Q2/26)", S["program_heading"],
    ))
    story.append(Paragraph(
        "A shared network and knowledge library where participating "
        "institutions exchange tested use cases, tools, and insights from "
        "deployments. This collective repository cultivates durable "
        "institutional knowledge within the rural ecosystem.",
        S["body"],
    ))

    # AI in the Mountains Summit
    story.append(Paragraph(
        "AI in the Mountains Summit (Q4/26)", S["program_heading"],
    ))
    story.append(Paragraph(
        "An annual convening hosted in rotating rural mountain towns, "
        "bringing together AI researchers, policymakers, corporate "
        "partners, and rural stakeholders to ensure rural perspectives "
        "shape national and regional AI strategies.",
        S["body"],
    ))

    # AI Fluency Platform
    story.append(Paragraph(
        "The AI Fluency Platform (Q2/26)", S["program_heading"],
    ))
    story.append(Paragraph(
        "Role-specific AI education tailored to rural institutional "
        "contexts. Built around an agentic content orchestration platform "
        "that contextualizes learning for real operational environments, "
        "this curriculum will generate usable intellectual property and "
        "scalable implementation beyond pilot phases.",
        S["body"],
    ))

    story.append(PageBreak())

    # ── Page 6: Why Philanthropic Capital Matters + Our Invitation ────────────
    story.append(Paragraph("Why Philanthropic Capital Matters", S["section"]))
    story.append(Paragraph(
        "Federal and corporate investment tends to follow demonstrated "
        "results; it rarely initiates them. Early philanthropic capital is "
        "essential to fund assessments, pilots, resources, technology "
        "infrastructure, and baseline operating capacity that generate the "
        "evidence of impact required to unlock scalable public and private "
        "funding streams. Without this initial support, promising rural AI "
        "adoption efforts may fail to reach the proof points needed to "
        "secure continued investment.",
        S["body"],
    ))

    story.append(Spacer(1, 6 * mm))
    story.append(Paragraph("Our Invitation", S["section"]))
    story.append(Paragraph(
        "CRAI seeks <b>$5,000,000 in philanthropic partnership over "
        "24 months</b> to launch core programs, demonstrate impact across "
        "8\u201312 partner institutions, build foundational infrastructure, "
        "and position for access to federal funding beginning in 2027.",
        S["body"],
    ))
    story.append(Spacer(1, 2 * mm))
    story.append(Paragraph("This investment will support:", S["body"]))
    for b in [
        "AI Ignition pilots at 8\u201310 rural higher education institutions",
        "Launch of the AI Innovation and Training Lab",
        "Development and deployment of the AI Fluency agentic curriculum "
        "platform",
        "Launch of the 2026 AI in the Mountains Summit",
        "Core operations and strategic partnerships",
    ]:
        story.append(Paragraph(b, S["bullet"], bulletText="\u2022"))

    story.append(Spacer(1, 8 * mm))

    # Closing box
    closing_text = Paragraph(
        "If this opportunity resonates, we welcome a conversation about "
        "how your partnership can help ensure rural communities lead, "
        "not follow, in the AI economy.",
        S["closing"],
    )
    closing_table = Table([[closing_text]], colWidths=[150 * mm])
    closing_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), GREEN_LIGHT),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 12),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
    ]))
    story.append(closing_table)

    story.append(Spacer(1, 8 * mm))
    story.append(Paragraph(
        "<b>Andrew Aitken</b> \u2014 Executive Director, "
        "The Center for Rural AI",
        S["body_center"],
    ))
    story.append(Paragraph(
        "andrew@ruralai.org  |  ruralai.org", S["link"],
    ))

    # ── Build ────────────────────────────────────────────────────────────────
    doc.build(
        story,
        onFirstPage=_cover_bg,
        onLaterPages=_normal_page,
    )
    print(f"Donor PDF generated: {output_path}")


if __name__ == "__main__":
    build_pdf()
