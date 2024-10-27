import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "InterviewPrpHubBackend.settings")

application = get_wsgi_application()

# This line is crucial for Vercel to find the app
app = application
