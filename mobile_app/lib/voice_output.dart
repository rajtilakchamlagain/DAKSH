import 'package:flutter/foundation.dart';
import 'package:flutter_tts/flutter_tts.dart';

/// Multi-lingual baritone voice output engine
/// Configured with Paul Bettany / JARVIS acoustic parameters:
/// Pitch lowered (~0.82), speech rate deliberate (~0.46), deep resonance.
class VoiceOutputController {
  final FlutterTts _flutterTts = FlutterTts();
  bool _isPlaying = false;

  bool get isPlaying => _isPlaying;

  Future<void> initialize() async {
    try {
      await _flutterTts.setPitch(0.82); // Lower pitch for deep baritone tone
      await _flutterTts.setSpeechRate(0.46); // Deliberate, tactical speech pace
      await _flutterTts.setVolume(1.0);

      _flutterTts.setStartHandler(() {
        _isPlaying = true;
      });

      _flutterTts.setCompletionHandler(() {
        _isPlaying = false;
      });

      _flutterTts.setErrorHandler((msg) {
        debugPrint('TTS Error: $msg');
        _isPlaying = false;
      });
    } catch (e) {
      debugPrint('VoiceOutputController init exception: $e');
    }
  }

  /// Automatically adapts accent/locale to language matching input context
  Future<void> speak(String text, {String? languageCode}) async {
    try {
      String targetLang = 'en-US';
      if (languageCode != null) {
        if (languageCode.startsWith('hi')) {
          targetLang = 'hi-IN';
        } else if (languageCode.startsWith('ne')) {
          targetLang = 'ne-NP';
        }
      }

      await _flutterTts.setLanguage(targetLang);
      _isPlaying = true;
      await _flutterTts.speak(text);
    } catch (e) {
      debugPrint('VoiceOutputController speak error: $e');
      _isPlaying = false;
    }
  }

  Future<void> stop() async {
    try {
      await _flutterTts.stop();
      _isPlaying = false;
    } catch (e) {
      debugPrint('VoiceOutputController stop error: $e');
    }
  }
}
