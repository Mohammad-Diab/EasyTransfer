# EasyTransfer Server

A robust Flask-based REST API for managing transfer requests and contacts with JWT authentication. Built with clean architecture principles and comprehensive error handling.

## 🚀 Features

- **JWT Authentication**: Secure token-based authentication system
- **Transfer Requests Management**: Create, track, and manage transfer requests
- **Contact Management**: Add, view, and delete contacts with validation
- **Health Monitoring**: Built-in health check endpoints
- **Clean Architecture**: 3-tier architecture with separation of concerns
- **Comprehensive Validation**: Input validation and error handling
- **SQLite Database**: Lightweight, file-based database solution

## 📁 Project Structure

```
server/
├── app.py                      # Main application entry point
├── config.py                   # Configuration settings
├── constants.py                # Centralized constants and error messages
├── requirements.txt            # Python dependencies
├── db.sqlite3                  # SQLite database file
│
├── database/                   # Database layer
│   ├── __init__.py
│   └── models.py              # Database models and operations
│
├── services/                   # Business logic layer
│   ├── __init__.py
│   ├── request_service.py     # Request business logic
│   └── contact_service.py     # Contact business logic
│
├── routes/                     # API routes layer
│   ├── __init__.py
│   ├── health_routes.py       # Health check endpoints
│   ├── request_routes.py      # Request endpoints
│   └── contact_routes.py      # Contact endpoints
│
└── utils/                      # Utility modules
    ├── __init__.py
    └── auth.py                # JWT authentication utilities
```

## 🏗️ Architecture

The application follows a **3-tier architecture**:

1. **Routes Layer** (`routes/`): Handles HTTP requests/responses and input validation
2. **Services Layer** (`services/`): Contains business logic and validation rules
3. **Database Layer** (`database/`): Manages database operations and queries

### Benefits:
- **Separation of Concerns**: Each layer has a single responsibility
- **Maintainability**: Easy to locate and modify specific functionality
- **Testability**: Each layer can be tested independently
- **Scalability**: Easy to add new features without affecting existing code
- **Reusability**: Services can be used by multiple routes

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.7+
- pip (Python package installer)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd EasyTransfer/server
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Setup**
   Create a `.env` file in the root directory:
   ```env
   JWT_SECRET=your-secret-key-here
   JWT_ALGORITHM=HS256
   FLASK_DEBUG=False
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

The server will start on `http://localhost:5000`

## 📚 API Documentation

### Authentication

All endpoints (except `/ping`) require JWT authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

### Endpoints

#### Health Check
- **GET** `/ping` - Basic health check (no auth required)
- **GET** `/ping-auth` - Authenticated health check

#### Transfer Requests
- **POST** `/requests` - Create a new transfer request
  ```json
  {
    "phone_number": "1234567890",
    "amount": 100.50
  }
  ```

- **GET** `/requests/next` - Get next pending request
- **GET** `/requests/status/{request_id}` - Get request status by ID
- **POST** `/requests/{request_id}/result` - Add result for a request
  ```json
  {
    "status": "Success",
    "message": "Transfer completed"
  }
  ```

#### Contacts
- **GET** `/contacts` - Get all contacts for authenticated account
- **POST** `/contacts` - Add a new contact
  ```json
  {
    "phone_number": "1234567890",
    "name": "John Doe"
  }
  ```
- **DELETE** `/contacts/{contact_id}` - Delete a contact

### Response Format

All responses follow a consistent JSON format:

**Success Response:**
```json
{
  "status": "ok",
  "data": { ... }
}
```

**Error Response:**
```json
{
  "error": "Error message in Arabic"
}
```

## 🗄️ Database Schema

### Tables

#### `requests`
- `id` (INTEGER, PRIMARY KEY)
- `account_id` (INTEGER, NOT NULL)
- `phone_number` (TEXT, NOT NULL)
- `amount` (REAL, NOT NULL)
- `status` (TEXT, NOT NULL, DEFAULT 'Pending')
- `created_at` (TEXT, NOT NULL)

#### `results`
- `id` (INTEGER, PRIMARY KEY)
- `account_id` (INTEGER, NOT NULL)
- `request_id` (INTEGER, NOT NULL, FOREIGN KEY)
- `status` (TEXT, NOT NULL)
- `message` (TEXT)
- `created_at` (TEXT, NOT NULL)

#### `contacts`
- `id` (INTEGER, PRIMARY KEY)
- `account_id` (INTEGER, NOT NULL)
- `phone_number` (TEXT, NOT NULL, CHECK length <= 14)
- `name` (VARCHAR(50), NOT NULL)
- `date_added` (TEXT, NOT NULL)

## ⚙️ Configuration

Edit `config.py` to modify:
- `DB_NAME`: Database file path
- `MAX_CONTACTS_PER_ACCOUNT`: Maximum contacts per account (default: 5)

## 🔒 Security Features

- **JWT Authentication**: Secure token-based authentication
- **Input Validation**: Comprehensive validation for all inputs
- **SQL Injection Protection**: Parameterized queries
- **Account Isolation**: Users can only access their own data
- **Contact Limits**: Maximum contacts per account enforcement
- **Security Headers**: XSS, CSRF, and content-type protection
- **Input Sanitization**: Protection against injection attacks
- **Debug Mode Control**: Production-safe configuration
- **Error Handling**: Secure error messages without information leakage

## 🌍 Internationalization

The application supports Arabic error messages and is structured to easily add more languages in the future. All messages are centralized in `constants.py`.

## 🧪 Development

### Running in Development Mode
```bash
python app.py
```
The server runs in debug mode with auto-reload enabled.

### Code Structure Guidelines
- **Routes**: Handle HTTP requests/responses only
- **Services**: Contain business logic and validation
- **Models**: Handle database operations
- **Constants**: Centralize all messages and configuration values

## 📝 Error Handling

The application provides comprehensive error handling with:
- Input validation errors
- Authentication errors
- Database constraint violations
- Custom business logic errors

All error messages are in Arabic and provide clear feedback to clients.

## 🤝 Contributing

1. Follow the existing code structure and naming conventions
2. Add appropriate error handling for new features
3. Update constants.py for new error messages
4. Maintain the 3-tier architecture pattern
5. Test all endpoints thoroughly

## 📄 License

[Add your license information here]

## 🆘 Support

For support and questions, please [create an issue](link-to-issues) or contact the development team.

---

**Built with ❤️ using Flask, SQLite, and clean architecture principles**