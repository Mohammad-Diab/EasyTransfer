package com.example.easytransfer

import android.Manifest
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Bundle
import android.widget.Toast
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material3.Button
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.input.ImeAction
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.input.PasswordVisualTransformation
import com.example.easytransfer.ui.theme.EasyTransferTheme
import androidx.core.content.ContextCompat
import androidx.core.content.edit
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import org.json.JSONObject
import java.net.HttpURLConnection
import java.net.URL
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.ui.unit.dp

class MainActivity : ComponentActivity() {

    private val requestPermissionLauncher =
        registerForActivityResult(ActivityResultContracts.RequestMultiplePermissions()) { permissions ->
            val granted = permissions[Manifest.permission.CALL_PHONE] == true &&
                    permissions[Manifest.permission.READ_PHONE_STATE] == true

            if (granted) {
                startRequestService()
            } else {
                Toast.makeText(
                    this,
                    "ليعمل التطبيق يجب منح الصلاحيات المطلوبة",
                    Toast.LENGTH_LONG
                ).show()

                finishAffinity()
            }
        }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()

        if (ContextCompat.checkSelfPermission(this, Manifest.permission.CALL_PHONE)
            != PackageManager.PERMISSION_GRANTED ||
            ContextCompat.checkSelfPermission(this, Manifest.permission.READ_PHONE_STATE)
            != PackageManager.PERMISSION_GRANTED) {

            requestPermissionLauncher.launch(
                arrayOf(
                    Manifest.permission.CALL_PHONE,
                    Manifest.permission.READ_PHONE_STATE
                )
            )
        } else {
            startRequestService()
        }

        setContent {
            EasyTransferTheme {
                ApiTokenScreen()
            }
        }
    }

    private fun startRequestService() {
        val intent = Intent(this, RequestService::class.java)
        ContextCompat.startForegroundService(this, intent)
    }
}


@Composable
fun ApiTokenScreen(context: Context = LocalContext.current) {
    val prefs = context.getSharedPreferences("my_prefs", Context.MODE_PRIVATE)

    var serverUrl by remember {
        mutableStateOf(prefs.getString("server_url", null))
    }

    var apiToken by remember {
        mutableStateOf(prefs.getString("api_token", null))
    }

    var transPassword by remember {
        mutableStateOf(prefs.getString("password", null))
    }

    var server by remember { mutableStateOf(serverUrl ?: "") }
    var token by remember { mutableStateOf(apiToken ?: "") }
    var password by remember { mutableStateOf(transPassword?: "") }
    val scope = rememberCoroutineScope()
    var errorMessage by remember { mutableStateOf<String?>(null) }


    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        verticalArrangement = Arrangement.Center,
        horizontalAlignment = Alignment.CenterHorizontally
    ) {

        if (apiToken.isNullOrEmpty() || serverUrl.isNullOrEmpty() || transPassword.isNullOrEmpty()) {
            Text("اضف عنوان السيرفر والتوكن وكلمة سر التحويل")

            Spacer(modifier = Modifier.height(16.dp))

            OutlinedTextField(
                value = server,
                onValueChange = { server = it },
                label = { Text("أدخل عنوان السيرفر") }
            )

            Spacer(modifier = Modifier.height(8.dp))

            OutlinedTextField(
                value = token,
                onValueChange = { token = it },
                label = { Text("أدخل API Token") }
            )

            Spacer(modifier = Modifier.height(8.dp))

            OutlinedTextField(
                value = password,
                onValueChange = { password = it },
                label = { Text("ادخل كلمة سر تحويل الرصيد") },
                keyboardOptions = KeyboardOptions(
                    keyboardType = KeyboardType.Number,
                    imeAction = ImeAction.Done
                ),
                visualTransformation = PasswordVisualTransformation()
            )

            Spacer(modifier = Modifier.height(8.dp))

            Button(onClick = {
                if (server.isNotBlank() && token.isNotBlank()) {
                    scope.launch(Dispatchers.IO) {
                        val result = testConnection(server, token)
                        result.onSuccess {
                            prefs.edit {
                                putString("server_url", server)
                                putString("api_token", token)
                                putString("password", password)
                            }

                            serverUrl = server
                            apiToken = token
                            transPassword = password

                            errorMessage = null
                        }.onFailure { e ->
                            errorMessage = "خطأ بالاتصال: ${e.message}"
                        }
                    }
                }
            }) {
                Text("حفظ")
            }

            errorMessage?.let {
                Spacer(modifier = Modifier.height(8.dp))
                Text(it, color = Color.Red)
            }
        } else {
            Text("✅ متصل")
        }
    }
}

fun testConnection(baseUrl: String, token: String): Result<Boolean> {
    return try {
        val url = URL("$baseUrl/ping-auth")
        val connection = url.openConnection() as HttpURLConnection
        connection.requestMethod = "GET"
        connection.setRequestProperty("Authorization", "Bearer $token")
        connection.connectTimeout = 5000
        connection.readTimeout = 5000

        val responseCode = connection.responseCode
        if (responseCode == HttpURLConnection.HTTP_OK) {
            val response = connection.inputStream.bufferedReader().use { it.readText() }
            val json = JSONObject(response)
            val status = json.optString("status")

            if (status.trim().equals("pong", ignoreCase = true)) {
                Result.success(true)
            } else {
                Result.failure(Exception("Unexpected response: $response"))
            }
        } else {
            Result.failure(Exception("HTTP error code: $responseCode"))
        }
    } catch (e: Exception) {
        Result.failure(e)
    }
}