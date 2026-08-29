class CloudflareMiddleware:
    """
    Middleware to handle Cloudflare Edge Proxy headers:
    - Sets request.META['REMOTE_ADDR'] from 'HTTP_CF_CONNECTING_IP'
    - Captures Cloudflare Ray ID (HTTP_CF_RAY)
    - Captures visitor country (HTTP_CF_IPCOUNTRY)
    - Sets Cloudflare response headers
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

        response = self.get_response(request)

        # 4. Attach Ray ID to response for edge debugging
        if request.cf_ray:
            response['X-CF-Ray'] = request.cf_ray

        return response
