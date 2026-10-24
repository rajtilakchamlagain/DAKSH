# D.A.K.S.H. ARCHITECTURAL MASTER PLAN
## Complete Branching, Sub-Branching, and Implementation Breakdown

---

### BRANCH 1: `arch/core-engine` (Core Orchestrator & State Matrix)
* **Sub-Branch 1.1: Event Bus & Reactive State**
  - Thread-safe pub/sub dispatch bus.
  - Event schemas: `VOICE_INTENT_TRIGGERED`, `TASK_STATE_CHANGED`, `NOTIFICATION_INGESTED`, `DEVICE_ACTION_COMMITTED`.
* **Sub-Branch 1.2: Local Sovereign Storage**
  - Encrypted SQLite schema with migrations.
  - Tables: `tasks`, `cadences`, `rollover_history`, `notification_logs`, `contact_audit_trail`.
* **Sub-Branch 1.3: Telemetry & Health Sentinel**
  - Battery impact monitor.
  - Network latency estimator for LLM / TTS fallback.

---

### BRANCH 2: `agent/cognitive-brain` (Multi-Agent Neural Pipeline)
* **Sub-Branch 2.1: Tactical Intent Router**
  - Intent classification (<80ms target).
  - JSON function schema validator for tool invocation.
* **Sub-Branch 2.2: Temporal & Routine Matrix**
  - Mathematical modulo engine for alternate-day schedules ($Day \pmod 2$).
  - Midnight rollover scheduler: carries pending items forward with `#rolled_over` debt counters.
  - Cadence parser: weekly intervals (trash pickup, trash bin return, deep cleanings).
* **Sub-Branch 2.3: Device Action Dispatcher**
  - Safe parameter sanitation for OS commands.
  - Undo-buffer for high-impact actions (e.g., contact rename reversal).
* **Sub-Branch 2.4: Tactical Persona Synthesis**
  - Terse, weighted, calm verbal generation (Paul Bettany / Vision cadence).
  - Dynamic briefing compiler: Morning briefing, Evening debrief, Urgent interruption.

---

### BRANCH 3: `platform/android-sentinel` (Deep Android OS Integrations)
* **Sub-Branch 3.1: Consent & Authorization Gatekeeper**
  - Interactive onboarding for high-privilege Android permissions:
    - `READ_CONTACTS` & `WRITE_CONTACTS`
    - `BIND_NOTIFICATION_LISTENER_SERVICE`
    - `SCHEDULE_EXACT_ALARM` & `USE_EXACT_ALARM`
    - `SEND_SMS` & `CALL_PHONE`
* **Sub-Branch 3.2: Native Contacts Controller**
  - Android `ContentResolver` and `ContactsContract` read/update APIs.
  - Name query matching, update operations, and audit logging.
* **Sub-Branch 3.3: Notification Interceptor Service**
  - Custom `NotificationListenerService` subclass.
  - Regex & heuristic filtering to drop app promotions and isolate action-worthy events.
* **Sub-Branch 3.4: Background Persistence & Doze Exemption**
  - Android `WorkManager` & Foreground Service with silent notification channel for continuous vigilance.

---

### BRANCH 4: `voice/neural-acoustic` (Conversational & Voice Synthesis)
* **Sub-Branch 4.1: Streaming ASR (Speech-to-Text)**
  - Local Whisper / Edge ASR pipeline for immediate phrase capture.
  - Wake-word listener ("Hey Daksh" / "Daksh").
* **Sub-Branch 4.2: High-Weightage Baritone Voice Engine**
  - Integration with low-latency streaming TTS (ElevenLabs custom tuned British/baritone profile or Edge neural TTS).
  - Pitch, rate, and audio filter DSP to create cinematic studio acoustic presence.
* **Sub-Branch 4.3: Realtime Full-Duplex Dialogue**
  - Interruption handling (barge-in): stopping audio output the instant the user speaks.

---

### BRANCH 5: `ui/kite-tactical` (The Interface: Light & Dark Modes)
* **Sub-Branch 5.1: Dual Theme System (Light First)**
  - **Tactical Light (Default):** Neutral ivory/parchment background (`#F7F9FA`), razor 1px borders (`#E2E8F0`), deep slate typography (`#1A202C`), electric blue indicators (`#0066FF`).
  - **Obsidian Dark:** Pure OLED black (`#0B0D11`), graphite surfaces (`#161A22`), ice cyan glow (`#00F0FF`).
* **Sub-Branch 5.2: Kite-Style High-Density HUD**
  - Telemetry bar: Battery, AI Status, Pending Rollovers, Notification Queue.
  - Three-column / segmented execution ledger:
    - *Column 1:* `TODAY_TICKETS` (Alternate-day & daily routines).
    - *Column 2:* `TEMPORAL_DEBT` (Rollover tasks with pending days count).
    - *Column 3:* `SENTINEL_STREAM` (Triaged notifications converted to tasks).
* **Sub-Branch 5.3: Voice Reactive Visualizer**
  - Minimalist, non-gimmicky audio spectrum / harmonic bar across the bottom navigation bar.
