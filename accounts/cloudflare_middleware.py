import traceback
import sys

class CloudflareMiddleware:
    """
    Middleware to handle Cloudflare Edge Proxy headers:
    - Sets request.META['REMOTE_ADDR'] from 'HTTP_CF_CONNECTING_IP'
    - Captures Cloudflare Ray ID (HTTP_CF_RAY)
    - Captures visitor country (HTTP_CF_IPCOUNTRY)
    - Sets Cloudflare response headers
    - Captures and displays exception tracebacks for fast resolution
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 1. Real Client IP from Cloudflare
        cf_connecting_ip = request.META.get('HTTP_CF_CONNECTING_IP')
        if cf_connecting_ip:
            request.META['REMOTE_ADDR'] = cf_connecting_ip.split(',')[0].strip()
            request.client_ip = request.META['REMOTE_ADDR']
        else:
            request.client_ip = request.META.get('REMOTE_ADDR', '')

        # 2. Cloudflare Ray ID (Traceability)
        request.cf_ray = request.META.get('HTTP_CF_RAY', '')

        # 3. Visitor Country Code (e.g. 'IN', 'US')
        request.cf_country = request.META.get('HTTP_CF_IPCOUNTRY', '')

        try:
            response = self.get_response(request)
        except Exception as e:
            trace = traceback.format_exc()
            print(f"[500 SERVER EXCEPTION at {request.path}]:\n{trace}", file=sys.stderr)
            from django.http import HttpResponse
            return HttpResponse(
                f"<div style='font-family:sans-serif;padding:30px;max-width:800px;margin:40px auto;border:1px solid #fee2e2;border-radius:12px;background:#fff;box-shadow:0 10px 25px rgba(0,0,0,0.05);'>"
                f"<h2 style='color:#dc2626;margin-top:0;'>Server Exception (500)</h2>"
                f"<p style='color:#6b7280;'>An exception occurred while processing request to <code>{request.path}</code>:</p>"
                f"<pre style='background:#fef2f2;border:1px solid #fca5a5;padding:16px;border-radius:8px;color:#991b1b;font-size:13px;overflow-x:auto;white-space:pre-wrap;'>{trace}</pre>"
                f"</div>",
                status=500
            )

        # 4. Attach Ray ID to response for edge debugging
        if request.cf_ray and response and hasattr(response, '__setitem__'):
            try:
                response['X-CF-Ray'] = request.cf_ray
            except Exception:
                pass

        return response
