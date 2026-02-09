"""Generate a standalone HTML page with searchable catalog and curriculum."""

from __future__ import annotations

import json
from pathlib import Path

from ai_training_catalog.models.curriculum import Curriculum
from ai_training_catalog.models.resource import Resource


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AI Training Catalog</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f7fa; color: #1a1a2e; line-height: 1.6; }
  .header { background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%); color: white; padding: 2rem; text-align: center; }
  .header h1 { font-size: 2rem; margin-bottom: 0.5rem; }
  .header p { opacity: 0.85; font-size: 1.1rem; }
  .stats-bar { display: flex; justify-content: center; gap: 2rem; margin-top: 1.5rem; flex-wrap: wrap; }
  .stat { text-align: center; }
  .stat-num { font-size: 2rem; font-weight: 700; color: #e94560; }
  .stat-label { font-size: 0.85rem; opacity: 0.7; }
  .container { max-width: 1200px; margin: 0 auto; padding: 1.5rem; }
  .tabs { display: flex; gap: 0; margin-bottom: 1.5rem; border-bottom: 2px solid #e0e0e0; }
  .tab { padding: 0.75rem 1.5rem; cursor: pointer; background: none; border: none; font-size: 1rem; color: #666; border-bottom: 3px solid transparent; margin-bottom: -2px; }
  .tab.active { color: #0f3460; border-bottom-color: #e94560; font-weight: 600; }
  .tab:hover { color: #0f3460; }
  .search-bar { display: flex; gap: 0.75rem; margin-bottom: 1.5rem; flex-wrap: wrap; }
  .search-bar input { flex: 1; min-width: 200px; padding: 0.75rem 1rem; border: 2px solid #e0e0e0; border-radius: 8px; font-size: 1rem; }
  .search-bar input:focus { outline: none; border-color: #0f3460; }
  .search-bar select { padding: 0.75rem 1rem; border: 2px solid #e0e0e0; border-radius: 8px; font-size: 0.95rem; background: white; }
  .filters { display: flex; gap: 0.5rem; flex-wrap: wrap; margin-bottom: 1rem; }
  .filter-chip { padding: 0.4rem 0.8rem; border-radius: 20px; border: 1px solid #ccc; background: white; cursor: pointer; font-size: 0.85rem; }
  .filter-chip.active { background: #0f3460; color: white; border-color: #0f3460; }
  .filter-chip:hover { border-color: #0f3460; }
  .section { display: none; }
  .section.active { display: block; }
  .card { background: white; border-radius: 10px; padding: 1.25rem; margin-bottom: 1rem; box-shadow: 0 1px 3px rgba(0,0,0,0.08); border-left: 4px solid #0f3460; }
  .card:hover { box-shadow: 0 4px 12px rgba(0,0,0,0.12); }
  .card-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.5rem; }
  .card-title { font-size: 1.1rem; font-weight: 600; color: #1a1a2e; }
  .card-title a { color: #0f3460; text-decoration: none; }
  .card-title a:hover { text-decoration: underline; }
  .card-score { background: #e94560; color: white; padding: 0.2rem 0.6rem; border-radius: 12px; font-size: 0.8rem; font-weight: 600; white-space: nowrap; }
  .card-score.high { background: #2ecc71; }
  .card-score.medium { background: #f39c12; }
  .card-score.low { background: #e74c3c; }
  .card-desc { color: #555; font-size: 0.95rem; margin-bottom: 0.75rem; }
  .card-tags { display: flex; gap: 0.4rem; flex-wrap: wrap; }
  .tag { padding: 0.2rem 0.6rem; border-radius: 4px; font-size: 0.78rem; font-weight: 500; }
  .tag-domain { background: #e8f0fe; color: #1a73e8; }
  .tag-type { background: #fce8e6; color: #d93025; }
  .tag-difficulty { background: #e6f4ea; color: #137333; }
  .tag-provider { background: #fef7e0; color: #b06000; }
  .tag-hours { background: #f3e8fd; color: #7b1fa2; }
  .path-card { border-left-color: #e94560; }
  .path-card .path-difficulty { display: inline-block; padding: 0.2rem 0.6rem; border-radius: 4px; font-size: 0.8rem; font-weight: 600; margin-right: 0.5rem; }
  .path-difficulty.beginner { background: #e6f4ea; color: #137333; }
  .path-difficulty.intermediate { background: #fef7e0; color: #b06000; }
  .path-difficulty.advanced { background: #fce8e6; color: #d93025; }
  .module-list { margin-top: 0.75rem; padding-left: 1.5rem; }
  .module-item { margin-bottom: 0.5rem; color: #444; font-size: 0.95rem; }
  .module-resources { font-size: 0.85rem; color: #888; margin-left: 0.5rem; }
  .count-badge { background: #eee; padding: 0.2rem 0.5rem; border-radius: 10px; font-size: 0.85rem; color: #666; margin-left: 0.5rem; }
  .empty-state { text-align: center; padding: 3rem; color: #888; }
  .resource-link { display: block; margin-top: 0.4rem; }
  .resource-link a { color: #1a73e8; text-decoration: none; font-size: 0.85rem; word-break: break-all; }
  .resource-link a:hover { text-decoration: underline; }
  @media (max-width: 768px) {
    .stats-bar { gap: 1rem; }
    .stat-num { font-size: 1.5rem; }
    .card-header { flex-direction: column; gap: 0.5rem; }
  }
</style>
</head>
<body>

<div class="header">
  <h1>AI Training Catalog</h1>
  <p>Free &amp; Open Source AI Training Resources — Auto-Curated</p>
  <div class="stats-bar">
    <div class="stat"><div class="stat-num" id="total-resources">0</div><div class="stat-label">Resources</div></div>
    <div class="stat"><div class="stat-num" id="total-paths">0</div><div class="stat-label">Learning Paths</div></div>
    <div class="stat"><div class="stat-num" id="total-hours">0</div><div class="stat-label">Hours of Content</div></div>
    <div class="stat"><div class="stat-num" id="total-domains">0</div><div class="stat-label">Skill Domains</div></div>
  </div>
</div>

<div class="container">
  <div class="tabs">
    <button class="tab active" onclick="switchTab('catalog')">Resource Catalog</button>
    <button class="tab" onclick="switchTab('curriculum')">Learning Paths</button>
  </div>

  <!-- CATALOG TAB -->
  <div id="catalog-section" class="section active">
    <div class="search-bar">
      <input type="text" id="search-input" placeholder="Search resources by title, description, tags..." oninput="filterResources()">
      <select id="domain-filter" onchange="filterResources()">
        <option value="">All Domains</option>
      </select>
      <select id="type-filter" onchange="filterResources()">
        <option value="">All Types</option>
      </select>
      <select id="difficulty-filter" onchange="filterResources()">
        <option value="">All Levels</option>
        <option value="beginner">Beginner</option>
        <option value="intermediate">Intermediate</option>
        <option value="advanced">Advanced</option>
      </select>
    </div>
    <div id="resource-count" style="margin-bottom:1rem; color:#666; font-size:0.9rem;"></div>
    <div id="resource-list"></div>
  </div>

  <!-- CURRICULUM TAB -->
  <div id="curriculum-section" class="section">
    <div class="search-bar">
      <input type="text" id="path-search" placeholder="Search learning paths..." oninput="filterPaths()">
      <select id="path-domain-filter" onchange="filterPaths()">
        <option value="">All Domains</option>
      </select>
      <select id="path-difficulty-filter" onchange="filterPaths()">
        <option value="">All Levels</option>
        <option value="beginner">Beginner</option>
        <option value="intermediate">Intermediate</option>
        <option value="advanced">Advanced</option>
      </select>
    </div>
    <div id="path-list"></div>
  </div>
</div>

<script>
const RESOURCES = __RESOURCES_JSON__;
const CURRICULUM = __CURRICULUM_JSON__;

// Populate stats
document.getElementById('total-resources').textContent = RESOURCES.length;
document.getElementById('total-paths').textContent = CURRICULUM.learning_paths ? CURRICULUM.learning_paths.length : 0;
const totalHours = CURRICULUM.learning_paths ? CURRICULUM.learning_paths.reduce((sum, p) => sum + (p.total_estimated_hours || 0), 0) : 0;
document.getElementById('total-hours').textContent = totalHours.toFixed(0);
const allDomains = [...new Set(RESOURCES.flatMap(r => r.domains || []))].sort();
document.getElementById('total-domains').textContent = allDomains.length;

// Populate domain filters
const domainSelect = document.getElementById('domain-filter');
const pathDomainSelect = document.getElementById('path-domain-filter');
allDomains.forEach(d => {
  const label = d.replace(/_/g, ' ').replace(/\\b\\w/g, c => c.toUpperCase());
  domainSelect.add(new Option(label, d));
  pathDomainSelect.add(new Option(label, d));
});

// Populate type filter
const allTypes = [...new Set(RESOURCES.map(r => r.content_type))].sort();
const typeSelect = document.getElementById('type-filter');
allTypes.forEach(t => {
  const label = t.replace(/_/g, ' ').replace(/\\b\\w/g, c => c.toUpperCase());
  typeSelect.add(new Option(label, t));
});

// Resource ID to resource map
const resourceMap = {};
RESOURCES.forEach(r => resourceMap[r.id] = r);

function scoreClass(score) {
  if (score >= 0.7) return 'high';
  if (score >= 0.5) return 'medium';
  return 'low';
}

function renderResource(r) {
  const domains = (r.domains || []).map(d => '<span class="tag tag-domain">' + d.replace(/_/g, ' ') + '</span>').join('');
  const typeLabel = (r.content_type || '').replace(/_/g, ' ');
  const hours = r.estimated_hours ? '<span class="tag tag-hours">' + r.estimated_hours + 'h</span>' : '';
  return '<div class="card">' +
    '<div class="card-header">' +
      '<div class="card-title"><a href="' + r.url + '" target="_blank" rel="noopener">' + escHtml(r.title) + '</a></div>' +
      '<span class="card-score ' + scoreClass(r.quality_score) + '">' + (r.quality_score || 0).toFixed(2) + '</span>' +
    '</div>' +
    (r.description ? '<div class="card-desc">' + escHtml(r.description).substring(0, 300) + '</div>' : '') +
    '<div class="resource-link"><a href="' + r.url + '" target="_blank" rel="noopener">' + escHtml(r.url) + '</a></div>' +
    '<div class="card-tags" style="margin-top:0.5rem">' +
      domains +
      '<span class="tag tag-type">' + typeLabel + '</span>' +
      '<span class="tag tag-difficulty">' + (r.difficulty || 'beginner') + '</span>' +
      (r.provider ? '<span class="tag tag-provider">' + r.provider + '</span>' : '') +
      hours +
    '</div>' +
  '</div>';
}

function renderPath(path) {
  const diffClass = (path.difficulty || 'beginner');
  let modulesHtml = '';
  if (path.modules) {
    modulesHtml = '<ol class="module-list">';
    path.modules.forEach(mod => {
      const resourceLinks = (mod.resource_ids || []).map(rid => {
        const res = resourceMap[rid];
        if (res) return '<a href="' + res.url + '" target="_blank" rel="noopener">' + escHtml(res.title) + '</a>';
        return rid;
      }).join('<br>');
      modulesHtml += '<li class="module-item"><strong>' + escHtml(mod.title) + '</strong> (' + (mod.estimated_hours || 0).toFixed(1) + 'h)' +
        '<div style="margin-top:0.3rem;font-size:0.85rem;color:#555">' + resourceLinks + '</div></li>';
    });
    modulesHtml += '</ol>';
  }
  const prereqs = (path.prerequisites || []).length > 0
    ? '<div style="margin-top:0.5rem;font-size:0.85rem;color:#888">Prerequisites: ' + path.prerequisites.join(', ') + '</div>'
    : '';
  return '<div class="card path-card">' +
    '<div class="card-header">' +
      '<div class="card-title">' + escHtml(path.title) + '</div>' +
      '<span class="tag tag-hours">' + (path.total_estimated_hours || 0).toFixed(1) + 'h</span>' +
    '</div>' +
    '<div><span class="path-difficulty ' + diffClass + '">' + diffClass.toUpperCase() + '</span>' +
      '<span style="color:#666;font-size:0.9rem">' + (path.modules || []).length + ' modules &middot; ' + escHtml(path.target_audience || '') + '</span>' +
    '</div>' +
    (path.description ? '<div class="card-desc" style="margin-top:0.5rem">' + escHtml(path.description) + '</div>' : '') +
    prereqs +
    modulesHtml +
  '</div>';
}

function escHtml(s) {
  if (!s) return '';
  return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

function filterResources() {
  const query = document.getElementById('search-input').value.toLowerCase();
  const domain = document.getElementById('domain-filter').value;
  const type = document.getElementById('type-filter').value;
  const diff = document.getElementById('difficulty-filter').value;
  const filtered = RESOURCES.filter(r => {
    if (query && !(r.title + ' ' + r.description + ' ' + (r.tags || []).join(' ')).toLowerCase().includes(query)) return false;
    if (domain && !(r.domains || []).includes(domain)) return false;
    if (type && r.content_type !== type) return false;
    if (diff && r.difficulty !== diff) return false;
    return true;
  });
  filtered.sort((a, b) => (b.quality_score || 0) - (a.quality_score || 0));
  document.getElementById('resource-count').textContent = 'Showing ' + filtered.length + ' of ' + RESOURCES.length + ' resources';
  document.getElementById('resource-list').innerHTML = filtered.length
    ? filtered.map(renderResource).join('')
    : '<div class="empty-state">No resources match your filters.</div>';
}

function filterPaths() {
  const query = document.getElementById('path-search').value.toLowerCase();
  const domain = document.getElementById('path-domain-filter').value;
  const diff = document.getElementById('path-difficulty-filter').value;
  const paths = CURRICULUM.learning_paths || [];
  const filtered = paths.filter(p => {
    if (query && !(p.title + ' ' + p.description).toLowerCase().includes(query)) return false;
    if (domain && !(p.domains || []).includes(domain)) return false;
    if (diff && p.difficulty !== diff) return false;
    return true;
  });
  document.getElementById('path-list').innerHTML = filtered.length
    ? filtered.map(renderPath).join('')
    : '<div class="empty-state">No learning paths match your filters.</div>';
}

function switchTab(tab) {
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
  if (tab === 'catalog') {
    document.querySelectorAll('.tab')[0].classList.add('active');
    document.getElementById('catalog-section').classList.add('active');
  } else {
    document.querySelectorAll('.tab')[1].classList.add('active');
    document.getElementById('curriculum-section').classList.add('active');
  }
}

// Initial render
filterResources();
filterPaths();
</script>
</body>
</html>"""


def generate_html(
    resources: list[Resource],
    curriculum: Curriculum | None,
    output_path: Path,
) -> Path:
    """Generate a standalone searchable HTML catalog."""
    resources_json = json.dumps(
        [r.model_dump(mode="json") for r in resources],
        default=str,
    )
    curriculum_json = json.dumps(
        curriculum.model_dump(mode="json") if curriculum else {"learning_paths": []},
        default=str,
    )

    html = HTML_TEMPLATE.replace("__RESOURCES_JSON__", resources_json)
    html = html.replace("__CURRICULUM_JSON__", curriculum_json)

    output_path.write_text(html, encoding="utf-8")
    return output_path
