"""Configuration settings for the application."""
import os

# ERPNext Configuration
ERP_URL = os.environ.get('ERP_URL', 'https://demo.erpnext.com')
ERP_API_KEY = os.environ.get('ERP_API_KEY', 'DEMO_KEY')
ERP_API_SECRET = os.environ.get('ERP_API_SECRET', 'DEMO_SECRET')
ERP_MOCK_MODE = os.environ.get('ERP_MOCK_MODE', 'true').lower() == 'true'

# AI Configuration - GitHub Models (Primary - Free)
AI_ENDPOINT = os.environ.get('AI_ENDPOINT', 'https://models.inference.ai.azure.com/chat/completions')
AI_MODEL = os.environ.get('AI_MODEL', 'gpt-4o')
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN', '')

# AI Configuration - Azure AI Foundry (Fallback - Paid)
AZURE_AI_ENDPOINT = os.environ.get('AZURE_AI_ENDPOINT', '')
AZURE_AI_KEY = os.environ.get('AZURE_AI_KEY', '')
AZURE_AI_MODEL = 'Phi-4'

# CORS Configuration
CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*').split(',')
