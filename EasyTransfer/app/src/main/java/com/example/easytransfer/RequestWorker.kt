package com.example.easytransfer

import android.Manifest
import android.annotation.SuppressLint
import android.app.Service
import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.net.Uri
import android.os.Build
import android.os.Handler
import android.os.IBinder
import android.os.Looper
import android.telephony.TelephonyManager
import android.util.Log
import androidx.annotation.RequiresPermission
import androidx.core.app.ActivityCompat
import androidx.core.app.NotificationCompat
import okhttp3.OkHttpClient
import okhttp3.Request
import org.json.JSONObject
import java.io.IOException
import androidx.core.net.toUri
import okhttp3.FormBody
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.RequestBody
import okhttp3.RequestBody.Companion.toRequestBody

class RequestService : Service() {
    private val handler = Handler(Looper.getMainLooper())
    private val client = OkHttpClient()
    private var serverUrl: String? = null
    private var apiToken: String? = null

    private var password: String? = null
    private val delayMs: Long = 30_000

    private val STATUS_FAILED = "Failed"
    private val STATUS_SUCCESS = "Success"

    @SuppressLint("ForegroundServiceType")
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        startForeground(1, createNotification())
        handler.post(taskRunnable)
        return START_STICKY
    }

    private val taskRunnable: Runnable = object : Runnable {
        override fun run() {
            val prefs = getSharedPreferences("my_prefs", MODE_PRIVATE)
            apiToken = prefs.getString("api_token", null)
            serverUrl = prefs.getString("server_url", null)
            password = prefs.getString("password", null)


            if (apiToken.isNullOrEmpty() || serverUrl.isNullOrEmpty() || password.isNullOrEmpty()) {
                Log.d(
                    "RequestService",
                    "⚠️ Service is On... (Server URL or API token is missing, ignoring request)"
                )
                handler.postDelayed(this, delayMs)
                return
            }

            Log.d("RequestService", "🔄 Service is On...")

            val request = Request.Builder()
                .url("$serverUrl/requests/next")
                .addHeader("Authorization", "Bearer $apiToken")
                .build()

            client.newCall(request).enqueue(object : okhttp3.Callback {
                override fun onFailure(call: okhttp3.Call, e: IOException) {
                    Log.e("RequestService", "⚠️ Error: ${e.message}")
                    handler.postDelayed(taskRunnable, delayMs)
                }

                override fun onResponse(call: okhttp3.Call, response: okhttp3.Response) {
                    try {
                        response.use {
                            val body = it.body?.string()?: ""
                            val json = JSONObject(body)
                            val status = json.optString("status")
                            when (status.lowercase()) {
                                "empty" -> {
                                    val msg = json.optString("message")
                                    Log.d("RequestService", "ℹ️ $msg")
                                    handler.postDelayed(taskRunnable, delayMs)
                                }
                                "ok" -> {
                                    val requestId = json.optInt("request_id")
                                    val amount = json.optDouble("amount")
                                    val phone = json.optString("phone_number")

                                    val ussdCode = "*150*1*$password*1*$phone*$phone*$amount#"

                                    val maskedUssdCode = "*150*1*[PASSWORD]*1*$phone*$phone*$amount#"
                                    Log.d("RequestService", "📲 USSD Code: $maskedUssdCode")

                                    if (ActivityCompat.checkSelfPermission(this@RequestService, Manifest.permission.CALL_PHONE)
                                        != PackageManager.PERMISSION_GRANTED) {
                                        updateServer(requestId, STATUS_FAILED, "Permission denied")
                                        handler.postDelayed(taskRunnable, delayMs)
                                        return
                                    }

                                    sendUssd(this@RequestService, ussdCode,
                                        onSuccess = { response ->
                                            updateServer(requestId, STATUS_SUCCESS, response)
                                            handler.postDelayed(taskRunnable, delayMs)
                                        },
                                        onFailure = { code ->
                                            updateServer(requestId, STATUS_FAILED, "code=$code")
                                            handler.postDelayed(taskRunnable, delayMs)
                                        }
                                    )


                                    val encodedUssd = Uri.encode(ussdCode)
                                    val callIntent =
                                        Intent(Intent.ACTION_CALL, "tel:$encodedUssd".toUri())
                                    callIntent.flags = Intent.FLAG_ACTIVITY_NEW_TASK
                                    startActivity(callIntent)
                                }
                                else -> {
                                    Log.e("RequestService", "⚠️ Unexpected status: $status")
                                }
                            }
                        }
                    } catch (e: Exception) {
                        Log.e("RequestService", "⚠️ Error processing response: ${e.message}")
                        handler.postDelayed(taskRunnable, delayMs)
                    }
                }
            })
        }
    }

    private fun createNotification(): Notification {
        val channelId = "request_channel"
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                channelId,
                "Request Service",
                NotificationManager.IMPORTANCE_LOW
            )
            val nm = getSystemService(NOTIFICATION_SERVICE) as NotificationManager
            nm.createNotificationChannel(channel)
        }
        return NotificationCompat.Builder(this, channelId)
            .setContentTitle("EasyTransfer Service")
            .setContentText("Service started ✅")
            .setSmallIcon(R.mipmap.ic_launcher)
            .build()
    }

    override fun onBind(intent: Intent?): IBinder? = null

    @RequiresPermission(Manifest.permission.CALL_PHONE)
    fun sendUssd(
        context: Context,
        ussdCode: String,
        onSuccess: (String) -> Unit,
        onFailure: (Int) -> Unit
    ) {
        val tm = context.getSystemService(TELEPHONY_SERVICE) as TelephonyManager

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val callback = object : TelephonyManager.UssdResponseCallback() {
                override fun onReceiveUssdResponse(
                    telephonyManager: TelephonyManager,
                    request: String,
                    response: CharSequence
                ) {
                    onSuccess(response.toString())
                }

                override fun onReceiveUssdResponseFailed(
                    telephonyManager: TelephonyManager,
                    request: String,
                    failureCode: Int
                ) {
                    onFailure(failureCode)
                }
            }
            tm.sendUssdRequest(ussdCode, callback, Handler(Looper.getMainLooper()))
        } else {
            try {
                val encodedUssd = Uri.encode(ussdCode)
                val callIntent = Intent(Intent.ACTION_CALL, "tel:$encodedUssd".toUri())
                callIntent.flags = Intent.FLAG_ACTIVITY_NEW_TASK
                context.startActivity(callIntent)

                onSuccess("USSD code sent (no response available on this Android version)")
            } catch (e: Exception) {
                onFailure(-1)
            }
        }
    }

    fun updateServer(requestId: Int, status: String, message: String) {
        val json = """{"status": "$status","message": "$message"}""".trimIndent()

        val body = json.toRequestBody("application/json; charset=utf-8".toMediaType())

        val req = Request.Builder()
            .url("$serverUrl/requests/${requestId}/result")
            .post(body)
            .addHeader("Authorization", "Bearer $apiToken")
            .build()

        client.newCall(req).enqueue(object : okhttp3.Callback {
            override fun onFailure(call: okhttp3.Call, e: IOException) {
                Log.e("ServerUpdate", "Failed: ${e.message}")
            }
            override fun onResponse(call: okhttp3.Call, response: okhttp3.Response) {
                Log.d("ServerUpdate", "Updated: ${response.code}")
            }
        })
    }
}