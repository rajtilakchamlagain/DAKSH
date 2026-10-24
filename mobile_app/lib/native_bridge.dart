import 'dart:async';
import 'package:flutter/services.dart';

/// D.A.K.S.H. Sentinel & Device Control Bridge
/// Connects Flutter UI to native Android Subsystems
class DakshNativeBridge {
  static const MethodChannel _methodChannel = MethodChannel('com.stark.daksh/device_control');
  static const EventChannel _notifEventChannel = EventChannel('com.stark.daksh/notification_stream');

  /// Checks if Android NotificationListenerService permission is active
  static Future<bool> isNotificationAccessGranted() async {
    try {
      final bool granted = await _methodChannel.invokeMethod('checkNotificationPermission');
      return granted;
    } on PlatformException catch (e) {
      print("[DAKSH_NATIVE] Error checking notification permission: ${e.message}");
      return false;
    }
  }

  /// Opens the Android system settings page directly to allow notification access
  static Future<void> requestNotificationAccess() async {
    try {
      await _methodChannel.invokeMethod('openNotificationSettings');
    } on PlatformException catch (e) {
      print("[DAKSH_NATIVE] Error opening notification settings: ${e.message}");
    }
  }

  /// Finds contacts matching a name query
  static Future<List<Map<String, dynamic>>> searchContacts(String nameQuery) async {
    try {
      final List<dynamic>? raw = await _methodChannel.invokeMethod('findContacts', {'query': nameQuery});
      if (raw == null) return [];
      return raw.map((item) => Map<String, dynamic>.from(item as Map)).toList();
    } on PlatformException catch (e) {
      print("[DAKSH_NATIVE] Error searching contacts: ${e.message}");
      return [];
    }
  }

  /// Modifies an existing contact's name (e.g. from "Priya" to "Swimi")
  static Future<Map<String, dynamic>> renameContact({
    required String currentName,
    required String newName,
  }) async {
    try {
      final Map<dynamic, dynamic>? outcome = await _methodChannel.invokeMethod('renameContact', {
        'currentName': currentName,
        'newName': newName,
      });
      if (outcome == null) return {'success': false, 'message': 'Null response'};
      return Map<String, dynamic>.from(outcome);
    } on PlatformException catch (e) {
      print("[DAKSH_NATIVE] Error renaming contact: ${e.message}");
      return {'success': false, 'message': e.message};
    }
  }

  /// Stream of live notifications intercepted by DakshNotificationService
  static Stream<Map<String, dynamic>> get notificationStream {
    return _notifEventChannel.receiveBroadcastStream().map((event) {
      return Map<String, dynamic>.from(event as Map);
    });
  }
}
