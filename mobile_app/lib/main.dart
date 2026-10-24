import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'native_bridge.dart';

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
        scaffoldBackgroundColor: const Color(0xFFF8FAFC), // Light Tactical Ivory
        primaryColor: const Color(0xFF0284C7),
        fontFamily: 'monospace',
      ),
      darkTheme: ThemeData(
        brightness: Brightness.dark,
        scaffoldBackgroundColor: const Color(0xFF0B0D11), // Obsidian Black
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
  bool _notifPermissionGranted = false;
  final List<Map<String, dynamic>> _sentinelStream = [];
  String _statusMessage = "SYSTEM READY // STANDBY";

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
        if (_sentinelStream.length > 20) {
          _sentinelStream.removeLast();
        }
      });
    }, onError: (err) {
      print("[SENTINEL_STREAM_ERROR] $err");
    });
  }

  Future<void> _testRenameContact() async {
    setState(() => _statusMessage = "EXECUTING: RENAME 'Priya' -> 'Swimi'...");
    final result = await DakshNativeBridge.renameContact(
      currentName: "Priya",
      newName: "Swimi",
    );
    setState(() {
      _statusMessage = result['success'] == true
          ? "SUCCESS: Contact Priya renamed to Swimi"
          : "OUTCOME: ${result['message']}";
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
                    color: accent.withOpacity(0.15),
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
          // Telemetry Status Bar
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
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
                      _notifPermissionGranted ? "SENTINEL ONLINE" : "SENTINEL PERMISSION REQUIRED",
                      style: TextStyle(
                        color: textPrimary,
                        fontSize: 10,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
                if (!_notifPermissionGranted)
                  GestureDetector(
                    onTap: () async {
                      await DakshNativeBridge.requestNotificationAccess();
                      await _checkPermissions();
                    },
                    child: Text(
                      "[ENABLE]",
                      style: TextStyle(color: accent, fontSize: 10, fontWeight: FontWeight.bold),
                    ),
                  ),
              ],
            ),
          ),

          // Main Execution Ledger
          Expanded(
            child: ListView(
              padding: const EdgeInsets.all(16),
              children: [
                // Quick Test Command Bar
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: bgCard,
                    borderRadius: BorderRadius.circular(6),
                    border: Border.all(color: borderColor),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        "// HIGH-PRIVILEGE OS CONTROLLER",
                        style: TextStyle(color: accent, fontSize: 10, fontWeight: FontWeight.bold),
                      ),
                      const SizedBox(height: 6),
                      Text(
                        _statusMessage,
                        style: TextStyle(color: textPrimary, fontSize: 11),
                      ),
                      const SizedBox(height: 10),
                      ElevatedButton(
                        style: ElevatedButton.styleFrom(
                          backgroundColor: accent,
                          foregroundColor: Colors.white,
                          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(4)),
                          padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
                        ),
                        onPressed: _testRenameContact,
                        child: const Text(
                          "TEST MUTATION: RENAME PRIYA -> SWIMI",
                          style: TextStyle(fontSize: 10, fontWeight: FontWeight.bold),
                        ),
                      )
                    ],
                  ),
                ),

                const SizedBox(height: 16),

                // Cadence Matrix (Phase 1 Integration Preview)
                Text(
                  "01 // ACTIVE CADENCES & HABIT MATRIX",
                  style: TextStyle(color: textMuted, fontSize: 10, fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 8),
                _buildCadenceCard(
                  title: "Alternate Day Hair Wash (Shampoo)",
                  status: "DUE TODAY (PARITY MODULO MATCH)",
                  time: "08:00 AM",
                  isDue: true,
                  isDark: isDark,
                  borderColor: borderColor,
                  bgCard: bgCard,
                  accent: accent,
                ),
                _buildCadenceCard(
                  title: "Trash Bin Night",
                  status: "SCHEDULED (MONDAY / THURSDAY)",
                  time: "09:30 PM",
                  isDue: false,
                  isDark: isDark,
                  borderColor: borderColor,
                  bgCard: bgCard,
                  accent: accent,
                ),

                const SizedBox(height: 16),

                // Sentinel Stream (Phase 2 Native Interception)
                Text(
                  "02 // AMBIENT NOTIFICATION SENTINEL STREAM",
                  style: TextStyle(color: textMuted, fontSize: 10, fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 8),
                if (_sentinelStream.isEmpty)
                  Container(
                    padding: const EdgeInsets.all(16),
                    alignment: Alignment.center,
                    decoration: BoxDecoration(
                      color: bgCard,
                      borderRadius: BorderRadius.circular(6),
                      border: Border.all(color: borderColor),
                    ),
                    child: Text(
                      "NO ACTIVE SENTINEL PACKETS INTERCEPTED YET\nWaiting for phone notifications...",
                      textAlign: TextAlign.center,
                      style: TextStyle(color: textMuted, fontSize: 10),
                    ),
                  )
                else
                  ..._sentinelStream.map((packet) => _buildSentinelPacketCard(packet, isDark, borderColor, bgCard)),
              ],
            ),
          ),

          // Bottom Harmonic Soundwave Bar (Vision/Jarvis indicator)
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
            decoration: BoxDecoration(
              color: bgCard,
              border: Border(top: BorderSide(color: borderColor)),
            ),
            child: Row(
              children: [
                Icon(Icons.mic_none, color: accent, size: 20),
                const SizedBox(width: 12),
                Expanded(
                  child: Container(
                    height: 2,
                    decoration: BoxDecoration(
                      color: accent.withOpacity(0.4),
                      borderRadius: BorderRadius.circular(1),
                    ),
                  ),
                ),
                const SizedBox(width: 12),
                Text(
                  "DAKSH LISTENING",
                  style: TextStyle(color: textMuted, fontSize: 9, fontWeight: FontWeight.bold),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildCadenceCard({
    required String title,
    required String status,
    required String time,
    required bool isDue,
    required bool isDark,
    required Color borderColor,
    required Color bgCard,
    required Color accent,
  }) {
    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
      decoration: BoxDecoration(
        color: bgCard,
        borderRadius: BorderRadius.circular(6),
        border: Border.all(color: borderColor),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                title,
                style: TextStyle(
                  color: isDark ? Colors.white : Colors.black87,
                  fontSize: 11,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 2),
              Text(
                status,
                style: TextStyle(
                  color: isDue ? accent : Colors.grey,
                  fontSize: 9,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ],
          ),
          Text(
            time,
            style: TextStyle(
              color: isDark ? const Color(0xFF94A3B8) : const Color(0xFF64748B),
              fontSize: 10,
              fontWeight: FontWeight.bold,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSentinelPacketCard(Map<String, dynamic> packet, bool isDark, Color borderColor, Color bgCard) {
    final title = packet['title'] ?? 'Alert';
    final text = packet['text'] ?? '';
    final pkg = packet['package'] ?? '';
    final isActionable = packet['isActionable'] == true;

    return Container(
      margin: const EdgeInsets.only(bottom: 6),
      padding: const EdgeInsets.all(10),
      decoration: BoxDecoration(
        color: bgCard,
        borderRadius: BorderRadius.circular(6),
        border: Border.all(color: isActionable ? Colors.blue.withOpacity(0.5) : borderColor),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                pkg.toString().split('.').last.toUpperCase(),
                style: TextStyle(color: Colors.blueAccent, fontSize: 8.5, fontWeight: FontWeight.bold),
              ),
              if (isActionable)
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 1),
                  decoration: BoxDecoration(
                    color: Colors.blue.withOpacity(0.2),
                    borderRadius: BorderRadius.circular(3),
                  ),
                  child: const Text("ACTIONABLE", style: TextStyle(color: Colors.blueAccent, fontSize: 7.5, fontWeight: FontWeight.bold)),
                ),
            ],
          ),
          const SizedBox(height: 3),
          Text(title, style: TextStyle(color: isDark ? Colors.white : Colors.black87, fontSize: 10.5, fontWeight: FontWeight.bold)),
          if (text.toString().isNotEmpty)
            Text(text, maxLines: 2, overflow: TextOverflow.ellipsis, style: TextStyle(color: Colors.grey, fontSize: 9.5)),
        ],
      ),
    );
  }
}
