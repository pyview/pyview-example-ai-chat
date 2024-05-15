from fastapi.staticfiles import StaticFiles
from pyview import PyView, defaultRootTemplate
from .views import ChatView
from markupsafe import Markup

app = PyView()
css = """
<link href="https://cdn.jsdelivr.net/npm/daisyui@4.11.1/dist/full.min.css" rel="stylesheet" type="text/css" />
<script src="https://cdn.tailwindcss.com"></script>     
"""


app.rootTemplate = defaultRootTemplate(css=Markup(css))
app.mount("/static", StaticFiles(packages=[("pyview", "static")]), name="static")

app.add_live_view("/", ChatView)
