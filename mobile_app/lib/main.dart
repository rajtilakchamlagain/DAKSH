import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'native_bridge.dart';
import 'harmonic_bar.dart';
import 'voice_input.dart';
import 'voice_output.dart';
import 'session_state.dart';
import 'gemini_brain.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  SystemChrome.setSystemUIOverlayStyle(
    const SystemUiOverlayStyle(
      statusBarColor: Colors.transparent,
      statusBarIconBrightness: Brightness.dark,
    ),
  );
  runApp(const DakshApp());
}

class DakshApp extends StatefulWidget {
  const DakshApp({super.key});

  @override
  State<DakshApp> createState() => _DakshAppState();
}

class _DakshAppState extends State<DakshApp> {
  bool _isDarkMode = false;

  void _toggleTheme() {
    setState(() {
      _isDarkMode = !_isDarkMode;
    });
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'D.A.K.S.H.',
      debugShowCheckedModeBanner: false,
      themeMode: _isDarkMode ? ThemeMode.dark : ThemeMode.light,
      theme: ThemeData(
        brightness: Brightness.light,
        scaffoldBackgroundColor: const Color(0xFFF8FAFC), // Default Tactical Ivory
        primaryColor: const Color(0xFF0284C7),
        fontFamily: 'monospace',
      ),
      darkTheme: ThemeData(
        brightness: Brightness.dark,
        scaffoldBackgroundColor: const Color(0xFF0B0D11), // Tactical Obsidian
        primaryColor: const Color(0xFF00F0FF),
        fontFamily: 'monospace',
      ),
      home: DakshDashboard(
        isDarkMode: _isDarkMode,
        onToggleTheme: _toggleTheme,
      ),
    );
  }
}

class DakshDashboard extends StatefulWidget {
  final bool isDarkMode;
  final VoidCallback onToggleTheme;

  const DakshDashboard({
    super.key,
    required this.isDarkMode,
    required this.onToggleTheme,
  });

  @override
  State<DakshDashboard> createState() => _DakshDashboardState();
}

class _DakshDashboardState extends State<DakshDashboard> {
  int _activeLedgerTab = 0; // 0: Cadences, 1: Rollover Debt, 2: Sentinel
  bool _notifPermissionGranted = false;
  bool _isSpeaking = false;
  bool _isListening = false;
  String _statusMessage = "ALL SUBSYSTEMS STANDING BY // SILENT STEALTH";

  // Phase 7 Controllers & Brain
  final VoiceInputController _voiceInput = VoiceInputController();
  final VoiceOutputController _voiceOutput = VoiceOutputController();
  final SessionStateMachine _sessionState = SessionStateMachine();
  final GeminiBrain _brain = GeminiBrain();

  // Phase 1 Cadence State
  final List<Map<String, dynamic>> _cadences = [
    {
      "id": "CAD_SHAMPOO",
      "title": "Alternate Day Hair Wash (Shampoo)",
      "cadence_type": "ALTERNATE_DAYS",
      "status": "DUE TODAY (MODULO PARITY MATCH)",
      "time": "08:00 AM",
      "isDue": true,
      "debt": 0
    },
    {
      "id": "CAD_TRASH",
      "title": "Trash Bin Night",
      "cadence_type": "SPECIFIC_WEEKDAYS",
      "status": "NEXT: THURSDAY 09:30 PM",
      "time": "09:30 PM",
      "isDue": false,
      "debt": 0
    },
    {
      "id": "CAD_WALK",
      "title": "Daily Walk (5,000 Steps)",
      "cadence_type": "DAILY",
      "status": "TARGET ACTIVE",
      "time": "07:00 AM",
      "isDue": true,
      "debt": 0
    }
  ];

