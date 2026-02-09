"""Rural Contextualization Engine.

Takes a learning path from the curriculum and generates a new,
rural-contextualized version with adapted examples, exercises,
datasets, and community project ideas.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

from ai_training_catalog.models.curriculum import Curriculum, LearningPath, ModuleUnit
from ai_training_catalog.models.resource import Resource

from .rural_context import (
    EXAMPLE_REPLACEMENTS,
    RURAL_CONTEXTS,
    RuralDomainContext,
    RuralUseCase,
)


def _apply_replacements(text: str, replacements: dict[str, str]) -> str:
    """Replace urban examples with rural equivalents (case-insensitive)."""
    result = text
    for urban, rural in replacements.items():
        pattern = re.compile(re.escape(urban), re.IGNORECASE)
        result = pattern.sub(rural, result)
    return result


def _format_use_case(uc: RuralUseCase) -> dict:
    return {
        "concept": uc.concept,
        "original_example": uc.urban_example,
        "rural_example": uc.rural_example,
        "suggested_dataset": uc.dataset_suggestion,
        "exercise": uc.exercise_prompt,
    }


def _build_module_supplement(
    module: ModuleUnit,
    resources: dict[str, Resource],
    context: RuralDomainContext,
) -> dict:
    """Build a rural supplement for a single module."""
    # Gather resource info
    module_resources = []
    for rid in module.resource_ids:
        r = resources.get(rid)
        if r:
            rural_desc = _apply_replacements(r.description, EXAMPLE_REPLACEMENTS)
            module_resources.append({
                "title": r.title,
                "url": r.url,
                "original_description": r.description,
                "rural_context_note": rural_desc if rural_desc != r.description else (
                    "Apply the concepts from this resource to the rural use cases below."
                ),
            })

    # Match use cases to module objectives
    matched_use_cases = []
    module_text = (module.title + " " + module.description + " " +
                   " ".join(o.description for o in module.objectives)).lower()
    for uc in context.use_cases:
        if any(kw in module_text for kw in uc.concept.lower().split()):
            matched_use_cases.append(_format_use_case(uc))

    # If no specific matches, include all use cases for the domain
    if not matched_use_cases and context.use_cases:
        matched_use_cases = [_format_use_case(uc) for uc in context.use_cases[:2]]

    return {
        "module_title": module.title,
        "estimated_hours": module.estimated_hours,
        "resources_with_rural_notes": module_resources,
        "rural_use_cases": matched_use_cases,
        "rural_objectives": [
            f"Apply {uc['concept']} to a rural context: {uc['rural_example']}"
            for uc in matched_use_cases
        ],
    }


def contextualize_path(
    path: LearningPath,
    resources: dict[str, Resource],
    context: RuralDomainContext | None = None,
) -> dict:
    """Generate a complete rural-contextualized version of a learning path.

    Returns a dictionary suitable for JSON serialization and HTML rendering.
    """
    # Auto-detect context from path domains
    if context is None:
        for domain in path.domains:
            if domain.value in RURAL_CONTEXTS:
                context = RURAL_CONTEXTS[domain.value]
                break

    if context is None:
        # Fallback: use ML basics context as default
        context = RURAL_CONTEXTS.get("ml_basics", RuralDomainContext(
            domain="general",
            overview="AI concepts applied to rural community challenges.",
            why_it_matters="Rural communities can benefit from AI-driven solutions.",
        ))

    # Build module supplements
    module_supplements = [
        _build_module_supplement(mod, resources, context)
        for mod in path.modules
    ]

    return {
        "title": f"{path.title} — Rural Edition",
        "original_path_id": path.id,
        "difficulty": path.difficulty.value,
        "target_audience": (
            f"Rural practitioners, agricultural extension workers, community "
            f"development professionals, and anyone interested in applying "
            f"{path.domains[0].value.replace('_', ' ')} to rural challenges. "
            f"Original audience: {path.target_audience}"
        ),
        "rural_context": {
            "overview": context.overview,
            "why_it_matters": context.why_it_matters,
        },
        "total_estimated_hours": path.total_estimated_hours + 2.0,  # extra time for rural exercises
        "prerequisites": path.prerequisites + [
            "Basic familiarity with rural/agricultural concepts (no AI experience needed)"
        ],
        "modules": module_supplements,
        "rural_datasets": context.local_datasets,
        "community_projects": context.community_projects,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


def generate_rural_html(contextualized: dict, output_path: Path) -> Path:
    """Generate a standalone HTML page for the rural-contextualized course."""
    title = contextualized["title"]
    ctx = contextualized["rural_context"]
    modules = contextualized["modules"]
    datasets = contextualized.get("rural_datasets", [])
    projects = contextualized.get("community_projects", [])

    modules_html = ""
    for i, mod in enumerate(modules, 1):
        # Resources section
        resources_html = ""
        for res in mod.get("resources_with_rural_notes", []):
            resources_html += f"""
            <div class="resource-item">
              <a href="{res['url']}" target="_blank">{_esc(res['title'])}</a>
              <p class="rural-note">{_esc(res['rural_context_note'])}</p>
            </div>"""

        # Use cases section
        use_cases_html = ""
        for uc in mod.get("rural_use_cases", []):
            use_cases_html += f"""
            <div class="use-case">
              <h4>{_esc(uc['concept'])}</h4>
              <div class="comparison">
                <div class="urban"><strong>Typical example:</strong> {_esc(uc['original_example'])}</div>
                <div class="arrow">&#10132;</div>
                <div class="rural"><strong>Rural example:</strong> {_esc(uc['rural_example'])}</div>
              </div>
              <div class="dataset"><strong>Dataset:</strong> {_esc(uc['suggested_dataset'])}</div>
              <div class="exercise"><strong>Exercise:</strong> {_esc(uc['exercise'])}</div>
            </div>"""

        modules_html += f"""
        <div class="module">
          <h3>Module {i}: {_esc(mod['module_title'])} <span class="hours">{mod['estimated_hours']:.1f}h</span></h3>
          <div class="resources-section">
            <h4>Learning Resources</h4>
            {resources_html if resources_html else '<p class="empty">Resources from the original curriculum apply here.</p>'}
          </div>
          <div class="use-cases-section">
            <h4>Rural Use Cases &amp; Exercises</h4>
            {use_cases_html if use_cases_html else '<p class="empty">Apply the general concepts to your local rural context.</p>'}
          </div>
        </div>"""

    datasets_html = "".join(f"<li>{_esc(d)}</li>" for d in datasets)
    projects_html = "".join(f"<li>{_esc(p)}</li>" for p in projects)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{_esc(title)}</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f7f0; color: #2d3436; line-height: 1.7; }}
  .header {{ background: linear-gradient(135deg, #2d5016 0%, #4a7c2e 50%, #6ba33e 100%); color: white; padding: 2.5rem 2rem; text-align: center; }}
  .header h1 {{ font-size: 2rem; margin-bottom: 0.5rem; }}
  .header p {{ opacity: 0.9; font-size: 1.1rem; max-width: 700px; margin: 0 auto; }}
  .meta {{ display: flex; justify-content: center; gap: 2rem; margin-top: 1.5rem; flex-wrap: wrap; }}
  .meta-item {{ text-align: center; }}
  .meta-num {{ font-size: 1.8rem; font-weight: 700; color: #ffd93d; }}
  .meta-label {{ font-size: 0.85rem; opacity: 0.8; }}
  .container {{ max-width: 900px; margin: 0 auto; padding: 2rem 1.5rem; }}
  .context-box {{ background: white; border-radius: 12px; padding: 1.5rem; margin-bottom: 2rem; border-left: 5px solid #4a7c2e; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }}
  .context-box h2 {{ color: #2d5016; margin-bottom: 0.75rem; font-size: 1.3rem; }}
  .context-box p {{ color: #555; }}
  .module {{ background: white; border-radius: 12px; padding: 1.5rem; margin-bottom: 1.5rem; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }}
  .module h3 {{ color: #2d5016; border-bottom: 2px solid #e8f5e9; padding-bottom: 0.5rem; margin-bottom: 1rem; }}
  .module h4 {{ color: #4a7c2e; margin: 1rem 0 0.5rem; font-size: 1rem; }}
  .hours {{ float: right; background: #e8f5e9; color: #2d5016; padding: 0.2rem 0.8rem; border-radius: 15px; font-size: 0.85rem; }}
  .resource-item {{ padding: 0.75rem; margin-bottom: 0.5rem; background: #f8faf5; border-radius: 8px; }}
  .resource-item a {{ color: #2d5016; font-weight: 600; text-decoration: none; }}
  .resource-item a:hover {{ text-decoration: underline; }}
  .rural-note {{ font-size: 0.9rem; color: #666; margin-top: 0.3rem; font-style: italic; }}
  .use-case {{ padding: 1rem; margin-bottom: 1rem; background: #f0f7e8; border-radius: 8px; border-left: 3px solid #6ba33e; }}
  .use-case h4 {{ color: #2d5016; margin-bottom: 0.5rem; }}
  .comparison {{ display: flex; align-items: center; gap: 0.75rem; margin: 0.75rem 0; flex-wrap: wrap; }}
  .urban {{ flex: 1; min-width: 200px; padding: 0.5rem; background: #fff3e0; border-radius: 6px; font-size: 0.9rem; }}
  .arrow {{ font-size: 1.5rem; color: #4a7c2e; }}
  .rural {{ flex: 1; min-width: 200px; padding: 0.5rem; background: #e8f5e9; border-radius: 6px; font-size: 0.9rem; }}
  .dataset {{ margin-top: 0.5rem; font-size: 0.9rem; color: #555; }}
  .exercise {{ margin-top: 0.75rem; padding: 0.75rem; background: white; border-radius: 6px; font-size: 0.9rem; border: 1px dashed #4a7c2e; }}
  .section-title {{ color: #2d5016; font-size: 1.4rem; margin: 2rem 0 1rem; padding-bottom: 0.5rem; border-bottom: 2px solid #4a7c2e; }}
  .dataset-list, .project-list {{ list-style: none; }}
  .dataset-list li, .project-list li {{ padding: 0.6rem 0.75rem; margin-bottom: 0.5rem; background: white; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }}
  .dataset-list li::before {{ content: "\\1F4CA "; }}
  .project-list li::before {{ content: "\\1F6E0 "; }}
  .empty {{ color: #999; font-style: italic; }}
  .prereqs {{ background: #fff8e1; padding: 1rem; border-radius: 8px; margin-bottom: 2rem; }}
  .prereqs h3 {{ color: #f57f17; margin-bottom: 0.5rem; }}
  .prereqs li {{ margin-left: 1.5rem; color: #555; }}
  @media (max-width: 768px) {{
    .comparison {{ flex-direction: column; }}
    .arrow {{ transform: rotate(90deg); }}
  }}
</style>
</head>
<body>

<div class="header">
  <h1>{_esc(title)}</h1>
  <p>{_esc(ctx['overview'])}</p>
  <div class="meta">
    <div class="meta-item"><div class="meta-num">{len(modules)}</div><div class="meta-label">Modules</div></div>
    <div class="meta-item"><div class="meta-num">{contextualized['total_estimated_hours']:.0f}h</div><div class="meta-label">Estimated Hours</div></div>
    <div class="meta-item"><div class="meta-num">{contextualized['difficulty'].title()}</div><div class="meta-label">Difficulty</div></div>
  </div>
</div>

<div class="container">
  <div class="context-box">
    <h2>Why This Matters for Rural Communities</h2>
    <p>{_esc(ctx['why_it_matters'])}</p>
  </div>

  <div class="prereqs">
    <h3>Prerequisites</h3>
    <ul>
      {"".join(f"<li>{_esc(p)}</li>" for p in contextualized.get('prerequisites', []))}
    </ul>
  </div>

  <h2 class="section-title">Course Modules</h2>
  {modules_html}

  {"<h2 class='section-title'>Rural Datasets</h2><ul class='dataset-list'>" + datasets_html + "</ul>" if datasets_html else ""}

  {"<h2 class='section-title'>Community Project Ideas</h2><ul class='project-list'>" + projects_html + "</ul>" if projects_html else ""}
</div>

</body>
</html>"""

    output_path.write_text(html, encoding="utf-8")
    return output_path


def _esc(s: str) -> str:
    if not s:
        return ""
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
