import os

# ERPNext Configuration
ERP_URL = os.environ.get('ERP_URL', 'https://demo.erpnext.com')
ERP_API_KEY = os.environ.get('ERP_API_KEY', 'DEMO_KEY')
ERP_API_SECRET = os.environ.get('ERP_API_SECRET', 'DEMO_SECRET')
ERP_MOCK_MODE = os.environ.get('ERP_MOCK_MODE', 'true').lower() == 'true'

# Azure OpenAI Configuration (Primary AI Service)
AZURE_OPENAI_ENDPOINT = os.environ.get('AZURE_OPENAI_ENDPOINT', '')
AZURE_OPENAI_API_KEY = os.environ.get('AZURE_OPENAI_API_KEY', '')
AZURE_OPENAI_MODEL = os.environ.get('AZURE_OPENAI_MODEL', 'gpt-4o')
AZURE_OPENAI_API_VERSION = os.environ.get('AZURE_OPENAI_API_VERSION', '2024-10-21')

# CORS Configuration
CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*').split(',')