  // Rollover Backlog Debt State
  final List<Map<String, dynamic>> _rolloverDebt = [
    {
      "id": "TASK_ROLL_01",
      "title": "Deep Clean Workstation",
      "original_date": "2026-10-24",
      "rollover_count": 2,
      "priority": "MEDIUM",
      "tag": "#ROLLED_OVER"
    },
    {
      "id": "TASK_ROLL_02",
      "title": "Review Bank Statement",
      "original_date": "2026-10-23",
      "rollover_count": 3,
      "priority": "HIGH",
      "tag": "#DEBT_HIGH"
    }
  ];

  // Live Sentinel Interception Buffer
  final List<Map<String, dynamic>> _sentinelStream = [];

  @override
  void initState() {
    super.initState();
    _checkPermissions();
    _listenToSentinel();
    _voiceOutput.initialize();
  }

  @override
  void dispose() {
    _voiceInput.dispose();
    super.dispose();
  }

  Future<void> _checkPermissions() async {
    final granted = await DakshNativeBridge.isNotificationAccessGranted();
    setState(() {
      _notifPermissionGranted = granted;
    });
  }

  void _listenToSentinel() {
    DakshNativeBridge.notificationStream.listen((event) {
      setState(() {
        _sentinelStream.insert(0, event);
        if (_sentinelStream.length > 30) {
          _sentinelStream.removeLast();
        }
      });
    });
  }

  Future<void> _triggerWakeGreeting() async {
    setState(() {
      _sessionState.setMode(DakshMode.speaking);
      _isSpeaking = true;
      _statusMessage = "DAKSH: Standing by. Would you like a tactical briefing?";
    });
    await _voiceOutput.speak("Standing by. Would you like a tactical briefing?");
    if (mounted) {
      setState(() {
        _isSpeaking = false;
        _sessionState.setMode(DakshMode.silent);
      });
    }
  }

  Future<void> _handleUserUtterance(String text) async {
    if (text.isEmpty) return;

    if (_sessionState.isStandDownCommand(text)) {
      await _voiceInput.stopListening();
      setState(() {
        _isListening = false;
        _sessionState.setMode(DakshMode.silent);
        _statusMessage = "DAKSH: Standing down. Stealth mode active.";
      });
      await _voiceOutput.speak("Standing down.");
      return;
    }

    // Check JARVIS habit pushback
    final pushback = _sessionState.evaluatePushback(text.toLowerCase());
    if (pushback != null) {
      setState(() {
        _isSpeaking = true;
        _statusMessage = "DAKSH: $pushback";
      });
      await _voiceOutput.speak(pushback);
      if (mounted) setState(() => _isSpeaking = false);
      return;
    }

    // Native Bridge Action or Cognitive Brain Query
    setState(() {
      _statusMessage = "PROCESSING: '$text'";
      _sessionState.setMode(DakshMode.processing);
    });

    if (text.toLowerCase().contains("rename priya")) {
      final res = await DakshNativeBridge.renameContact(currentName: "Priya", newName: "Swimi");
      final reply = res['success'] == true
          ? "Contact Priya updated to Swimi. Records synchronized."
          : "Unable to modify contact Priya.";
      _deliverResponse(reply);
      return;
    }

    if (text.toLowerCase().contains("push walk") || text.toLowerCase().contains("postpone walk")) {
      setState(() {
        _rolloverDebt.insert(0, {
          "id": "TASK_WALK_ROLL",
          "title": "Daily Walk (5,000 Steps)",
          "original_date": "2026-10-25",
          "rollover_count": 1,
          "priority": "HIGH",
          "tag": "#ROLLED_OVER"
        });
      });
      _deliverResponse("Daily walk rolled over to tomorrow at 0700 hours.");
      return;
    }

    // Briefing and General Cognitive Synthesis
    final tacticalContext = {
      "missedNotifications": _sentinelStream.length,
      "pendingCadences": _cadences.where((c) => c['isDue'] == true).length,
      "rolloverDebt": "${_rolloverDebt.length} items logged",
    };

    final answer = await _brain.query(text, tacticalContext: tacticalContext);
    await _deliverResponse(answer);
  }

