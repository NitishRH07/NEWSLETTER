"""Jinja2 HTML renderer for newsletter pages."""

from jinja2 import Environment, FileSystemLoader, select_autoescape


class HTMLRenderer:
    """Renders the full multi-page newsletter HTML from Jinja2 templates."""

    def __init__(self, templates_dir: str = "templates"):
        self.env = Environment(
            loader=FileSystemLoader(templates_dir),
            autoescape=select_autoescape(["html"]),
        )

    def render_newsletter(
        self,
        tools: list,
        issue_info: dict,
        template_name: str = "classic",
    ) -> str:
        """
        Render all tool pages into a single HTML document.

        Args:
            tools: list of tool content dicts (each becomes one A4 page)
            issue_info: dict with keys: issue_number, week_label, pub_date, title
            template_name: "classic" (standard reference) or "modern" (infographic layout)

        Returns:
            Complete HTML string ready for PDF conversion.
        """
        filename = "newsletter_modern.html" if template_name == "modern" else "newsletter_page.html"
        template = self.env.get_template(filename)
        render_ctx = {
            "tools": tools,
            "issue": issue_info,
            **issue_info,
        }
        render_ctx.setdefault("pages_per_tool", 1)
        return template.render(**render_ctx)
