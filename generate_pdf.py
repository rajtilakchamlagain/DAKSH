import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, PageBreak, KeepTogether
)
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor("#718096"))
        
        # Header (Top)
        self.drawString(54, 750, "D.A.K.S.H. ARCHITECTURAL BLUEPRINT // SPECIFICATION DOCUMENT")
        self.drawRightString(612 - 54, 750, "CONFIDENTIAL // LIFE-OS")
        self.setStrokeColor(colors.HexColor("#E2E8F0"))
        self.setLineWidth(0.75)
        self.line(54, 742, 612 - 54, 742)
        
        # Footer (Bottom)
        self.line(54, 45, 612 - 54, 45)
        self.setFont("Helvetica", 8)
        self.drawString(54, 32, "DECISION & KNOWLEDGE SYNTHESIZER FOR HUMAN-OPERATIONS")
        self.drawRightString(612 - 54, 32, f"PAGE {self._pageNumber} OF {page_count}")
        self.restoreState()

def generate_blueprint_pdf(filename):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=64,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=colors.HexColor("#0F172A")
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        leading=16,
        textColor=colors.HexColor("#475569")
    )

    section_heading = ParagraphStyle(
        'SecHeading',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=17,
        textColor=colors.HexColor("#0284C7"),
        spaceBefore=14,
        spaceAfter=6
    )

    subsection_heading = ParagraphStyle(
        'SubSecHeading',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#1E293B"),
        spaceBefore=8,
        spaceAfter=4
    )

    body_style = ParagraphStyle(
        'DocBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#334155")
    )

    code_like = ParagraphStyle(
        'CodeBranch',
        parent=styles['Normal'],
        fontName='Courier-Bold',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#0369A1")
    )

    table_header_style = ParagraphStyle(
        'TblHdr',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#FFFFFF")
    )

    story = []

    # Title block
    story.append(Paragraph("D.A.K.S.H. (दक्ष)", title_style))
    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>Decision & Knowledge Synthesizer for Human-operations</b><br/>System Architecture, Branching Strategy & Engineering Implementation Plan", subtitle_style))
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0284C7"), spaceAfter=14))

    # Executive Overview
    story.append(Paragraph("1. EXECUTIVE ARCHITECTURAL VISION", section_heading))
    story.append(Paragraph(
        "<b>D.A.K.S.H.</b> is an autonomous cognitive personal operating system designed to transcend ordinary task list "
        "and assistant applications. Combining deep Android OS hardware authority, real-time ambient notification interception, "
        "alternate-day mathematical routine scheduling, and a low-latency cinematic baritone voice loop, D.A.K.S.H. serves as a "
        "continuous sovereign life copilot. The design language rejects typical AI clichés in favor of a <b>Zerodha Kite-inspired</b> "
        "high-density, tactical light-default interface paired with an obsidian dark theme.",
        body_style
    ))
    story.append(Spacer(1, 8))

    # Branch Strategy Matrix
    story.append(Paragraph("2. BRANCH & SUB-BRANCH IMPLEMENTATION ROADMAP", section_heading))
    story.append(Paragraph("The engineering lifecycle is structured across five primary branches and eleven focused sub-branches:", body_style))
    story.append(Spacer(1, 6))

    branch_table_data = [
        [
            Paragraph("<b>BRANCH IDENTIFIER</b>", table_header_style),
            Paragraph("<b>SUB-BRANCHES & DOMAIN</b>", table_header_style),
            Paragraph("<b>KEY DELIVERABLES</b>", table_header_style)
        ],
        [
            Paragraph("<b>arch/core-engine</b>", code_like),
            Paragraph("• 1.1: Event Bus & Reactive State<br/>• 1.2: Encrypted Local Store<br/>• 1.3: Health Sentinel", body_style),
            Paragraph("Thread-safe pub/sub dispatch bus, local encrypted SQLite, battery and latency metrics tracker.", body_style)
        ],
        [
            Paragraph("<b>agent/cognitive-brain</b>", code_like),
            Paragraph("• 2.1: Tactical Router<br/>• 2.2: Temporal & Routine Matrix<br/>• 2.3: Device Action Dispatcher<br/>• 2.4: Persona Engine", body_style),
            Paragraph("&lt;80ms intent classification, modulo alternate-day engine, midnight auto-rollover, contact updater, baritone persona.", body_style)
        ],
        [
            Paragraph("<b>platform/android-sentinel</b>", code_like),
            Paragraph("• 3.1: Consent & Auth Protocol<br/>• 3.2: Contacts Controller<br/>• 3.3: Notification Interceptor<br/>• 3.4: Doze Persistence", body_style),
            Paragraph("NotificationListenerService, ContactsContract CRUD, exact hardware alarms, and background foreground service.", body_style)
        ],
        [
            Paragraph("<b>voice/neural-acoustic</b>", code_like),
            Paragraph("• 4.1: Streaming ASR<br/>• 4.2: Baritone Neural Voice<br/>• 4.3: Realtime Duplex", body_style),
            Paragraph("Fast wake-word detection, studio-weighted cinematic voice (Vision/Jarvis cadence), instant barge-in interruption.", body_style)
        ],
        [
            Paragraph("<b>ui/kite-tactical</b>", code_like),
            Paragraph("• 5.1: Dual Theme (Light Default)<br/>• 5.2: High-Density HUD<br/>• 5.3: Harmonic Spectrum Meter", body_style),
            Paragraph("Kite-inspired financial-grade ledger, paper-white default UI, obsidian dark mode, live audio reactive meter.", body_style)
        ],
    ]

    branch_table = Table(branch_table_data, colWidths=[1.4*inch, 2.4*inch, 3.2*inch])
    branch_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#0F172A")),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor("#FFFFFF"), colors.HexColor("#F8FAFC")]),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
    ]))

    story.append(branch_table)
    story.append(Spacer(1, 10))

    # Deep Mobile Device Control Section
    story.append(Paragraph("3. SOVEREIGN MOBILE CONTROL & CONSENT PROTOCOL", section_heading))
    story.append(Paragraph(
        "D.A.K.S.H. executes system operations with verified user consent. Unlike cloud-only assistants, it bridges directly "
        "to native Android subsystems:",
        body_style
    ))
    story.append(Spacer(1, 4))

    perm_data = [
        [
            Paragraph("<b>SYSTEM DOMAIN</b>", table_header_style),
            Paragraph("<b>ANDROID PERMISSION / API</b>", table_header_style),
            Paragraph("<b>D.A.K.S.H. CAPABILITY & VOICE ACTION</b>", table_header_style)
        ],
        [
            Paragraph("<b>Address Book</b>", code_like),
            Paragraph("READ_CONTACTS<br/>WRITE_CONTACTS", body_style),
            Paragraph("Allows spoken mutations: <i>'Daksh, rename contact Priya to Swimi.'</i> Queries ContentResolver and updates record in milliseconds.", body_style)
        ],
        [
            Paragraph("<b>Ambient Telemetry</b>", code_like),
            Paragraph("NotificationListenerService", body_style),
            Paragraph("Triages incoming notifications (WhatsApp, Bank, Delivery), dropping noise and turning actionables into dynamic ledger items.", body_style)
        ],
        [
            Paragraph("<b>Temporal Alerts</b>", code_like),
            Paragraph("SCHEDULE_EXACT_ALARM<br/>WAKE_LOCK", body_style),
            Paragraph("Guarantees morning briefings and alternate-day reminders execute reliably, even when Android enters deep Doze battery mode.", body_style)
        ]
    ]

    perm_table = Table(perm_data, colWidths=[1.4*inch, 2.2*inch, 3.4*inch])
    perm_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#0F172A")),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor("#FFFFFF"), colors.HexColor("#F8FAFC")]),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(perm_table)
    story.append(Spacer(1, 10))

    # Design Specifications (Kite HUD)
    story.append(Paragraph("4. KITE-TACTICAL DESIGN SYSTEM (LIGHT & DARK MODES)", section_heading))
    story.append(Paragraph(
        "The interface rejects standard AI chatbot patterns. It employs an instrument-grade financial HUD:",
        body_style
    ))
    story.append(Spacer(1, 4))
    story.append(Paragraph("• <b>Light Mode (Default):</b> Crisp paper background (#F8FAFC), 1px slate divider borders (#E2E8F0), dark-slate tabular data (#0F172A), and stark electrical blue accents (#0284C7).", body_style))
    story.append(Paragraph("• <b>Dark Mode (Tactical Obsidian):</b> Deep OLED black (#0B0D11), matte slate cards (#1E293B), ice-cyan highlights (#00F0FF), and amber rollover markers (#F59E0B).", body_style))
    story.append(Paragraph("• <b>Dynamic Execution Ledger:</b> Replaces scattered task lists with a 3-column ticket system: Today's Cadences, Rollover Debt Ledger, and Ambient Notification Stream.", body_style))
    story.append(Paragraph("• <b>Harmonic Soundwave Bar:</b> A continuous, ultra-slim 2px harmonic visualizer that pulses during neural reasoning and voice generation.", body_style))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"SUCCESS: Blueprint generated at {filename}")

if __name__ == '__main__':
    out_path = r"C:\Users\rajti\Downloads\Projects\DAKSH\DAKSH_Master_Implementation_Plan.pdf"
    generate_blueprint_pdf(out_path)
