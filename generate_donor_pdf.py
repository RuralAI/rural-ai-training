#!/usr/bin/env python3
"""Generate a donor-facing PDF from Rural AI Training project materials."""

from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import Color, HexColor
from reportlab.lib.units import mm, cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak,
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
            fontSize=11, leading=16, textColor=BLACK, spaceAfter=6,
        ),
        "body_center": ParagraphStyle(
            "body_center", parent=ss["Normal"],
            fontSize=11, leading=16, textColor=BLACK, spaceAfter=6,
            alignment=TA_CENTER,
        ),
        "bullet": ParagraphStyle(
            "bullet", parent=ss["Normal"],
            fontSize=11, leading=16, textColor=BLACK,
            leftIndent=18, bulletIndent=6, spaceAfter=3,
            bulletFontName="Helvetica", bulletFontSize=11,
        ),
        "sub_heading": ParagraphStyle(
            "sub_heading", parent=ss["Heading2"],
            fontSize=13, leading=17, textColor=GREEN_DARK,
            spaceBefore=12, spaceAfter=4,
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
        "domain_name": ParagraphStyle(
            "domain_name", parent=ss["Normal"],
            fontSize=10, leading=14, textColor=GREEN_DARK,
            fontName="Helvetica-Bold",
        ),
        "domain_desc": ParagraphStyle(
            "domain_desc", parent=ss["Normal"],
            fontSize=10, leading=14, textColor=GREY,
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
        "step_num": ParagraphStyle(
            "step_num", parent=ss["Normal"],
            fontSize=12, leading=16, textColor=ACCENT,
            fontName="Helvetica-Bold",
        ),
    }


def _stat_table(stats, styles):
    """Build a stat-box row as a Table."""
    val_row = [Paragraph(v, styles["stat_val"]) for _, v in stats]
    lbl_row = [Paragraph(l, styles["stat_label"]) for l, _ in stats]
    t = Table([val_row, lbl_row], colWidths=[42*mm]*len(stats))
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


def _domain_table(domains, styles):
    """Build a two-column domain table."""
    data = [
        [Paragraph(n, styles["domain_name"]), Paragraph(d, styles["domain_desc"])]
        for n, d in domains
    ]
    t = Table(data, colWidths=[55*mm, 110*mm])
    t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LINEBELOW", (0, 0), (-1, -2), 0.3, HexColor("#e0e0e0")),
    ]))
    return t


def _cover_bg(canvas, doc):
    """Draw the green cover banner."""
    canvas.saveState()
    canvas.setFillColor(GREEN_DARK)
    canvas.rect(0, HEIGHT - 110*mm, WIDTH, 110*mm, fill=True, stroke=False)
    canvas.restoreState()


def _normal_page(canvas, doc):
    """Header/footer for non-cover pages."""
    canvas.saveState()
    # Header line
    canvas.setStrokeColor(GREEN_LIGHT)
    canvas.setLineWidth(0.5)
    canvas.line(20*mm, HEIGHT - 12*mm, WIDTH - 20*mm, HEIGHT - 12*mm)
    canvas.setFont("Helvetica-Oblique", 8)
    canvas.setFillColor(GREY)
    canvas.drawRightString(WIDTH - 20*mm, HEIGHT - 10*mm,
                           "Rural AI Training -- Donor Information")
    # Footer
    canvas.setFont("Helvetica-Oblique", 8)
    canvas.drawCentredString(WIDTH / 2, 10*mm, f"Page {doc.page}")
    canvas.restoreState()


