from flask import Flask
import sys
import os

# Aggiungi la directory principale al path di Python
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importa l'app Flask dal file app.py principale
from app import app

# Vercel richiede che l'app Flask sia esposta come 'app'
# Non è necessario un handler specifico
