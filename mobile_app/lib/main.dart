import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'native_bridge.dart';
import 'harmonic_bar.dart';

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
  bool _isListening = true;
  String _statusMessage = "ALL SUBSYSTEMS STANDING BY // LISTENING";

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

  Future<void> _executeVoiceSimulation(String command) async {
    setState(() {
      _isSpeaking = true;
      _statusMessage = "PROCESSING: '$command'";
    });

    if (command.contains("Rename Priya")) {
      final res = await DakshNativeBridge.renameContact(currentName: "Priya", newName: "Swimi");
      setState(() {
        _statusMessage = res['success'] == true
            ? "DAKSH: Contact Priya updated to Swimi, sir. Records synchronized."
            : "DAKSH: Unable to modify contact Priya, sir.";
      });
    } else if (command.contains("Push walk")) {
      setState(() {
        _rolloverDebt.insert(0, {
          "id": "TASK_WALK_ROLL",
          "title": "Daily Walk (5,000 Steps)",
          "original_date": "2026-10-25",
          "rollover_count": 1,
          "priority": "HIGH",
          "tag": "#ROLLED_OVER"
        });
        _statusMessage = "DAKSH: Understood, sir. Shifting the 5,000-step walk to tomorrow at 0700 hours.";
      });
    }

    await Future.delayed(const Duration(milliseconds: 2400));
    setState(() {
      _isSpeaking = false;
    });
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
                  "D.A.K.S.H.",
                  style: TextStyle(
                    color: textPrimary,
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                    letterSpacing: 2,
                  ),
                ),
                const SizedBox(width: 8),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                  decoration: BoxDecoration(
                    color: accent.withValues(alpha: 0.15),
                    borderRadius: BorderRadius.circular(4),
                    border: Border.all(color: accent, width: 0.8),
                  ),
                  child: Text(
                    "OS 1.0",
                    style: TextStyle(color: accent, fontSize: 10, fontWeight: FontWeight.bold),
                  ),
                )
              ],
            ),
            Text(
              "DECISION & KNOWLEDGE SYNTHESIZER",
              style: TextStyle(color: textMuted, fontSize: 8.5, letterSpacing: 1),
            ),
          ],
        ),
        actions: [
          IconButton(
            icon: Icon(
              isDark ? Icons.light_mode_outlined : Icons.dark_mode_outlined,
              color: textPrimary,
              size: 20,
            ),
            onPressed: widget.onToggleTheme,
          ),
          const SizedBox(width: 8),
        ],
        bottom: PreferredSize(
          preferredSize: const Size.fromHeight(1),
          child: Container(color: borderColor, height: 1),
        ),
      ),
      body: Column(
        children: [
          // Telemetry HUD Bar
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
            color: isDark ? const Color(0xFF0D1117) : const Color(0xFFF1F5F9),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Row(
                  children: [
                    Container(
                      width: 8,
                      height: 8,
                      decoration: BoxDecoration(
                        color: _notifPermissionGranted ? Colors.green : Colors.amber,
                        shape: BoxShape.circle,
                      ),
                    ),
                    const SizedBox(width: 8),
                    Text(
                      _notifPermissionGranted ? "SENTINEL ACTIVE" : "PERMISSION REQUIRED",
                      style: TextStyle(color: textPrimary, fontSize: 10, fontWeight: FontWeight.bold),
                    ),
                  ],
                ),
                Text(
                  "DEBT TICKETS: ${_rolloverDebt.length}",
                  style: TextStyle(color: amberDebt, fontSize: 10, fontWeight: FontWeight.bold),
                ),
                if (!_notifPermissionGranted)
                  GestureDetector(
                    onTap: () async {
                      await DakshNativeBridge.requestNotificationAccess();
                      await _checkPermissions();
                    },
                    child: Text(
                      "[AUTHORIZE]",
                      style: TextStyle(color: accent, fontSize: 10, fontWeight: FontWeight.bold),
                    ),
                  ),
              ],
            ),
          ),

          // 3-Column Execution Ledger Header (Kite Financial Tabs)
          Container(
            decoration: BoxDecoration(
              color: bgCard,
              border: Border(bottom: BorderSide(color: borderColor)),
            ),
            child: Row(
              children: [
                _buildLedgerTab(0, "01 // CADENCES", accent, textPrimary, textMuted),
                _buildLedgerTab(1, "02 // DEBT LEDGER", accent, textPrimary, textMuted),
                _buildLedgerTab(2, "03 // SENTINEL STREAM", accent, textPrimary, textMuted),
              ],
            ),
          ),

          // Active Ledger Body
          Expanded(
            child: IndexedStack(
              index: _activeLedgerTab,
              children: [
                // TAB 0: Cadences
                _buildCadenceList(isDark, bgCard, borderColor, accent),

                // TAB 1: Rollover Backlog Debt
                _buildRolloverDebtList(isDark, bgCard, borderColor, amberDebt),

                // TAB 2: Sentinel Live Stream
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
                    maxLines: 1,
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

          // Bottom Voice Simulation Command Bar
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
            decoration: BoxDecoration(
              color: bgCard,
              border: Border(top: BorderSide(color: borderColor)),
            ),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: [
                _buildCommandButton(
                  "\"Rename Priya to Swimi\"",
                  () => _executeVoiceSimulation("Rename Priya to Swimi"),
                  accent,
                  bgCard,
                  borderColor,
                ),
                const SizedBox(width: 8),
                _buildCommandButton(
                  "\"Push walk to tomorrow\"",
                  () => _executeVoiceSimulation("Push walk to tomorrow morning"),
                  amberDebt,
                  bgCard,
                  borderColor,
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
        final cad = _cadences[i];
        final isDue = cad['isDue'] == true;
        return Container(
          margin: const EdgeInsets.only(bottom: 8),
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: bgCard,
            borderRadius: BorderRadius.circular(4),
            border: Border.all(color: isDue ? accent.withValues(alpha: 0.5) : borderColor),
          ),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    cad['title'],
                    style: TextStyle(
                      color: isDark ? Colors.white : Colors.black87,
                      fontSize: 11,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 3),
                  Text(
                    cad['status'],
                    style: TextStyle(
                      color: isDue ? accent : Colors.grey,
                      fontSize: 9,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ],
              ),
              Text(
                cad['time'],
                style: TextStyle(color: Colors.grey, fontSize: 10, fontWeight: FontWeight.bold),
              ),
            ],
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
