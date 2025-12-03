#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de Debug do Banco.
"""
import os
from BelarminoMonteiroAdvogado import create_app
from BelarminoMonteiroAdvogado.models import db

def run_debug():
    """Executa debug."""
    print("Debug OK.")

if __name__ == '__main__':
    run_debug()