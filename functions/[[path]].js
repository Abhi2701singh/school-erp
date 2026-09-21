export async function onRequest(context) {
  try {
    const url = new URL(context.request.url);
    
    // 1. Static assets direct from Cloudflare Edge
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

    // 2. Proxy dynamic requests
    const backendHost = "edumanage-school-erp.onrender.com";
    const backendOrigin = "https://" + backendHost;
    const targetUrl = new URL(url.pathname + url.search, backendOrigin);

    const newHeaders = new Headers(context.request.headers);
    newHeaders.set("Host", backendHost);
    newHeaders.set("X-Forwarded-Host", url.host);
    newHeaders.set("X-Forwarded-Proto", "https");

    // Rewrite Origin and Referer so Django CSRF/Origin validation is 100% satisfied
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

    // Build fresh response headers with separate Set-Cookie entries
    const resHeaders = new Headers();
    for (const [key, value] of response.headers.entries()) {
      const lowerKey = key.toLowerCase();
      if (lowerKey !== "set-cookie" && lowerKey !== "location") {
        resHeaders.set(key, value);
      }
    }

    // Handle redirects
    if ([301, 302, 303, 307, 308].includes(response.status)) {
      const location = response.headers.get("Location");
      if (location) {
        const redirectedLocation = location.replace(backendOrigin, "").replace(/^https?:\/\/[^\/]+/, "");
        const cleanLocation = redirectedLocation.startsWith("/") ? redirectedLocation : "/" + redirectedLocation;
        resHeaders.set("Location", cleanLocation);
      }
    }

    // Extract all Set-Cookie headers cleanly for Safari/Chrome compatibility
    let rawCookies = [];
    if (typeof response.headers.getSetCookie === "function") {
      rawCookies = response.headers.getSetCookie();
    } else {
      const singleCookie = response.headers.get("Set-Cookie");
      if (singleCookie) {
        rawCookies = singleCookie.split(/,\s*(?=[a-zA-Z0-9_\-]+=[^;]+)/g);
      }
    }

    if (rawCookies && rawCookies.length > 0) {
      for (const cookie of rawCookies) {
        if (!cookie) continue;
        // Strip backend domain if present so cookie binds directly to pages.dev domain
        const cleanCookie = cookie.replace(/Domain=[^;]+;?\s*/gi, "").trim();
        resHeaders.append("Set-Cookie", cleanCookie);
      }
    }

    return new Response(response.body, {
      status: response.status,
      statusText: response.statusText,
      headers: resHeaders,
    });
  } catch (err) {
    return new Response("Edge Gateway Exception: " + err.message + "\n" + err.stack, {
      status: 500,
      headers: { "Content-Type": "text/plain" },
    });
  }
}
