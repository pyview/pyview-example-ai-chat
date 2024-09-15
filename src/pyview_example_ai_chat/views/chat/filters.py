import markdown as md
from markupsafe import Markup
from pyview.vendor.ibis import filters


@filters.register
def markdown(text):
    return Markup(
        md.markdown(
            text,
            extensions=["fenced_code", "codehilite"],
            extension_configs={"codehilite": {"css_class": "highlight"}},
        )
    )
