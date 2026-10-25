enum DakshMode {
  silent,     // Passive, non-intrusive
  listening,  // Active STT capture
  processing, // Routing & reasoning
  speaking,   // Baritone TTS delivery
}

class SessionStateMachine {
  DakshMode _currentMode = DakshMode.silent;
  bool _meetingMode = false;
  int _consecutiveGymSkips = 0;

  DakshMode get currentMode => _currentMode;
  bool get isMeetingMode => _meetingMode;
  int get consecutiveGymSkips => _consecutiveGymSkips;

  void setMode(DakshMode mode) {
    _currentMode = mode;
  }

  void toggleMeetingMode(bool active) {
    _meetingMode = active;
    if (_meetingMode) {
      _currentMode = DakshMode.silent;
    }
  }

  void recordGymSkip() {
    _consecutiveGymSkips++;
  }

  void resetGymSkips() {
    _consecutiveGymSkips = 0;
  }

  /// Evaluates if DAKSH should push back on user's habit deferral
  String? evaluatePushback(String intent) {
    if (intent.contains('skip gym') || intent.contains('skip workout')) {
      _consecutiveGymSkips++;
      if (_consecutiveGymSkips >= 3) {
        return "That's $_consecutiveGymSkips gym skips in a row. Are you certain you want to stand down?";
      }
      return "Understood. But your momentum drops by 20% on back-to-back rest days.";
    }
    return null;
  }

  /// Detects command to return to stealth/silent state
  bool isStandDownCommand(String transcript) {
    final lower = transcript.toLowerCase().trim();
    return lower.contains('go silent') ||
        lower.contains('stand down') ||
        lower.contains('stop listening') ||
        lower.contains('sleep') ||
        lower.contains('shutup');
  }
}
