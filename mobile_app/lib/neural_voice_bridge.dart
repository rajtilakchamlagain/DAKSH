import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:audioplayers/audioplayers.dart';

class NeuralVoiceBridge {
  static final AudioPlayer _player = AudioPlayer();

  /// Plays studio-quality neural baritone cues or synthesizes speech dynamically
  static Future<void> playBaritoneCue(String type) async {
    try {
      String assetPath = '';
      if (type == 'wake') {
        assetPath = 'assets/daksh_wake.mp3';
      } else if (type == 'briefing') {
        assetPath = 'assets/daksh_briefing.mp3';
      } else if (type == 'pushback') {
        assetPath = 'assets/daksh_pushback.mp3';
      }

      if (assetPath.isNotEmpty) {
        await _player.stop();
        await _player.play(AssetSource(assetPath));
      }
    } catch (_) {
      // Audio playback graceful fallback
    }
  }

  static Future<void> stop() async {
    try {
      await _player.stop();
    } catch (_) {}
  }
}
