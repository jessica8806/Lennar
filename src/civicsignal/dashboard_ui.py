from __future__ import annotations


def render_dashboard_html() -> str:
    return """<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>CivicSignal Dashboard</title>
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, sans-serif; margin: 0; background: #f6f7fb; color: #111827; }
    header { padding: 16px 20px; background: #111827; color: white; }
    main { padding: 20px; display: grid; gap: 16px; }
    .card { background: white; border: 1px solid #e5e7eb; border-radius: 10px; padding: 14px; }
    .grid { display: grid; gap: 12px; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); }
    .filters { display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 10px; }
    .filters input, .filters select { width: 100%; padding: 8px; border: 1px solid #d1d5db; border-radius: 6px; }
    .kpi { font-size: 24px; font-weight: 600; }
    .list { margin: 0; padding-left: 18px; }
    table { width: 100%; border-collapse: collapse; font-size: 14px; }
    th, td { border-bottom: 1px solid #e5e7eb; text-align: left; padding: 8px; vertical-align: top; }
    .badge { display: inline-block; padding: 2px 8px; border-radius: 999px; font-size: 12px; font-weight: 600; }
    .badge-title_only { background: #fde68a; color: #92400e; }
    .badge-item_description { background: #dbeafe; color: #1e3a8a; }
    .badge-agenda_packet { background: #dcfce7; color: #14532d; }
    .badge-staff_report { background: #ede9fe; color: #4c1d95; }
    .signal-card { border: 1px solid #e5e7eb; border-radius: 8px; padding: 10px; margin-bottom: 8px; }
    .muted { color: #6b7280; font-size: 12px; }
  </style>
</head>
<body>
  <header>
    <h1 style=\"margin:0;font-size:20px;\">CivicSignal Dashboard</h1>
  </header>
  <main>
    <section class=\"card\">
      <h2 style=\"margin-top:0;\">Filters</h2>
      <div class=\"filters\">
        <input id=\"f-keyword\" placeholder=\"Keyword\" />
        <input id=\"f-city\" placeholder=\"City\" />
        <input id=\"f-category\" placeholder=\"Category\" />
        <select id=\"f-confidence\"><option value=\"\">Any confidence</option><option>Low</option><option>Medium</option><option>High</option></select>
        <select id=\"f-sort\"><option value=\"date\">Sort: date</option><option value=\"confidence\">Sort: confidence</option></select>
        <select id=\"f-order\"><option value=\"desc\">Order: desc</option><option value=\"asc\">Order: asc</option></select>
      </div>
      <div style=\"margin-top:10px;\"><button id=\"apply\">Apply</button></div>
    </section>

    <section class=\"grid\">
      <div class=\"card\"><div class=\"muted\">New Signals (24h)</div><div id=\"kpi-24h\" class=\"kpi\">-</div></div>
      <div class=\"card\"><div class=\"muted\">Signals (7d)</div><div id=\"kpi-7d\" class=\"kpi\">-</div></div>
      <div class=\"card\"><div class=\"muted\">Trending Projects</div><div id=\"kpi-projects\" class=\"kpi\">-</div></div>
    </section>

    <section class=\"grid\">
      <div class=\"card\">
        <h3 style=\"margin-top:0;\">Signals by Category</h3>
        <ul id=\"by-category\" class=\"list\"></ul>
      </div>
      <div class=\"card\">
        <h3 style=\"margin-top:0;\">Signals by City</h3>
        <ul id=\"by-city\" class=\"list\"></ul>
      </div>
      <div class=\"card\">
        <h3 style=\"margin-top:0;\">Trending Projects</h3>
        <ul id=\"trending-projects\" class=\"list\"></ul>
      </div>
    </section>

    <section class=\"card\">
      <h2 style=\"margin-top:0;\">Signal Cards</h2>
      <div id=\"signal-cards\"></div>
    </section>

    <section class=\"card\">
      <h2 style=\"margin-top:0;\">Signals Table</h2>
      <table>
        <thead>
          <tr>
            <th>Date</th><th>City</th><th>Body</th><th>Signal Type</th><th>Project</th><th>Confidence</th><th>Documents</th>
          </tr>
        </thead>
        <tbody id=\"signals-table\"></tbody>
      </table>
    </section>
  </main>

  <script>
    function groupCount(items, keyFn) {
      const map = new Map();
      for (const item of items) {
        const key = keyFn(item);
        map.set(key, (map.get(key) || 0) + 1);
      }
      return [...map.entries()].sort((a, b) => b[1] - a[1]);
    }

    function renderList(el, entries) {
      el.innerHTML = entries.slice(0, 8).map(([name, count]) => `<li>${name}: ${count}</li>`).join('');
    }

    function toDate(value) {
      const parsed = Date.parse(value);
      return Number.isNaN(parsed) ? null : new Date(parsed);
    }

    function qualityClass(source) {
      return `badge badge-${source || 'title_only'}`;
    }

    async function loadDashboard() {
      const keyword = document.getElementById('f-keyword').value;
      const city = document.getElementById('f-city').value;
      const category = document.getElementById('f-category').value;
      const confidence = document.getElementById('f-confidence').value;
      const sortBy = document.getElementById('f-sort').value;
      const sortOrder = document.getElementById('f-order').value;

      const params = new URLSearchParams({ limit: '300', sort_by: sortBy, sort_order: sortOrder });
      if (keyword) params.set('keyword', keyword);
      if (city) params.set('city', city);
      if (category) params.set('category', category);
      if (confidence) params.set('confidence', confidence);

      const signalsResp = await fetch(`/signals?${params.toString()}`);
      const signalsPayload = await signalsResp.json();
      const signals = signalsPayload.items || [];

      const projectsResp = await fetch(`/projects?limit=20${city ? `&city=${encodeURIComponent(city)}` : ''}`);
      const projectsPayload = await projectsResp.json();
      const projects = projectsPayload.items || [];

      const now = new Date();
      const dayAgo = new Date(now.getTime() - 24 * 3600 * 1000);
      const weekAgo = new Date(now.getTime() - 7 * 24 * 3600 * 1000);

      const in24h = signals.filter(s => {
        const d = toDate(s.meeting_date);
        return d && d >= dayAgo;
      }).length;

      const in7d = signals.filter(s => {
        const d = toDate(s.meeting_date);
        return d && d >= weekAgo;
      }).length;

      document.getElementById('kpi-24h').textContent = String(in24h);
      document.getElementById('kpi-7d').textContent = String(in7d);
      document.getElementById('kpi-projects').textContent = String(projects.length);

      renderList(document.getElementById('by-category'), groupCount(signals, s => s.signal_category));
      renderList(document.getElementById('by-city'), groupCount(signals, s => s.city));
      renderList(document.getElementById('trending-projects'), projects.map(p => [p.project_name, p.signals_count]));

      const cardsEl = document.getElementById('signal-cards');
      cardsEl.innerHTML = signals.slice(0, 12).map(s => `
        <div class=\"signal-card\">
          <div><strong>${s.title}</strong></div>
          <div class=\"muted\">${s.city} · ${s.meeting_body} · ${s.meeting_date}</div>
          <div style=\"margin-top:4px;\">${s.summary || ''}</div>
          <div style=\"margin-top:6px;display:flex;gap:8px;align-items:center;\">
            <span>${s.signal_type}</span>
            <span>${s.confidence}</span>
            <span class=\"${qualityClass(s.summary_source)}\">${s.summary_source}</span>
          </div>
          <div class=\"muted\">Source: ${(s.source_urls && s.source_urls[0]) ? `<a href=\"${s.source_urls[0]}\" target=\"_blank\" rel=\"noreferrer\">link</a>` : 'n/a'}</div>
        </div>
      `).join('');

      const tableEl = document.getElementById('signals-table');
      tableEl.innerHTML = signals.slice(0, 100).map(s => `
        <tr>
          <td>${s.meeting_date}</td>
          <td>${s.city}</td>
          <td>${s.meeting_body}</td>
          <td>${s.signal_type}</td>
          <td>-</td>
          <td>${s.confidence}</td>
          <td>${(s.supporting_documents || []).length}</td>
        </tr>
      `).join('');
    }

    document.getElementById('apply').addEventListener('click', loadDashboard);
    loadDashboard();
  </script>
</body>
</html>
"""
