"""Compatibility helpers applied early to ensure tests that rely on
older SQLAlchemy APIs keep working.

This module is imported very early from `BelarminoMonteiroAdvogado.__init__`.
It adds a small `table_names()` compatibility method on SQLAlchemy Engine
instances so code/tests that call `engine.table_names()` keep working.
"""
from sqlalchemy import inspect
import sqlalchemy.engine


def _engine_table_names(self):
    try:
        return inspect(self).get_table_names()
    except Exception:
        # Fallback: attempt to read table names from dialect if possible
        try:
            return list(self.dialect.get_table_names(self))
        except Exception:
            return []


# Attach compat method to Engine class if not present
if not hasattr(sqlalchemy.engine.Engine, 'table_names'):
    setattr(sqlalchemy.engine.Engine, 'table_names', _engine_table_names)
