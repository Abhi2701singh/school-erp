export async function onRequest(context) {
  const url = new URL(context.request.url);
  
  // 1. Try serving static asset directly from Cloudflare Pages Edge
  try {
    const asset = await context.env.ASSETS.fetch(context.request);
    if (asset.status < 400) {
      return asset;
    }
  } catch (e) {
    // Continue if asset not found
  }

  // 2. Proxy dynamic requests through Cloudflare Global Edge
  const backendHost = "edumanage-school-erp.onrender.com";
  const backendOrigin = "https://" + backendHost;
  const targetUrl = backendOrigin + url.pathname + url.search;

  // Clone headers
  const newHeaders = new Headers(context.request.headers);
  newHeaders.set("Host", backendHost);
  newHeaders.set("X-Forwarded-Host", url.host);
  newHeaders.set("X-Forwarded-Proto", "https");

  // Preserve CF connecting IP
  const clientIp = context.request.headers.get("CF-Connecting-IP") || "";
  if (clientIp) {
    newHeaders.set("CF-Connecting-IP", clientIp);
    newHeaders.set("X-Real-IP", clientIp);
  }

  const isBodyMethod = ["POST", "PUT", "PATCH", "DELETE"].includes(context.request.method.toUpperCase());
  const body = isBodyMethod ? context.request.body : undefined;

  const fetchOptions = {
    method: context.request.method,
    headers: newHeaders,
    body: body,
    redirect: "manual",
  };

  // Node/V8 stream duplex support
  if (body) {
    fetchOptions.duplex = "half";
  }

  const response = await fetch(targetUrl, fetchOptions);

  // Rewrite redirect headers to keep user on Cloudflare Pages domain (*.pages.dev)
  if ([301, 302, 303, 307, 308].includes(response.status)) {
    const location = response.headers.get("Location");
    if (location) {
      const redirectedLocation = location.replace(backendOrigin, "").replace(/^https?:\/\/[^\/]+/, "");
      const newResponseHeaders = new Headers(response.headers);
      newResponseHeaders.set("Location", redirectedLocation.startsWith("/") ? redirectedLocation : "/" + redirectedLocation);
      return new Response(response.body, {
        status: response.status,
        statusText: response.statusText,
        headers: newResponseHeaders,
      });
    }
  }

  return response;
}
