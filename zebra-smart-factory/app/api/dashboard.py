"""Dashboard and demo routes."""
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
@router.get("/dashboard", response_class=HTMLResponse)
@router.get("/demo", response_class=HTMLResponse)
async def dashboard():
    """ZebraStream IoT Demo Dashboard."""
    html = _DASHBOARD_HTML
    return HTMLResponse(html)


_DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>ZebraStream IoT Demo | Industry 4.0</title>
  <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
  <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&family=Space+Grotesk:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg: #0f0f12;
      --surface: #1a1a1f;
      --border: #2a2a32;
      --accent: #00d4aa;
      --accent-dim: #00a884;
      --text: #e4e4e7;
      --text-muted: #71717a;
      --danger: #f43f5e;
      --warn: #f59e0b;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: 'Space Grotesk', sans-serif;
      background: var(--bg);
      color: var(--text);
      min-height: 100vh;
      line-height: 1.6;
    }
    .header {
      background: linear-gradient(180deg, var(--surface) 0%, transparent 100%);
      border-bottom: 1px solid var(--border);
      padding: 1.5rem 2rem;
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 1rem;
    }
    .logo { font-size: 1.5rem; font-weight: 700; color: var(--accent); }
    .subtitle { font-size: 0.85rem; color: var(--text-muted); margin-top: 0.25rem; }
    .links a {
      color: var(--accent);
      text-decoration: none;
      margin-left: 1rem;
      font-size: 0.9rem;
    }
    .links a:hover { text-decoration: underline; }
    .container { max-width: 1400px; margin: 0 auto; padding: 2rem; }
    .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 1.5rem; }
    .card {
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 1.5rem;
      overflow: hidden;
    }
    .card h2 { font-size: 1rem; color: var(--text-muted); margin-bottom: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em; }
    .card h3 { font-size: 1.25rem; margin-bottom: 1rem; color: var(--accent); }
    .stat-row { display: flex; justify-content: space-between; padding: 0.5rem 0; border-bottom: 1px solid var(--border); font-family: 'JetBrains Mono', monospace; }
    .stat-row:last-child { border-bottom: none; }
    .stat-label { color: var(--text-muted); }
    .stat-value { color: var(--accent); }
    .summary-box {
      background: rgba(0, 212, 170, 0.08);
      border: 1px solid rgba(0, 212, 170, 0.2);
      border-radius: 8px;
      padding: 1rem;
      margin-top: 1rem;
      font-size: 0.95rem;
    }
    .rec-list { list-style: none; margin-top: 0.5rem; }
    .rec-list li { padding: 0.35rem 0; padding-left: 1.25rem; position: relative; }
    .rec-list li::before { content: "→"; position: absolute; left: 0; color: var(--accent); }
    .chart-container { min-height: 320px; }
    .loading { color: var(--text-muted); padding: 2rem; text-align: center; }
    .error { color: var(--danger); padding: 1rem; }
    .section { margin-bottom: 2rem; }
    .section-title { font-size: 1.5rem; margin-bottom: 1rem; color: var(--text); }
  </style>
