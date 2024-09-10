
class Config:
    """Base configuration class."""
    # Common configurations across all environments can go here

class DevelopmentConfig(Config):
    """Configuration for development environment."""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "postgres://avnadmin:AVNS_KelLziF-vKSDVytqAOh@pg-2eade052-kishore88-20d6.c.aivencloud.com:14147/defaultdb?sslmode=require"  # Your development database URI

class TestingConfig(Config):
    """Configuration for testing environment."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "postgres://avnadmin:AVNS_KelLziF-vKSDVytqAOh@pg-2eade052-kishore88-20d6.c.aivencloud.com:14147/defaultdb?sslmode=require"  # Your testing database URI