package com.stark.daksh.mobile_app

import android.app.Notification
import android.content.Intent
import android.os.Bundle
import android.service.notification.NotificationListenerService
import android.service.notification.StatusBarNotification
import android.util.Log

class DakshNotificationService : NotificationListenerService() {

    companion object {
        private const val TAG = "DakshSentinel"
        var notificationListener: ((Map<String, Any?>) -> Unit)? = null
    }

    override fun onListenerConnected() {
        super.onListenerConnected()
        Log.i(TAG, "D.A.K.S.H. Sentinel Service connected to Android Notification Subsystem.")
    }

    override fun onNotificationPosted(sbn: StatusBarNotification?) {
        super.onNotificationPosted(sbn)
        if (sbn == null) return

        val packageName = sbn.packageName ?: "unknown"
        val extras: Bundle? = sbn.notification.extras
        val title = extras?.getCharSequence(Notification.EXTRA_TITLE)?.toString() ?: ""
        val text = extras?.getCharSequence(Notification.EXTRA_TEXT)?.toString() ?: ""
        val subText = extras?.getCharSequence(Notification.EXTRA_SUB_TEXT)?.toString() ?: ""
        val postTime = sbn.postTime

        // Ignore our own notifications or blank system toasts
        if (packageName == applicationContext.packageName || (title.isBlank() && text.isBlank())) {
            return
        }

        // Triage classification
        val isActionable = isActionableNotification(packageName, title, text)

        val payload = mapOf(
            "package" to packageName,
            "title" to title,
            "text" to text,
            "subText" to subText,
            "timestamp" to postTime,
            "isActionable" to isActionable
        )

        Log.d(TAG, "Notification Captured: [$packageName] $title - $text | Actionable: $isActionable")
        notificationListener?.invoke(payload)
    }

    /**
     * Filters marketing noise vs actionable communications
     */
    private fun isActionableNotification(pkg: String, title: String, text: String): Boolean {
        val content = "$title $text".lowercase()

        // High priority triggers
        val priorityKeywords = listOf(
            "otp", "code", "verif", "arriving", "delivery", "delivered",
            "order", "urgent", "call", "reminder", "appointment", "alert"
        )

        if (priorityKeywords.any { content.contains(it) }) {
            return true
        }

        // Priority packages (Messaging, Delivery, Ride)
        val priorityPackages = listOf(
            "whatsapp", "telegram", "mms", "messaging", "dialer",
            "swiggy", "zomato", "amazon", "flipkart", "uber", "ola"
        )

        return priorityPackages.any { pkg.lowercase().contains(it) }
    }
}
