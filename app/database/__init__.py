"""
Database package initialization.
"""
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool


def get_database_engine(database_url):
    """Create and return a database engine."""
    return create_engine(database_url, poolclass=NullPool)


__all__ = ['get_database_engine']
