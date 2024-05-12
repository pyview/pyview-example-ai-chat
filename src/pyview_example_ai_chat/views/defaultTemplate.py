from pyview import RootTemplateContext


def defaultRootTemplate(context: RootTemplateContext) -> str:
    suffix = " | PyView Chat"
    render_title = (
        (context["title"] + suffix)  # type: ignore
        if context.get("title", None) is not None
        else "PyView Chat"
    )
    return f"""
<!DOCTYPE html>
<html lang="en">
    <head>
      <title data-suffix="{suffix}">{render_title}</title>
      <meta name="csrf-token" content="{context['csrf_token']}" />
      <meta charset="utf-8">
      <meta http-equiv="X-UA-Compatible" content="IE=edge">
      <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
      <script defer type="text/javascript" src="/static/assets/app.js"></script>
      <link href="https://cdn.jsdelivr.net/npm/daisyui@4.11.1/dist/full.min.css" rel="stylesheet" type="text/css" />
      <script src="https://cdn.tailwindcss.com"></script>      
    </head>
    <body>
      <div
        data-phx-main="true"
        data-phx-session="{context['session']}"
        data-phx-static=""
        id="phx-{context['id']}"
        >
        {context['content']}
    </div>
    </body>
</html>
"""
