set dotenv-load

start:
  PYVIEW_SECRET=`openssl rand -base64 16` cd src && poetry run uvicorn pyview_example_ai_chat.app:app --reload --port 7000
