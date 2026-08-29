"""
Cloudflare Worker Entrypoint for Django ERP.
Bridges Cloudflare Python Workers ASGI requests to Django ASGI application.
"""
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "school_erp.settings")
django.setup()

from school_erp.asgi import application

async def on_fetch(request, env):
    """
    Cloudflare Worker Fetch Event Handler
    """
    # Cloudflare Python Workers ASGI interface
    return await application(request, env)
