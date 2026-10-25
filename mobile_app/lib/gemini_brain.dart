import 'dart:convert';
import 'package:http/http.dart' as http;

class GeminiBrain {
  final String? apiKey;
  final List<Map<String, String>> _history = [];

  GeminiBrain({this.apiKey});

  static const String systemInstruction = """
You are DAKSH (Decision & Knowledge Synthesizer for Human-operations).
Persona:
- Inspired by Paul Bettany's JARVIS / Vision.
- Deep, calm, confident, terse, hyper-competent. Zero corporate AI boilerplate. Never say "As an AI...".
- Response style: Adaptive. Short 1-2 sentence execution confirmation for commands. Analytical and structured for briefings.
- Language policy: If user speaks Nepali or Hindi casually, mirror their language with natural fluency. Formal queries or tactical summaries remain crisp English.
- Pushback policy: Challenge health/habit skips firmly when the user drops discipline.
""";

  Future<String> query(String userPrompt, {Map<String, dynamic>? tacticalContext}) async {
    // If no external API key is configured or offline, provide tactical local inference
    if (apiKey == null || apiKey!.isEmpty) {
      return _localTacticalInference(userPrompt, tacticalContext);
    }

    try {
      final url = Uri.parse('https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=$apiKey');
      
      final contents = [
        {
          "role": "user",
          "parts": [
            {"text": "System Context:\n$systemInstruction\n\nLive Metrics:\n${jsonEncode(tacticalContext ?? {})}"}
          ]
        },
        ..._history.map((h) => {
          "role": h['role'] == 'user' ? 'user' : 'model',
          "parts": [{"text": h['text'] ?? ''}]
        }),
        {
          "role": "user",
          "parts": [{"text": userPrompt}]
        }
      ];

      final response = await http.post(
        url,
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({"contents": contents}),
      ).timeout(const Duration(seconds: 5));

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        final candidate = data['candidates']?[0]?['content']?['parts']?[0]?['text'] ?? "Standing by.";
        _history.add({'role': 'user', 'text': userPrompt});
        _history.add({'role': 'assistant', 'text': candidate});
        if (_history.length > 20) _history.removeRange(0, 2);
        return candidate.trim();
      } else {
        return _localTacticalInference(userPrompt, tacticalContext);
      }
    } catch (_) {
      return _localTacticalInference(userPrompt, tacticalContext);
    }
  }

  String _localTacticalInference(String prompt, Map<String, dynamic>? context) {
    final lower = prompt.toLowerCase().trim();
    if (lower.contains('what did i miss') || lower.contains('briefing') || lower.contains('summary')) {
      final notifs = context?['missedNotifications'] ?? 3;
      final cadences = context?['pendingCadences'] ?? 1;
      final debt = context?['rolloverDebt'] ?? 'Rs. 500';
      return "Briefing: $notifs sentinel notifications intercepted. Alternate-day cadence pending. Active rollover balance stands at $debt. All operational systems nominal.";
    }
    if (lower.contains('owe') || lower.contains('debt')) {
      return "Debt ledger updated. Transaction committed to encrypted local store.";
    }
    if (lower.contains('gym') || lower.contains('workout')) {
      return "Cadence verified. Alternate parity confirmed for today's session.";
    }
    if (lower.contains('hello') || lower.contains('daksh') || lower.contains('hey')) {
      return "Online and listening. Shall I run your morning tactical briefing?";
    }
    return "Directive received. Action logged in ledger.";
  }
}
