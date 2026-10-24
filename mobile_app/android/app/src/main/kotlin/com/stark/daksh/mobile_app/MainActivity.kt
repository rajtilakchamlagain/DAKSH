package com.stark.daksh.mobile_app

import android.content.Intent
import android.os.Build
import android.provider.Settings
import androidx.annotation.NonNull
import io.flutter.embedding.android.FlutterActivity
import io.flutter.embedding.engine.FlutterEngine
import io.flutter.plugin.common.EventChannel
import io.flutter.plugin.common.MethodChannel

class MainActivity : FlutterActivity() {

    private val METHOD_CHANNEL = "com.stark.daksh/device_control"
    private val NOTIF_EVENT_CHANNEL = "com.stark.daksh/notification_stream"

    private lateinit var contactsController: DakshContactsController

    override fun configureFlutterEngine(@NonNull flutterEngine: FlutterEngine) {
        super.configureFlutterEngine(flutterEngine)

        contactsController = DakshContactsController(applicationContext)

        // Method Channel for discrete device commands
        MethodChannel(flutterEngine.dartExecutor.binaryMessenger, METHOD_CHANNEL).setMethodCallHandler { call, result ->
            when (call.method) {
                "checkNotificationPermission" -> {
                    val enabled = isNotificationListenerEnabled()
                    result.success(enabled)
                }
                "openNotificationSettings" -> {
                    openNotificationListenerSettings()
                    result.success(true)
                }
                "findContacts" -> {
                    val query = call.argument<String>("query") ?: ""
                    val contacts = contactsController.findContacts(query)
                    result.success(contacts)
                }
                "renameContact" -> {
                    val currentName = call.argument<String>("currentName") ?: ""
                    val newName = call.argument<String>("newName") ?: ""
                    val outcome = contactsController.renameContact(currentName, newName)
                    result.success(outcome)
                }
                else -> {
                    result.notImplemented()
                }
            }
        }

        // Event Channel for real-time streaming notifications from background sentinel
        EventChannel(flutterEngine.dartExecutor.binaryMessenger, NOTIF_EVENT_CHANNEL).setStreamHandler(
            object : EventChannel.StreamHandler {
                override fun onListen(arguments: Any?, events: EventChannel.EventSink?) {
                    DakshNotificationService.notificationListener = { payload ->
                        runOnUiThread {
                            events?.success(payload)
                        }
                    }
                }

                override fun onCancel(arguments: Any?) {
                    DakshNotificationService.notificationListener = null
                }
            }
        )
    }

    private fun isNotificationListenerEnabled(): Boolean {
        val packageName = packageName
        val flat = Settings.Secure.getString(contentResolver, "enabled_notification_listeners")
        return flat != null && flat.contains(packageName)
    }

    private fun openNotificationListenerSettings() {
        val intent = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP_MR1) {
            Intent(Settings.ACTION_NOTIFICATION_LISTENER_SETTINGS)
        } else {
            Intent("android.settings.ACTION_NOTIFICATION_LISTENER_SETTINGS")
        }
        intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
        startActivity(intent)
    }
}