def build_pdf(output_path="donor_materials.pdf"):
    doc = SimpleDocTemplate(
        output_path, pagesize=A4,
        topMargin=20*mm, bottomMargin=20*mm,
        leftMargin=20*mm, rightMargin=20*mm,
    )
    S = _styles()
    story = []

    # ── Page 1: Cover ────────────────────────────────────────────────────────
    story.append(Spacer(1, 25*mm))
    story.append(Paragraph("Rural AI Training", S["cover_title"]))
    story.append(Spacer(1, 4*mm))
    story.append(Paragraph("Free and Open-Source AI Education", S["cover_sub"]))
    story.append(Paragraph("for Rural Communities", S["cover_sub"]))
    story.append(Spacer(1, 8*mm))
    story.append(Paragraph("Donor Information Package", S["cover_tag"]))
    story.append(Spacer(1, 20*mm))

    stats = [("Resources", "269+"), ("Modules", "3"),
             ("Hours", "10.7"), ("Datasets", "9")]
    story.append(_stat_table(stats, S))
    story.append(Spacer(1, 12*mm))

    story.append(Paragraph(
        "Rural AI Training is an open-source initiative that brings free, high-quality "
        "artificial intelligence and machine learning education to rural communities "
        "worldwide. Our platform bridges the digital divide by providing curated "
        "learning resources, hands-on courses, and real-world projects contextualized "
        "for agriculture, rural healthcare, and community development.",
        S["body_center"],
    ))
    story.append(Spacer(1, 10*mm))
    story.append(Paragraph("github.com/RuralAI/rural-ai-training", S["link"]))
    story.append(PageBreak())

    # ── Page 2: The Challenge & Our Solution ─────────────────────────────────
    story.append(Paragraph("The Challenge", S["section"]))
    story.append(Paragraph(
        "Rural communities face unique barriers to participating in the AI revolution:",
        S["body"],
    ))
    for b in [
        "Limited access to technology experts and mentors",
        "Vast land areas requiring monitoring with minimal staff",
        "Weather-dependent livelihoods that could benefit from predictive models",
        "Resource constraints that make paid training programmes inaccessible",
        "Existing AI education uses urban-centric examples (stock trading, ride-sharing) "
        "that feel irrelevant to rural learners",
    ]:
        story.append(Paragraph(b, S["bullet"], bulletText="\u2022"))

    story.append(Spacer(1, 6*mm))
    story.append(Paragraph("Our Solution", S["section"]))
    story.append(Paragraph(
        "Rural AI Training provides a complete, free learning platform with two core components:",
        S["body"],
    ))

    story.append(Paragraph("1. AI Resource Catalog", S["sub_heading"]))
    story.append(Paragraph(
        "A searchable catalog of 269+ free AI training resources aggregated from GitHub, "
        "arXiv, and across the web. Learners can filter by domain (machine learning, NLP, "
        "computer vision, and more), difficulty level, and content type (tutorials, "
        "notebooks, courses, and papers).",
        S["body"],
    ))

    story.append(Paragraph("2. ML Basics -- Rural Edition Course", S["sub_heading"]))
    story.append(Paragraph(
        "A structured, beginner-friendly machine learning course that teaches "
        "fundamental concepts through rural-specific applications:",
        S["body"],
    ))
    for prefix, text in [
        ("<b>Agriculture:</b> ", "Crop yield prediction"),
        ("<b>Livestock:</b> ", "Livestock health monitoring and classification"),
        ("<b>Land Management:</b> ", "Soil analysis and irrigation optimisation"),
        ("<b>Economics:</b> ", "Market price forecasting for agricultural commodities"),
    ]:
        story.append(Paragraph(prefix + text, S["bullet"], bulletText="\u2022"))

    story.append(PageBreak())

    # ── Page 3: Curriculum Coverage ──────────────────────────────────────────
    story.append(Paragraph("Curriculum Coverage", S["section"]))
    story.append(Paragraph(
        "Our platform covers 13 AI skill domains, ensuring learners get "
        "comprehensive exposure to the field:",
        S["body"],
    ))
    story.append(Spacer(1, 4*mm))

    domains = [
        ("Machine Learning Fundamentals", "Core ML concepts adapted for rural contexts"),
        ("Deep Learning", "Neural networks, CNNs for image-based tasks"),
        ("Natural Language Processing", "Text analysis for agricultural reports and extension services"),
        ("Computer Vision", "Crop disease detection, livestock monitoring"),
        ("MLOps &amp; Production ML", "Deploying models in low-resource environments"),
        ("Generative AI", "LLMs and diffusion models for content generation"),
        ("Reinforcement Learning", "Optimisation for irrigation and resource allocation"),
        ("Data Engineering", "Building data pipelines from sensor and field data"),
        ("AI Strategy", "Planning AI adoption for rural organisations"),
        ("AI Ethics", "Responsible AI practices in community settings"),
        ("AI Project Management", "Managing AI initiatives with limited resources"),
        ("AI ROI", "Measuring return on investment for rural AI projects"),
        ("AI Governance", "Compliance and governance frameworks"),
    ]
    story.append(_domain_table(domains, S))

    story.append(PageBreak())

    # ── Page 4: How It Works ─────────────────────────────────────────────────
    story.append(Paragraph("How It Works", S["section"]))
    story.append(Paragraph(
        "The platform is built on an automated discovery and curation pipeline:",
        S["body"],
    ))
    story.append(Spacer(1, 4*mm))

    steps = [
        ("Discovery",
         "An automated agent searches GitHub, arXiv, and the web for free AI "
         "training content across all 13 skill domains."),
        ("Ingestion &amp; Analysis",
         "Discovered resources are scraped, de-duplicated, quality-scored, "
         "and categorised by domain, difficulty, and content type."),
        ("Curriculum Generation",
         "A structured curriculum is generated with learning paths, modules, "
         "and estimated completion times."),
        ("Rural Contextualisation",
         "Each module includes rural-specific use cases, datasets, and exercises "
         "that connect abstract AI concepts to real-world agricultural and "
         "community challenges."),
        ("Open Access",
         "Everything is published as static HTML and open-source code -- no server "
         "costs, no login required, works on any device with a web browser."),
    ]
    for i, (title, desc) in enumerate(steps, 1):
        story.append(Paragraph(
            f'<font color="{ACCENT.hexval()}">{i}.</font>  '
            f'<font color="{GREEN_DARK.hexval()}"><b>{title}</b></font>',
            S["body"],
        ))
        story.append(Paragraph(desc, S["body"]))
        story.append(Spacer(1, 2*mm))

    story.append(PageBreak())

    # ── Page 5: Course at a Glance ───────────────────────────────────────────
    story.append(Paragraph("Course at a Glance", S["section"]))
    story.append(Paragraph("ML Basics -- Beginner -- Rural Edition", S["body"]))
    story.append(Spacer(1, 4*mm))

    course_stats = [("Modules", "3"), ("Hours", "10.7"),
                    ("Datasets", "9"), ("Projects", "6")]
    story.append(_stat_table(course_stats, S))
    story.append(Spacer(1, 6*mm))

    story.append(Paragraph(
        "The course teaches machine learning fundamentals through three progressive "
        "modules, each grounded in rural applications. Learners work with real datasets "
        "and build projects that solve genuine community challenges.",
        S["body"],
    ))
    story.append(Spacer(1, 4*mm))
    story.append(Paragraph("Sample Rural Use Cases", S["sub_heading"]))

    use_cases = [
        ("Crop Yield Prediction",
         "Instead of predicting stock prices, learners build models to predict "
         "harvest yields based on weather, soil, and historical data."),
        ("Livestock Health Classification",
         "Image classification is taught through identifying healthy vs. diseased "
         "livestock rather than classifying cats and dogs."),
        ("Soil Analysis",
         "Regression and clustering concepts are applied to soil nutrient data "
         "to guide fertiliser decisions."),
        ("Market Price Forecasting",
         "Time series analysis is learned by forecasting commodity prices for "
         "local agricultural products."),
    ]
    for title, desc in use_cases:
        story.append(Paragraph(f"<b>{title}</b>", S["body"]))
        story.append(Paragraph(desc, S["body"]))

    story.append(PageBreak())

    # ── Page 6: Why Support Us ───────────────────────────────────────────────
    story.append(Paragraph("Why Support Rural AI Training?", S["section"]))

    reasons = [
        ("Bridge the Digital Divide",
         "AI is transforming every industry, but rural communities risk being left "
         "behind. Your support ensures that farmers, rural health workers, and "
         "community planners gain the skills to participate in the AI economy."),
        ("Measurable, Scalable Impact",
         "As a fully open-source platform, every dollar goes further. Content "
         "created once serves learners globally. Static HTML deployment means "
         "near-zero hosting costs and offline access capability."),
        ("Real-World Relevance",
         "Unlike generic AI courses, our materials are specifically contextualised "
         "for rural challenges. Learners don't just study theory -- they build "
         "solutions for their own communities."),
        ("Open Source &amp; Transparent",
         "All code, content, and curriculum are open source on GitHub. Donors "
         "can verify exactly how resources are used and what content is produced."),
        ("Community-Driven Growth",
         "The automated discovery pipeline continuously finds and curates new "
         "free resources, ensuring the platform grows and stays current without "
         "ongoing manual effort."),
    ]
    for title, desc in reasons:
        story.append(Paragraph(f"<b>{title}</b>", S["sub_heading"]))
        story.append(Paragraph(desc, S["body"]))

    story.append(PageBreak())

    # ── Page 7: How You Can Help ─────────────────────────────────────────────
    story.append(Paragraph("How You Can Help", S["section"]))

    help_items = [
        ("Financial Support",
         "Donations fund infrastructure, content development, community outreach, "
         "and translation of materials into local languages. Even modest contributions "
         "make a significant difference because our open-source model multiplies impact."),
        ("In-Kind Contributions",
         "We welcome subject matter experts who can review content, contribute "
         "rural-specific datasets, or help translate materials. Cloud computing "
         "credits and development tools also accelerate our work."),
        ("Partnerships",
         "We are seeking partnerships with agricultural organisations, rural development "
         "agencies, educational institutions, and technology companies to extend our "
         "reach and ensure our content addresses real community needs."),
    ]
    for title, desc in help_items:
        story.append(Paragraph(f"<b>{title}</b>", S["sub_heading"]))
        story.append(Paragraph(desc, S["body"]))

    story.append(Spacer(1, 8*mm))
    story.append(Paragraph("Get Involved", S["section"]))
    story.append(Paragraph(
        "<b>GitHub:</b>  github.com/RuralAI/rural-ai-training", S["body"],
    ))
    story.append(Paragraph(
        "<b>Organisation:</b>  github.com/RuralAI", S["body"],
    ))

    story.append(Spacer(1, 12*mm))

    # Closing box -- use a table with background
    closing_text = Paragraph(
        "Together, we can ensure that the AI revolution reaches every community "
        "-- not just those with access to expensive courses and urban tech hubs.",
        S["closing"],
    )
    closing_table = Table([[closing_text]], colWidths=[150*mm])
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

    # Build with cover page handler for first page, normal for rest
    doc.build(
        story,
        onFirstPage=_cover_bg,
        onLaterPages=_normal_page,
    )
    print(f"Donor PDF generated: {output_path}")


if __name__ == "__main__":
    build_pdf()
