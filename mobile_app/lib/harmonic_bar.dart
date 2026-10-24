import 'package:flutter/material.dart';
import 'dart:math' as math;

/// Ultra-fine Harmonic Spectrum Visualizer
/// Displays dynamic audio/reasoning energy without cartoonish graphics.
class HarmonicSpectrumBar extends StatefulWidget {
  final bool isSpeaking;
  final bool isListening;
  final Color accentColor;

  const HarmonicSpectrumBar({
    super.key,
    required this.isSpeaking,
    required this.isListening,
    required this.accentColor,
  });

  @override
  State<HarmonicSpectrumBar> createState() => _HarmonicSpectrumBarState();
}

class _HarmonicSpectrumBarState extends State<HarmonicSpectrumBar>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1200),
    )..repeat();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _controller,
      builder: (context, child) {
        return CustomPaint(
          size: const Size(double.infinity, 18),
          painter: _HarmonicSpectrumPainter(
            animationValue: _controller.value,
            isSpeaking: widget.isSpeaking,
            isListening: widget.isListening,
            accentColor: widget.accentColor,
          ),
        );
      },
    );
  }
}

class _HarmonicSpectrumPainter extends CustomPainter {
  final double animationValue;
  final bool isSpeaking;
  final bool isListening;
  final Color accentColor;

  _HarmonicSpectrumPainter({
    required this.animationValue,
    required this.isSpeaking,
    required this.isListening,
    required this.accentColor,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = accentColor
      ..strokeWidth = 1.2
      ..strokeCap = StrokeCap.round;

    final basePaint = Paint()
      ..color = accentColor.withValues(alpha: 0.15)
      ..strokeWidth = 1.0;

    final centerY = size.height / 2;
    // Base reference line
    canvas.drawLine(Offset(0, centerY), Offset(size.width, centerY), basePaint);

    final barCount = 42;
    final spacing = size.width / barCount;

    for (int i = 0; i < barCount; i++) {
      final x = (i * spacing) + (spacing / 2);
      double amplitude = 1.5;

      if (isSpeaking) {
        // High harmonic oscillation during TTS speech
        final wave1 = math.sin((i / 4.0) + (animationValue * 2 * math.pi));
        final wave2 = math.cos((i / 2.5) - (animationValue * 4 * math.pi));
        amplitude = 2.0 + (wave1 * wave2).abs() * 7.0;
      } else if (isListening) {
        // Gentle breathing pulse while standing by
        final pulse = math.sin((i / 6.0) + (animationValue * 2 * math.pi));
        amplitude = 1.5 + (pulse.abs() * 3.5);
      }

      canvas.drawLine(
        Offset(x, centerY - amplitude),
        Offset(x, centerY + amplitude),
        paint,
      );
    }
  }

  @override
  bool shouldRepaint(covariant _HarmonicSpectrumPainter oldDelegate) {
    return true;
  }
}
