export default {
  // 1. Automatic Cron Trigger: Runs every 5 minutes around the clock
  async scheduled(event, env, ctx) {
    const targets = [
      "https://edumanage-school-erp.pages.dev/accounts/login/",
      "https://edumanage-school-erp.onrender.com/accounts/login/"
    ];

    ctx.waitUntil(
      Promise.all(
        targets.map(async (url) => {
          try {
            const res = await fetch(url, {
              headers: { "User-Agent": "Cloudflare-247-KeepAlive-Bot/1.0" }
            });
            console.log(`[KeepAlive] Pinged ${url} => HTTP ${res.status}`);
          } catch (e) {
            console.error(`[KeepAlive Error] ${url} => ${e.message}`);
          }
        })
      )
    );
  },

  // 2. HTTP Status Endpoint: Check keep-alive health
  async fetch(request, env, ctx) {
    const resPages = await fetch("https://edumanage-school-erp.pages.dev/accounts/login/");
    const resBackend = await fetch("https://edumanage-school-erp.onrender.com/accounts/login/");

    return new Response(
      JSON.stringify(
        {
          service: "EduManage ERP 24/7 Keep-Alive",
          cron_frequency: "Every 5 minutes",
          status: "ONLINE & ACTIVE",
          cloudflare_pages_status: resPages.status,
          backend_server_status: resBackend.status,
          cold_start_protection: "ENABLED (Zero Sleep)",
          checked_at: new Date().toISOString()
        },
        null,
        2
      ),
      {
        headers: { "Content-Type": "application/json" }
      }
    );
  }
};
