import 'dart:async';
import 'package:flutter/foundation.dart';
import 'package:speech_to_text/speech_to_text.dart' as stt;

/// Manages multi-lingual speech recognition (en_US, hi_IN, ne_NP)
/// with graceful fallback on unsupported targets or web simulator.
class VoiceInputController {
  final stt.SpeechToText _speech = stt.SpeechToText();
  bool _isAvailable = false;
  bool _isListening = false;
  String _currentLocaleId = 'en_US';

  bool get isAvailable => _isAvailable;
  bool get isListening => _isListening;
  String get currentLocaleId => _currentLocaleId;

  final StreamController<String> _transcriptController = StreamController<String>.broadcast();
  final StreamController<double> _soundLevelController = StreamController<double>.broadcast();

  Stream<String> get transcriptStream => _transcriptController.stream;
  Stream<double> get soundLevelStream => _soundLevelController.stream;

  Future<bool> initialize() async {
    try {
      _isAvailable = await _speech.initialize(
        onError: (val) {
          debugPrint('STT Error: $val');
          _isListening = false;
        },
        onStatus: (val) {
          debugPrint('STT Status: $val');
          if (val == 'done' || val == 'notListening') {
            _isListening = false;
          }
        },
      );
      return _isAvailable;
    } catch (e) {
      debugPrint('VoiceInput initialize exception (running mock fallback): $e');
      _isAvailable = false;
      return false;
    }
  }

  void setLocale(String localeId) {
    _currentLocaleId = localeId;
  }

  Future<void> startListening({required Function(String text, bool isFinal) onResult}) async {
    if (!_isAvailable) {
      bool initialized = await initialize();
      if (!initialized) {
        // Fallback or simulated voice input if native STT is missing
        _isListening = true;
        _transcriptController.add("Listening (Simulated input ready)...");
        return;
      }
    }

    try {
      _isListening = true;
      await _speech.listen(
        onResult: (result) {
          final words = result.recognizedWords;
          _transcriptController.add(words);
          onResult(words, result.finalResult);
        },
        onSoundLevelChange: (level) {
          _soundLevelController.add(level);
        },
        localeId: _currentLocaleId,
        listenMode: stt.ListenMode.dictation,
        cancelOnError: true,
        partialResults: true,
      );
    } catch (e) {
      debugPrint('VoiceInput startListening error: $e');
      _isListening = false;
    }
  }

  Future<void> stopListening() async {
    try {
      if (_isListening) {
        await _speech.stop();
        _isListening = false;
      }
    } catch (e) {
      debugPrint('VoiceInput stopListening error: $e');
      _isListening = false;
    }
  }

  void dispose() {
    _transcriptController.close();
    _soundLevelController.close();
  }
}
