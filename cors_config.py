from flask_cors import CORS
from flask import Flask
app = Flask(__name__)
CORS(app, resources={
    r"/*": {
        "origins": [
            "http://localhost:5173",  # Local development
            "https://axion-digitaverse.vercel.app",  # Production frontend
            "https://axion-digitaverse-git-main-codes-projects-57d381b5.vercel.app",  # Preview frontend
        ],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})