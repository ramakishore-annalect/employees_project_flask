
class Config:
    """Base configuration class."""
    # Common configurations across all environments can go here

class DevelopmentConfig(Config):
    """Configuration for development environment."""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "postgresql://ramakishorenooji:@localhost/testdb"  # Your development database URI

class TestingConfig(Config):
    """Configuration for testing environment."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "postgresql://ramakishorenooji:@localhost/mock_db"  # Your testing database URI