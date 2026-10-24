import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
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
        self.setFillColor(colors.HexColor("#64748B"))
        
        # Header (Top)
        self.drawString(54, 750, "D.A.K.S.H. // 6-PHASE SYSTEM IMPLEMENTATION BLUEPRINT")
        self.drawRightString(612 - 54, 750, "ENGINEERING LIFECYCLE ROADMAP")
        self.setStrokeColor(colors.HexColor("#E2E8F0"))
        self.setLineWidth(0.75)
        self.line(54, 742, 612 - 54, 742)
        
        # Footer (Bottom)
        self.line(54, 45, 612 - 54, 45)
        self.setFont("Helvetica", 8)
        self.drawString(54, 32, "DECISION & KNOWLEDGE SYNTHESIZER FOR HUMAN-OPERATIONS (D.A.K.S.H.)")
        self.drawRightString(612 - 54, 32, f"PAGE {self._pageNumber} OF {page_count}")
        self.restoreState()

def generate_phases_pdf(filename):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=64,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#0F172A")
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#475569")
    )

    phase_heading = ParagraphStyle(
        'PhaseHeading',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=colors.HexColor("#0284C7"),
        spaceBefore=10,
        spaceAfter=4
    )

    body_style = ParagraphStyle(
        'DocBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12.5,
        textColor=colors.HexColor("#334155")
    )

    bullet_style = ParagraphStyle(
        'DocBullet',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12.5,
        textColor=colors.HexColor("#1E293B"),
        leftIndent=12
    )

    story = []

    # Title Header
    story.append(Paragraph("D.A.K.S.H. SYSTEM PHASING MATRIX", title_style))
    story.append(Spacer(1, 2))
    story.append(Paragraph("<b>End-to-End Tactical Implementation Guide across 6 Sequential Engineering Phases</b>", subtitle_style))
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0284C7"), spaceAfter=10))

    # Phase 1
    story.append(Paragraph("PHASE 1: LOCAL CORE & TEMPORAL ENGINE (arch/core-engine)", phase_heading))
    story.append(Paragraph("<b>Primary Objective:</b> Build the deterministic algorithmic core: local persistence, mathematical modulo scheduling for alternate days, and midnight debt rollover.", body_style))
    story.append(Paragraph("• <b>Subphase 1.1 (Encrypted Persistence Schema):</b> SQLite / Room database modeling tasks, cadence rules, rollover ledgers, and reversible action audit trails.", bullet_style))
    story.append(Paragraph("• <b>Subphase 1.2 (Alternating Modulo Arithmetic):</b> Anchor-based modulo parity calculation (DayCount % 2) guaranteeing absolute synchronization for alternate-day habits (shampoo, workout splits).", bullet_style))
    story.append(Paragraph("• <b>Subphase 1.3 (Midnight Rollover Daemon):</b> Automated 23:59:59 rollover evaluator carrying uncompleted tasks to tomorrow with #rolled_over tags and debt counters.", bullet_style))
    story.append(Paragraph("• <b>Subphase 1.4 (Thread-Safe Event Bus):</b> In-process asynchronous event bus dispatching intent, status, and telemetry signals.", bullet_style))
    story.append(Spacer(1, 6))

    # Phase 2
    story.append(Paragraph("PHASE 2: ANDROID NATIVE SENTINEL BRIDGE (platform/android-sentinel)", phase_heading))
    story.append(Paragraph("<b>Primary Objective:</b> Grant D.A.K.S.H. sovereign device control via native Android APIs and explicit user authorization protocol.", body_style))
    story.append(Paragraph("• <b>Subphase 2.1 (Consent & Protocol Gatekeeper):</b> Interactive high-privilege permission onboarding (Contacts, NotificationListener, Exact Alarms, Telephony).", bullet_style))
    story.append(Paragraph("• <b>Subphase 2.2 (Native Contacts Controller):</b> ContentResolver bridge to query, match, and rename contacts (e.g., 'Rename Priya to Swimi') with reversible state snapshots.", bullet_style))
    story.append(Paragraph("• <b>Subphase 2.3 (Ambient Notification Interceptor):</b> NotificationListenerService extracting actionable items (WhatsApp, bank OTPs, delivery alerts) while filtering marketing spam.", bullet_style))
    story.append(Paragraph("• <b>Subphase 2.4 (Doze & Battery Resilience):</b> WorkManager and foreground execution pipeline allowing morning briefings to fire through deep battery sleep.", bullet_style))
    story.append(Spacer(1, 6))

    # Phase 3
    story.append(Paragraph("PHASE 3: TACTICAL INTENT ROUTER & MULTI-AGENT BRAIN (agent/cognitive-brain)", phase_heading))
    story.append(Paragraph("<b>Primary Objective:</b> Sub-100ms multi-model intent routing, parameter validation, and tactical persona synthesis.", body_style))
    story.append(Paragraph("• <b>Subphase 3.1 (Sub-100ms Router):</b> Fast SLM parsing voice inputs into structured JSON tool calls (Device Mutation, Temporal Operation, Query).", bullet_style))
    story.append(Paragraph("• <b>Subphase 3.2 (Action Dispatcher & Validator):</b> Sanitizes parameters (phone numbers, contact names, exact times) before native execution.", bullet_style))
    story.append(Paragraph("• <b>Subphase 3.3 (Tactical Persona Engine):</b> Paul Bettany / Vision-inspired cadence generator delivering concise, authoritative briefings without AI boilerplate.", bullet_style))
    story.append(Spacer(1, 6))

    # Phase 4
    story.append(Paragraph("PHASE 4: BARITONE VOICE & FULL-DUPLEX AUDIO (voice/neural-acoustic)", phase_heading))
    story.append(Paragraph("<b>Primary Objective:</b> Cinematic acoustic resonance, custom wake-word, and real-time barge-in capability.", body_style))
    story.append(Paragraph("• <b>Subphase 4.1 (Streaming ASR & Wake-Word):</b> Instant 'Hey Daksh' detection and real-time speech tokenization.", bullet_style))
    story.append(Paragraph("• <b>Subphase 4.2 (Studio-Grade Baritone TTS):</b> Low-latency neural streaming voice with studio EQ and acoustic depth.", bullet_style))
    story.append(Paragraph("• <b>Subphase 4.3 (Instant Barge-In Handling):</b> Hardware microphone interrupt loop immediately halting audio output when user speaks.", bullet_style))
    story.append(Spacer(1, 6))

    # Phase 5
    story.append(Paragraph("PHASE 5: KITE-TACTICAL UI (ui/kite-tactical)", phase_heading))
    story.append(Paragraph("<b>Primary Objective:</b> Dual-theme financial HUD with default paper-white tactical mode and dynamic 3-column ticket ledger.", body_style))
    story.append(Paragraph("• <b>Subphase 5.1 (Light-First Dual Theme):</b> Paper-white/ivory canvas (#F8FAFC) with 1px architectural lines (#E2E8F0) and Obsidian Dark mode (#0B0D11).", bullet_style))
    story.append(Paragraph("• <b>Subphase 5.2 (3-Column Execution Ledger):</b> Live telemetry HUD: Today's Cadences, Rollover Debt Tickets, and Sentinel Notification Stream.", bullet_style))
    story.append(Paragraph("• <b>Subphase 5.3 (Harmonic Spectrum Visualizer):</b> Razor-thin 2px soundwave bar reacting in real-time to voice and reasoning state.", bullet_style))
    story.append(Spacer(1, 6))

    # Phase 6
    story.append(Paragraph("PHASE 6: FIELD HARDENING & SOVEREIGN REPO (main)", phase_heading))
    story.append(Paragraph("<b>Primary Objective:</b> 24h battery profiling, offline failover, and transition to sovereign private repository.", body_style))
    story.append(Paragraph("• <b>Subphase 6.1:</b> 24-hour battery consumption optimization for continuous background notification listening.", bullet_style))
    story.append(Paragraph("• <b>Subphase 6.2:</b> Offline on-device failover when network drops.", bullet_style))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"SUCCESS: Phases PDF generated at {filename}")

if __name__ == '__main__':
    out_path = r"C:\Users\rajti\Downloads\Projects\DAKSH\DAKSH_Implementation_Phases.pdf"
    generate_phases_pdf(out_path)