</head>
<body>
  <header class="header">
    <div>
      <div class="logo">ZebraStream</div>
      <div class="subtitle">IoT Monitoring Demo · Industry 4.0 / Smart Manufacturing</div>
    </div>
    <div class="links">
      <a href="/docs">API Docs</a>
      <a href="/api/v1/telemetry/">Telemetry</a>
      <a href="http://localhost:8080" target="_blank">Airflow</a>
    </div>
  </header>

  <main class="container">
    <section class="section">
      <h1 class="section-title">Live Dashboard</h1>
      <p style="color: var(--text-muted); margin-bottom: 1.5rem;">SPC analytics, AI maintenance insights, and real-time charts from simulated IoT sensor data.</p>

      <div class="grid">
        <div class="card">
          <h2>SPC Statistics</h2>
          <div id="spc-stats">
            <div class="loading">Loading...</div>
          </div>
        </div>
        <div class="card">
          <h2>AI Maintenance Summary</h2>
          <div id="maintenance-summary">
            <div class="loading">Loading...</div>
          </div>
        </div>
      </div>
    </section>

    <section class="section">
      <h2 class="section-title">Charts</h2>
      <div class="grid">
        <div class="card">
          <h3>X-bar Control Chart</h3>
          <div id="chart-xbar" class="chart-container">
            <div class="loading">Loading...</div>
          </div>
        </div>
        <div class="card">
          <h3>CUSUM Chart</h3>
          <div id="chart-cusum" class="chart-container">
            <div class="loading">Loading...</div>
          </div>
        </div>
        <div class="card">
          <h3>Pareto (by Sensor Type)</h3>
          <div id="chart-pareto" class="chart-container">
            <div class="loading">Loading...</div>
          </div>
        </div>
        <div class="card">
          <h3>Heatmap</h3>
          <div id="chart-heatmap" class="chart-container">
            <div class="loading">Loading...</div>
          </div>
        </div>
      </div>
    </section>
  </main>

  <script>
    const API = '/api/v1/analytics';

    async function loadSPCStats() {
      try {
        const r = await fetch(API + '/spc/stats?limit=200');
        const d = await r.json();
        const el = document.getElementById('spc-stats');
        el.innerHTML = `
          <div class="stat-row"><span class="stat-label">Readings</span><span class="stat-value">${d.count}</span></div>
          <div class="stat-row"><span class="stat-label">Mean</span><span class="stat-value">${d.mean?.toFixed(3) ?? '-'}</span></div>
          <div class="stat-row"><span class="stat-label">Std Dev</span><span class="stat-value">${d.std?.toFixed(3) ?? '-'}</span></div>
          <div class="stat-row"><span class="stat-label">UCL</span><span class="stat-value">${d.control_limits?.ucl?.toFixed(3) ?? '-'}</span></div>
          <div class="stat-row"><span class="stat-label">LCL</span><span class="stat-value">${d.control_limits?.lcl?.toFixed(3) ?? '-'}</span></div>
          <div class="stat-row"><span class="stat-label">Anomalies</span><span class="stat-value">${d.anomaly_indices?.length ?? 0}</span></div>
        `;
      } catch (e) {
        document.getElementById('spc-stats').innerHTML = '<div class="error">Failed to load. Ensure data exists.</div>';
      }
    }

    async function loadMaintenanceSummary() {
      try {
        const r = await fetch(API + '/maintenance-summary?limit=100');
        const d = await r.json();
        const el = document.getElementById('maintenance-summary');
        const recs = (d.recommendations || []).map(r => '<li>' + r + '</li>').join('');
        el.innerHTML = `
          <div class="summary-box">${d.summary || 'No summary available.'}</div>
          ${recs ? '<ul class="rec-list">' + recs + '</ul>' : ''}
        `;
      } catch (e) {
        document.getElementById('maintenance-summary').innerHTML = '<div class="error">Failed to load.</div>';
      }
    }

    async function loadChart(endpoint, containerId) {
      try {
        const r = await fetch(API + endpoint);
        const json = await r.json();
        const el = document.getElementById(containerId);
        el.innerHTML = '';
        if (json.data && json.data.length > 0) {
          Plotly.newPlot(containerId, json.data, json.layout || {}, { responsive: true });
        } else {
          el.innerHTML = '<div class="loading">No data for chart.</div>';
        }
      } catch (e) {
        document.getElementById(containerId).innerHTML = '<div class="error">Failed to load chart.</div>';
      }
    }

    async function init() {
      await loadSPCStats();
      await loadMaintenanceSummary();
      await loadChart('/charts/spc-xbar?limit=100', 'chart-xbar');
      await loadChart('/charts/spc-cusum?limit=100', 'chart-cusum');
      await loadChart('/charts/pareto', 'chart-pareto');
      await loadChart('/charts/heatmap', 'chart-heatmap');
    }

    init();
    setInterval(loadSPCStats, 30000);
    setInterval(loadMaintenanceSummary, 60000);
  </script>
</body>
</html>
"""
