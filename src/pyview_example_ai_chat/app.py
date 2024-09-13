from starlette.staticfiles import StaticFiles
from pyview import PyView, defaultRootTemplate
from pyview_example_ai_chat.views import ChatView
from markupsafe import Markup

app = PyView()
css = """
<link href="https://cdn.jsdelivr.net/npm/daisyui@4.11.1/dist/full.min.css" rel="stylesheet" type="text/css" />
<script src="https://cdn.tailwindcss.com"></script>

<link href="/static/code_highlight.css" rel="stylesheet" type="text/css" />
<link href="/static/chat.css" rel="stylesheet" type="text/css" />
<script src="/static/clipboard.js" defer></script>
"""

app.rootTemplate = defaultRootTemplate(css=Markup(css))
app.mount(
    "/static",
    StaticFiles(
        packages=[("pyview", "static"), ("pyview_example_ai_chat.views.chat", "static")]
    ),
    name="static",
)

app.add_live_view("/", ChatView)
