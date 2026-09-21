export async function onRequest(context) {
  try {
    const url = new URL(context.request.url);
    
    // 1. Serve static assets directly from Cloudflare Pages Edge
    if (context.request.method === "GET" || context.request.method === "HEAD") {
      if (url.pathname.startsWith("/static/") || url.pathname === "/favicon.ico") {
        try {
          const asset = await context.env.ASSETS.fetch(context.request);
          if (asset && asset.status < 400) {
            return asset;
          }
        } catch (e) {
          // Fallback to backend
        }
      }
    }

    // 2. Proxy dynamic requests through Cloudflare Global Edge
    const backendHost = "edumanage-school-erp.onrender.com";
    const backendOrigin = "https://" + backendHost;
    const targetUrl = new URL(url.pathname + url.search, backendOrigin);

    // Clone headers
    const newHeaders = new Headers(context.request.headers);
    newHeaders.set("Host", backendHost);
    newHeaders.set("X-Forwarded-Host", url.host);
    newHeaders.set("X-Forwarded-Proto", "https");

    // Rewrite Origin & Referer to backendOrigin so Django CSRF/Origin checks always succeed
    const origin = context.request.headers.get("Origin");
    if (origin) {
      newHeaders.set("Origin", backendOrigin);
    }
    const referer = context.request.headers.get("Referer");
    if (referer) {
      newHeaders.set("Referer", referer.replace(url.origin, backendOrigin));
    }

    const clientIp = context.request.headers.get("CF-Connecting-IP") || "";
    if (clientIp) {
      newHeaders.set("CF-Connecting-IP", clientIp);
      newHeaders.set("X-Real-IP", clientIp);
    }

    const init = {
      method: context.request.method,
      headers: newHeaders,
      redirect: "manual",
    };

    if (context.request.method !== "GET" && context.request.method !== "HEAD") {
      init.body = await context.request.arrayBuffer();
    }

    const response = await fetch(targetUrl.toString(), init);

    // Build response headers
    const responseHeaders = new Headers(response.headers);

    // Rewrite redirect location to keep user seamlessly on Cloudflare domain (*.pages.dev)
    const location = response.headers.get("Location");
    if (location) {
      const redirectedLocation = location.replace(backendOrigin, "").replace(/^https?:\/\/[^\/]+/, "");
      responseHeaders.set("Location", redirectedLocation.startsWith("/") ? redirectedLocation : "/" + redirectedLocation);
    }

    return new Response(response.body, {
      status: response.status,
      statusText: response.statusText,
      headers: responseHeaders,
    });
  } catch (err) {
    return new Response("Edge Gateway Exception: " + err.message + "\n" + err.stack, {
      status: 500,
      headers: { "Content-Type": "text/plain" },
    });
  }
}
