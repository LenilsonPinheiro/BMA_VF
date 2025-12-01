#!/usr/bin/env python
import tempfile
import os
import sqlite3

from BelarminoMonteiroAdvogado import create_app
from BelarminoMonteiroAdvogado.models import db, ThemeSettings
from sqlalchemy import inspect as sqlalchemy_inspect

def run_debug():
    tmpdir = tempfile.mkdtemp()
    db_path = os.path.join(tmpdir, 'test.db')
    print('DEBUG: temp db_path =', db_path)

    app = create_app()
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    with app.app_context():
        print('DEBUG: app.config[SQLALCHEMY_DATABASE_URI]=', app.config['SQLALCHEMY_DATABASE_URI'])
        try:
            engine = db.get_engine()
        except Exception:
            engine = db.engine
        print('DEBUG: db.engine =', engine)
        insp = sqlalchemy_inspect(engine)
        print('DEBUG: inspector.get_table_names() BEFORE create_all ->', insp.get_table_names())

        # Show ThemeSettings table metadata
        try:
            print('DEBUG: ThemeSettings.__table__ name =', ThemeSettings.__table__.name)
            print('DEBUG: ThemeSettings columns =', [c.name for c in ThemeSettings.__table__.columns])
        except Exception as e:
            print('DEBUG: error inspecting ThemeSettings table metadata:', e)

        print('[DEBUG] Running db.create_all()')
        db.create_all()
        print('[DEBUG] db.create_all() completed')

        insp2 = sqlalchemy_inspect(engine)
        print('DEBUG: inspector.get_table_names() AFTER create_all ->', insp2.get_table_names())

        # Check PRAGMA directly
        if app.config['SQLALCHEMY_DATABASE_URI'].startswith('sqlite:///'):
            path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
            conn = sqlite3.connect(path)
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(theme_settings)")
            rows = cursor.fetchall()
            print('DEBUG: PRAGMA table_info rows:', rows)
            conn.close()

if __name__ == '__main__':
    run_debug()
