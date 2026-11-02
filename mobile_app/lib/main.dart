import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:provider/provider.dart';
import 'core/constants/app_colors.dart';
import 'core/theme/app_theme.dart';
import 'providers/auth_provider.dart';
import 'providers/dashboard_provider.dart';
import 'providers/fee_provider.dart';
import 'providers/timetable_provider.dart';
import 'screens/splash_screen.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  SystemChrome.setSystemUIOverlayStyle(
    const SystemUiOverlayStyle(
      statusBarColor: Colors.transparent,
      statusBarIconBrightness: Brightness.dark,
    ),
  );

  runApp(const EduManageSchoolApp());
}

class EduManageSchoolApp extends StatelessWidget {
  const EduManageSchoolApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => AuthProvider()),
        ChangeNotifierProvider(create: (_) => DashboardProvider()),
        ChangeNotifierProvider(create: (_) => FeeProvider()),
        ChangeNotifierProvider(create: (_) => TimetableProvider()),
      ],
      child: MaterialApp(
        title: 'EduManage ERP',
        debugShowCheckedModeBanner: false,
        theme: AppTheme.lightTheme,
        builder: (context, child) {
          final mediaQuery = MediaQuery.of(context);
          // Scale text safely to avoid phone font over-scaling or truncation
          final clampedMediaQuery = mediaQuery.copyWith(
            textScaler: mediaQuery.textScaler.clamp(
              minScaleFactor: 0.85,
              maxScaleFactor: 1.15,
            ),
          );

          return MediaQuery(
            data: clampedMediaQuery,
            child: LayoutBuilder(
              builder: (ctx, constraints) {
                // If viewed on desktop or wide browser, center in a modern mobile frame
                if (constraints.maxWidth > 540) {
                  return Container(
                    color: const Color(0xFF0F172A),
                    alignment: Alignment.center,
                    child: Container(
                      width: 430,
                      decoration: BoxDecoration(
                        color: AppColors.background,
                        boxShadow: [
                          BoxShadow(
                            color: Colors.black.withValues(alpha: 0.35),
                            blurRadius: 28,
                            spreadRadius: 4,
                          ),
                        ],
                      ),
                      child: ClipRRect(
                        child: child!,
                      ),
                    ),
                  );
                }
                return child!;
              },
            ),
          );
        },
        home: const SplashScreen(),
      ),
    );
  }
}
