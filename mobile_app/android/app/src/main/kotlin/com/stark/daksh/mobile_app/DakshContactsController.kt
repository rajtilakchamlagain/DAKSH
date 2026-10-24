package com.stark.daksh.mobile_app

import android.content.ContentProviderOperation
import android.content.ContentResolver
import android.content.Context
import android.database.Cursor
import android.provider.ContactsContract
import android.util.Log

class DakshContactsController(private val context: Context) {

    companion object {
        private const val TAG = "DakshContacts"
    }

    /**
     * Search contacts by exact or fuzzy name match
     */
    fun findContacts(nameQuery: String): List<Map<String, Any>> {
        val results = mutableListOf<Map<String, Any>>()
        val resolver: ContentResolver = context.contentResolver

        val projection = arrayOf(
            ContactsContract.Contacts._ID,
            ContactsContract.Contacts.DISPLAY_NAME_PRIMARY,
            ContactsContract.Contacts.HAS_PHONE_NUMBER
        )

        val selection = "${ContactsContract.Contacts.DISPLAY_NAME_PRIMARY} LIKE ?"
        val selectionArgs = arrayOf("%$nameQuery%")

        var cursor: Cursor? = null
        try {
            cursor = resolver.query(
                ContactsContract.Contacts.CONTENT_URI,
                projection,
                selection,
                selectionArgs,
                null
            )

            cursor?.let {
                val idIndex = it.getColumnIndex(ContactsContract.Contacts._ID)
                val nameIndex = it.getColumnIndex(ContactsContract.Contacts.DISPLAY_NAME_PRIMARY)

                while (it.moveToNext()) {
                    val id = it.getString(idIndex)
                    val name = it.getString(nameIndex) ?: ""
                    results.add(mapOf("id" to id, "name" to name))
                }
            }
        } catch (e: Exception) {
            Log.e(TAG, "Error querying contacts: ${e.message}", e)
        } finally {
            cursor?.close()
        }

        return results
    }

    /**
     * Renames an existing contact (e.g., from 'Priya' to 'Swimi')
     * Returns true if successfully updated, false otherwise.
     */
    fun renameContact(currentName: String, newName: String): Map<String, Any> {
        val resolver: ContentResolver = context.contentResolver
        val candidates = findContacts(currentName)

        if (candidates.isEmpty()) {
            return mapOf(
                "success" to false,
                "message" to "No contact found matching '$currentName'",
                "recordsModified" to 0
            )
        }

        var updateCount = 0
        try {
            for (contact in candidates) {
                val contactId = contact["id"] as String

                val where = "${ContactsContract.Data.CONTACT_ID} = ? AND ${ContactsContract.Data.MIMETYPE} = ?"
                val params = arrayOf(
                    contactId,
                    ContactsContract.CommonDataKinds.StructuredName.CONTENT_ITEM_TYPE
                )

                val ops = ArrayList<ContentProviderOperation>()
                ops.add(
                    ContentProviderOperation.newUpdate(ContactsContract.Data.CONTENT_URI)
                        .withSelection(where, params)
                        .withValue(ContactsContract.CommonDataKinds.StructuredName.DISPLAY_NAME, newName)
                        .withValue(ContactsContract.CommonDataKinds.StructuredName.GIVEN_NAME, newName)
                        .build()
                )

                val results = resolver.applyBatch(ContactsContract.AUTHORITY, ops)
                if (results.isNotEmpty()) {
                    updateCount++
                    Log.i(TAG, "Successfully renamed contact ID $contactId from '$currentName' to '$newName'")
                }
            }
        } catch (e: Exception) {
            Log.e(TAG, "Error updating contact name: ${e.message}", e)
            return mapOf(
                "success" to false,
                "message" to "Exception during update: ${e.message}",
                "recordsModified" to updateCount
            )
        }

        return mapOf(
            "success" to (updateCount > 0),
            "previousName" to currentName,
            "updatedName" to newName,
            "recordsModified" to updateCount
        )
    }
}
