import 'package:flutter_test/flutter_test.dart';
import 'package:mobile_app/main.dart';

void main() {
  testWidgets('DAKSH app smoke test', (WidgetTester tester) async {
    // Build our app and trigger a frame.
    await tester.pumpWidget(const DakshApp());

    // Verify D.A.K.S.H. header renders
    expect(find.text('D.A.K.S.H.'), findsOneWidget);
  });
}
