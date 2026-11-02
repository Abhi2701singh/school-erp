import 'package:flutter_test/flutter_test.dart';
import 'package:edumanage_school_erp/main.dart';
import 'package:shared_preferences/shared_preferences.dart';

void main() {
  setUp(() {
    SharedPreferences.setMockInitialValues({});
  });

  testWidgets('App renders splash screen smoke test', (WidgetTester tester) async {
    await tester.pumpWidget(const EduManageSchoolApp());
    expect(find.text('EduManage ERP'), findsOneWidget);
    // Advance time past the splash delay so pending timers are flushed
    await tester.pump(const Duration(milliseconds: 2500));
    await tester.pumpAndSettle();
  });
}