  Future<void> _deliverResponse(String reply) async {
    setState(() {
      _sessionState.setMode(DakshMode.speaking);
      _isSpeaking = true;
      _statusMessage = "DAKSH: $reply";
    });

    // Check meeting mode (silence suppression)
    if (!_sessionState.isMeetingMode) {
      await _voiceOutput.speak(reply);
    }

    if (mounted) {
      setState(() {
        _isSpeaking = false;
        _sessionState.setMode(DakshMode.silent);
      });
    }
  }

  void _toggleLiveMic() async {
    if (_isListening) {
      await _voiceInput.stopListening();
      setState(() {
        _isListening = false;
        _sessionState.setMode(DakshMode.silent);
        _statusMessage = "MIC OFF // STEALTH";
      });
    } else {
      setState(() {
        _isListening = true;
        _sessionState.setMode(DakshMode.listening);
        _statusMessage = "LISTENING (MULTILINGUAL)...";
      });
      await _voiceInput.startListening(
        onResult: (text, isFinal) {
          if (isFinal) {
            _handleUserUtterance(text);
          }
        },
      );
    }
  }

  void _showNewCadenceModal(BuildContext context, bool isDark, Color bgCard, Color borderColor, Color accent) {
    final titleController = TextEditingController();
    String rhythm = 'DAILY';

    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: bgCard,
      shape: const RoundedRectangleBorder(borderRadius: BorderRadius.vertical(top: Radius.circular(8))),
      builder: (ctx) {
        return Padding(
          padding: EdgeInsets.only(
            left: 16,
            right: 16,
            top: 20,
            bottom: MediaQuery.of(ctx).viewInsets.bottom + 20,
          ),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                "NEW CADENCE // SCHEDULE SYNTHESIS",
                style: TextStyle(color: accent, fontSize: 11, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 12),
              TextField(
                controller: titleController,
                autofocus: true,
                style: TextStyle(color: isDark ? Colors.white : Colors.black87, fontSize: 12),
                decoration: InputDecoration(
                  hintText: "e.g. Morning Hydration, Gym Session, Medication",
                  hintStyle: const TextStyle(fontSize: 10, color: Colors.grey),
                  enabledBorder: OutlineInputBorder(borderSide: BorderSide(color: borderColor)),
                  focusedBorder: OutlineInputBorder(borderSide: BorderSide(color: accent)),
                ),
              ),
              const SizedBox(height: 12),
              Row(
                children: [
                  OutlinedButton(
                    onPressed: () {
                      if (titleController.text.trim().isNotEmpty) {
                        setState(() {
                          _cadences.add({
                            "id": "CAD_${DateTime.now().millisecondsSinceEpoch}",
                            "title": titleController.text.trim(),
                            "cadence_type": rhythm,
                            "status": "INITIALIZED // PARITY ACTIVE",
                            "time": "08:00 AM",
                            "isDue": true,
                            "debt": 0,
                          });
                        });
                        Navigator.pop(ctx);
                        _deliverResponse("Cadence '${titleController.text.trim()}' committed to ledger.");
                      }
                    },
                    style: OutlinedButton.styleFrom(side: BorderSide(color: accent)),
                    child: Text("COMMIT CADENCE", style: TextStyle(color: accent, fontSize: 10)),
                  ),
                ],
              )
            ],
          ),
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    final isDark = widget.isDarkMode;
    final bgCard = isDark ? const Color(0xFF141923) : Colors.white;
    final borderColor = isDark ? const Color(0xFF242E42) : const Color(0xFFE2E8F0);
    final textPrimary = isDark ? const Color(0xFFF1F5F9) : const Color(0xFF0F172A);
    final textMuted = isDark ? const Color(0xFF64748B) : const Color(0xFF64748B);
    final accent = isDark ? const Color(0xFF00F0FF) : const Color(0xFF0284C7);
    final amberDebt = isDark ? const Color(0xFFFFB020) : const Color(0xFFD97706);

    return Scaffold(
      appBar: AppBar(
        backgroundColor: bgCard,
        elevation: 0,
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Text(
                  'D.A.K.S.H.',
                  style: TextStyle(
                    fontFamily: 'monospace',
                    fontWeight: FontWeight.w900,
                    letterSpacing: 1.5,
                    color: accent,
                    fontSize: 16,
                  ),
                ),
                const SizedBox(width: 8),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                  decoration: BoxDecoration(
                    color: accent.withValues(alpha: 0.1),
                    borderRadius: BorderRadius.circular(2),
                    border: Border.all(color: accent.withValues(alpha: 0.4)),
                  ),
                  child: Text(
                    _sessionState.isMeetingMode ? 'STEALTH/MEETING' : 'ACTIVE_LIVE',
                    style: TextStyle(
                      fontFamily: 'monospace',
                      fontSize: 9,
                      fontWeight: FontWeight.bold,
                      color: accent,
                    ),
                  ),
                ),
              ],
            ),
            Text(
              'DECISION & KNOWLEDGE SYNTHESIZER',
              style: TextStyle(
                fontFamily: 'monospace',
                fontSize: 8,
                color: textMuted,
                letterSpacing: 0.8,
              ),
            ),
          ],
        ),
        actions: [
          IconButton(
            icon: Icon(
              _sessionState.isMeetingMode ? Icons.volume_off : Icons.meeting_room_outlined,
              size: 18,
              color: _sessionState.isMeetingMode ? amberDebt : textMuted,
            ),
            tooltip: 'Toggle Meeting / Stealth Silence',
            onPressed: () {
              setState(() {
                _sessionState.toggleMeetingMode(!_sessionState.isMeetingMode);
              });
            },
          ),
          IconButton(
            icon: Icon(
              isDark ? Icons.light_mode : Icons.dark_mode,
              size: 18,
              color: textMuted,
            ),
            onPressed: widget.onToggleTheme,
          ),
        ],
        bottom: PreferredSize(
          preferredSize: const Size.fromHeight(1.0),
          child: Container(
            color: borderColor,
            height: 1.0,
          ),
        ),
      ),
      body: Column(
        children: [
          if (!_notifPermissionGranted)
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              color: amberDebt.withValues(alpha: 0.12),
              child: Row(
                children: [
                  Icon(Icons.warning_amber_rounded, size: 14, color: amberDebt),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      "SENTINEL ACCESS NOT INITIALIZED",
                      style: TextStyle(color: amberDebt, fontSize: 9, fontWeight: FontWeight.bold),
                    ),
                  ),
                  InkWell(
                    onTap: () async {
                      await DakshNativeBridge.requestNotificationAccess();
                      _checkPermissions();
                    },
                    child: Text(
                      "[ENABLE SENTINEL]",
                      style: TextStyle(
                        color: amberDebt,
                        fontSize: 9,
                        fontWeight: FontWeight.w900,
                        decoration: TextDecoration.underline,
                      ),
                    ),
                  ),
                ],
              ),
            ),

          // 3-Column Tactical Ledger Tabs
          Container(
            color: bgCard,
            child: Row(
              children: [
                _buildLedgerTab(0, "CADENCES (${_cadences.length})", accent, textPrimary, textMuted),
                _buildLedgerTab(1, "ROLLOVER (${_rolloverDebt.length})", amberDebt, textPrimary, textMuted),
                _buildLedgerTab(2, "SENTINEL (${_sentinelStream.length})", accent, textPrimary, textMuted),
              ],
            ),
          ),
          Divider(height: 1, thickness: 1, color: borderColor),

          // Active Ledger Content
          Expanded(
            child: IndexedStack(
              index: _activeLedgerTab,
              children: [
                _buildCadenceList(isDark, bgCard, borderColor, accent),
                _buildRolloverDebtList(isDark, bgCard, borderColor, amberDebt),
                _buildSentinelStreamList(isDark, bgCard, borderColor, textMuted),
              ],
            ),
          ),

          // Status & Response Output Box
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
            decoration: BoxDecoration(
              color: isDark ? const Color(0xFF0D1117) : const Color(0xFFF1F5F9),
              border: Border(top: BorderSide(color: borderColor)),
            ),
            child: Row(
              children: [
                Icon(
                  _isSpeaking ? Icons.volume_up : Icons.terminal,
                  size: 16,
                  color: _isSpeaking ? accent : textMuted,
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    _statusMessage,
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                    style: TextStyle(
                      color: _isSpeaking ? accent : textPrimary,
                      fontSize: 10,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
              ],
            ),
          ),

          // Harmonic Spectrum Visualizer
          Container(
            color: bgCard,
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
            child: HarmonicSpectrumBar(
              isSpeaking: _isSpeaking,
              isListening: _isListening,
              accentColor: accent,
            ),
          ),

          // Voice & Tactical Operations Bar
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
            decoration: BoxDecoration(
              color: bgCard,
              border: Border(top: BorderSide(color: borderColor)),
            ),
            child: Row(
              children: [
                // Direct Mic Input Trigger (Sprint 7.1)
                IconButton(
                  onPressed: _toggleLiveMic,
                  icon: Icon(
                    _isListening ? Icons.mic : Icons.mic_none,
                    color: _isListening ? Colors.redAccent : accent,
                    size: 20,
                  ),
                  tooltip: "Toggle Voice Input",
                ),
                const SizedBox(width: 6),
                _buildCommandButton(
                  "\"What did I miss?\"",
                  () => _handleUserUtterance("What did I miss? Give me my tactical briefing."),
                  accent,
                  bgCard,
                  borderColor,
                ),
                const SizedBox(width: 6),
                _buildCommandButton(
                  "\"Skip Gym\"",
                  () => _handleUserUtterance("I will skip gym workout today"),
                  amberDebt,
                  bgCard,
                  borderColor,
                ),
                const SizedBox(width: 6),
                IconButton(
                  onPressed: () => _showNewCadenceModal(context, isDark, bgCard, borderColor, accent),
                  icon: Icon(Icons.add_circle_outline, color: accent, size: 18),
                  tooltip: "Create Cadence",
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildLedgerTab(int index, String label, Color accent, Color textPrimary, Color textMuted) {
    final isSelected = _activeLedgerTab == index;
    return Expanded(
      child: GestureDetector(
        onTap: () => setState(() => _activeLedgerTab = index),
        child: Container(
          padding: const EdgeInsets.symmetric(vertical: 12),
          decoration: BoxDecoration(
            border: Border(
              bottom: BorderSide(
                color: isSelected ? accent : Colors.transparent,
                width: 2,
              ),
            ),
          ),
          alignment: Alignment.center,
          child: Text(
            label,
            style: TextStyle(
              color: isSelected ? accent : textMuted,
              fontSize: 9,
              fontWeight: FontWeight.bold,
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildCadenceList(bool isDark, Color bgCard, Color borderColor, Color accent) {
    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: _cadences.length,
      itemBuilder: (context, i) {
        final item = _cadences[i];
        final isDue = item['isDue'] == true;
        return Dismissible(
          key: Key(item['id']),
          direction: DismissDirection.endToStart,
          background: Container(
            alignment: Alignment.centerRight,
            padding: const EdgeInsets.only(right: 16),
            color: Colors.redAccent.withValues(alpha: 0.2),
            child: const Icon(Icons.delete, color: Colors.redAccent, size: 16),
          ),
          onDismissed: (_) {
            setState(() {
              _cadences.removeAt(i);
            });
            _deliverResponse("Cadence '${item['title']}' removed from tracking.");
          },
          child: Container(
            margin: const EdgeInsets.only(bottom: 8),
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: bgCard,
              borderRadius: BorderRadius.circular(4),
              border: Border.all(color: isDue ? accent : borderColor),
            ),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      item['title'],
                      style: TextStyle(
                        color: isDark ? Colors.white : Colors.black87,
                        fontSize: 11,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      "TYPE: ${item['cadence_type']} // ${item['time']}",
                      style: const TextStyle(color: Colors.grey, fontSize: 8.5),
                    ),
                  ],
                ),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                  decoration: BoxDecoration(
                    color: (isDue ? accent : Colors.grey).withValues(alpha: 0.1),
                    borderRadius: BorderRadius.circular(2),
                  ),
                  child: Text(
                    item['status'],
                    style: TextStyle(
                      color: isDue ? accent : Colors.grey,
                      fontSize: 8,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _buildRolloverDebtList(bool isDark, Color bgCard, Color borderColor, Color amberDebt) {
    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: _rolloverDebt.length,
      itemBuilder: (context, i) {
        final item = _rolloverDebt[i];
        return Container(
          margin: const EdgeInsets.only(bottom: 8),
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: bgCard,
            borderRadius: BorderRadius.circular(4),
            border: Border.all(color: amberDebt.withValues(alpha: 0.5)),
          ),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 1),
                        decoration: BoxDecoration(
                          color: amberDebt.withValues(alpha: 0.2),
                          borderRadius: BorderRadius.circular(2),
                        ),
                        child: Text(
                          "${item['rollover_count']}x ROLLED",
                          style: TextStyle(color: amberDebt, fontSize: 8, fontWeight: FontWeight.bold),
                        ),
                      ),
                      const SizedBox(width: 6),
                      Text(
                        item['title'],
                        style: TextStyle(
                          color: isDark ? Colors.white : Colors.black87,
                          fontSize: 11,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 3),
                  Text(
                    "ORIGIN: ${item['original_date']} // PRIORITY: ${item['priority']}",
                    style: const TextStyle(color: Colors.grey, fontSize: 8.5),
                  ),
                ],
              ),
              Icon(Icons.arrow_forward, size: 14, color: amberDebt),
            ],
          ),
        );
      },
    );
  }

  Widget _buildSentinelStreamList(bool isDark, Color bgCard, Color borderColor, Color textMuted) {
    if (_sentinelStream.isEmpty) {
      return Center(
        child: Text(
          "SENTINEL BUFFER IDLE // NO PACKETS INTERCEPTED\nWaiting for system notifications...",
          textAlign: TextAlign.center,
          style: TextStyle(color: textMuted, fontSize: 10),
        ),
      );
    }
    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: _sentinelStream.length,
      itemBuilder: (context, i) {
        final packet = _sentinelStream[i];
        final isActionable = packet['isActionable'] == true;
        return Container(
          margin: const EdgeInsets.only(bottom: 6),
          padding: const EdgeInsets.all(10),
          decoration: BoxDecoration(
            color: bgCard,
            borderRadius: BorderRadius.circular(4),
            border: Border.all(color: isActionable ? Colors.blueAccent : borderColor),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                (packet['package'] ?? '').toString().split('.').last.toUpperCase(),
                style: const TextStyle(color: Colors.blueAccent, fontSize: 8, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 2),
              Text(
                packet['title'] ?? 'Notification',
                style: TextStyle(color: isDark ? Colors.white : Colors.black87, fontSize: 10, fontWeight: FontWeight.bold),
              ),
              if ((packet['text'] ?? '').toString().isNotEmpty)
                Text(
                  packet['text'],
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                  style: const TextStyle(color: Colors.grey, fontSize: 9),
                ),
            ],
          ),
        );
      },
    );
  }

  Widget _buildCommandButton(String label, VoidCallback onTap, Color accent, Color bgCard, Color borderColor) {
    return Expanded(
      child: OutlinedButton(
        style: OutlinedButton.styleFrom(
          side: BorderSide(color: accent.withValues(alpha: 0.6)),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(4)),
          padding: const EdgeInsets.symmetric(vertical: 8),
        ),
        onPressed: onTap,
        child: Text(
          label,
          style: TextStyle(color: accent, fontSize: 9, fontWeight: FontWeight.bold),
        ),
      ),
    );
  }
}
