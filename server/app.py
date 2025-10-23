from flask import Flask
from database.models import init_db
from routes.request_routes import request_bp
from routes.contact_routes import contact_bp
from routes.health_routes import health_bp
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()


def create_app():
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Security configuration
    app.config['SECRET_KEY'] = os.getenv('JWT_SECRET', 'fallback-secret-key')
    
    # Add security headers
    @app.after_request
    def add_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response.headers['Content-Security-Policy'] = "default-src 'self'"
        return response
    
    # Initialize database
    init_db()
    
    # Register blueprints
    app.register_blueprint(request_bp)
    app.register_blueprint(contact_bp)
    app.register_blueprint(health_bp)
    
    return app


if __name__ == '__main__':
    app = create_app()
    # Only run in debug mode if explicitly set in environment
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(debug=debug_mode)
