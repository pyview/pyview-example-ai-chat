from fastapi.staticfiles import StaticFiles
from pyview import PyView
from .views import ChatView, defaultRootTemplate

app = PyView()
app.rootTemplate = defaultRootTemplate
app.mount("/static", StaticFiles(packages=[("pyview", "static")]), name="static")

app.add_live_view("/", ChatView)
