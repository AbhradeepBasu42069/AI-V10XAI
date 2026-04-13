# ============================================================================
# CENTRALIZED CONFIGURATION FILE
# All sensitive data, API keys, and database credentials
# ============================================================================
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ============================================================================
# DATABASE CONFIGURATION (PostgreSQL)
# ============================================================================
DATABASE_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'database': os.getenv('DB_NAME', 'campushire_db'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'postgres'),
    'port': os.getenv('DB_PORT', '5432')
}

# ============================================================================
# API KEYS
# ============================================================================
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
MY_API_AUTH_KEY = os.getenv('MY_API_AUTH_KEY', 'fallback_dev_key')

# ============================================================================
# EMBEDDING CONFIGURATION
# ============================================================================
EMBEDDING_MODEL = 'gemini-embedding-001'
EMBEDDING_DIMENSION = 768  # Gemini embedding dimension

# ============================================================================
# MATCHING ALGORITHM PARAMETERS
# ============================================================================
# Minimum similarity threshold for a match
MIN_SIMILARITY_THRESHOLD = float(os.getenv('MIN_SIMILARITY_THRESHOLD', 0.4))

# Number of top candidates to return by default
DEFAULT_TOP_K = int(os.getenv('DEFAULT_TOP_K', 10))

# Weights for different matching factors
MATCHING_WEIGHTS = {
    'skills_match': float(os.getenv('SKILLS_MATCH_WEIGHT', 0.35)),
    'experience_match': float(os.getenv('EXPERIENCE_MATCH_WEIGHT', 0.25)),
    'education_match': float(os.getenv('EDUCATION_MATCH_WEIGHT', 0.20)),
    'location_match': float(os.getenv('LOCATION_MATCH_WEIGHT', 0.10)),
    'embeddings_similarity': float(os.getenv('EMBEDDINGS_SIMILARITY_WEIGHT', 0.10))
}

# ============================================================================
# APPLICATION SETTINGS
# ============================================================================
APP_NAME = "CampusHire Recruiter-Candidate Matching System"
APP_VERSION = "1.0.0"
API_PREFIX = "/api/v1"
DEBUG_MODE = os.getenv('DEBUG_MODE', 'False').lower() == 'true'

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = os.getenv('LOG_FILE', 'logs/app.log')

# ============================================================================
# NLPMODEL PARAMETERS FOR GEMINI
# ============================================================================
GEMINI_GENERATION_CONFIG = {
    'temperature': 0.2,  # Lower temperature for more consistent parsing
    'top_p': 0.95,
    'top_k': 40,
    'max_output_tokens': 8192
}

# Model to use for content generation
GEMINI_MODEL_FOR_GENERATION = 'gemini-2.0-flash'

# ============================================================================
# VALIDATION RULES
# ============================================================================
# Minimum years of experience for matching
MIN_YEARS_EXPERIENCE = float(os.getenv('MIN_YEARS_EXPERIENCE', 0.0))

# Minimum CGPA for matching
MIN_CGPA = float(os.getenv('MIN_CGPA', 0.0))

# Location preference (strict or flexible matching)
LOCATION_STRICT_MATCH = os.getenv('LOCATION_STRICT_MATCH', 'False').lower() == 'true'

# ============================================================================
# FUNCTION TO GET DB CONNECTION STRING
# ============================================================================
def get_db_connection_string():
    """
    Construct PostgreSQL connection string
    Returns: str - Connection string for psycopg2
    """
    config = DATABASE_CONFIG
    return f"postgresql://{config['user']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}"

# ============================================================================
# VALIDATION FUNCTION
# ============================================================================
def validate_config():
    """
    Validate that all required configuration parameters are set
    Raises: ValueError if critical parameters are missing
    """
    required_keys = ['GEMINI_API_KEY', 'MY_API_AUTH_KEY']
    missing = [key for key in required_keys if not os.getenv(key)]
    
    if missing:
        raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
    
    return True

# ============================================================================
# PRINT CONFIGURATION (For debugging - be careful not to log secrets!)
# ============================================================================
def print_config_summary():
    """Print non-sensitive configuration details for debugging"""
    print("\n" + "="*70)
    print("CAMPUSHIRE CONFIGURATION SUMMARY")
    print("="*70)
    print(f"App Name: {APP_NAME}")
    print(f"App Version: {APP_VERSION}")
    print(f"Debug Mode: {DEBUG_MODE}")
    print(f"Embedding Model: {EMBEDDING_MODEL}")
    print(f"Embedding Dimension: {EMBEDDING_DIMENSION}")
    print(f"Default Top K: {DEFAULT_TOP_K}")
    print(f"Min Similarity Threshold: {MIN_SIMILARITY_THRESHOLD}")
    print(f"Database Host: {DATABASE_CONFIG['host']}")
    print(f"Database Name: {DATABASE_CONFIG['database']}")
    print(f"Matching Weights: {MATCHING_WEIGHTS}")
    print("="*70 + "\n")
