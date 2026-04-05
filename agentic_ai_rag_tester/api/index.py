from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import os

app = FastAPI()

@app.get("/")
def read_root():
    return HTMLResponse(content="""
    <html>
        <head>
            <title>RAG Tester Vercel App</title>
            <style>
                body { font-family: 'Inter', sans-serif; padding: 40px; background-color: #f0f4f8; }
                h1 { color: #1a202c; }
                p { color: #4a5568; }
                .card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); display: inline-block; }
            </style>
        </head>
        <body>
            <div class="card">
                <h1>RAG Tester Dashboard (Vercel)</h1>
                <p>Since Streamlit cannot be hosted directly on Vercel due to WebSockets constraints,<br>
                this is a FastAPI placeholder. To view your metrics in production from your Neon DB,<br>
                you can either host Streamlit on <b>Streamlit Cloud</b>, or expand this FastAPI endpoint.</p>
            </div>
        </body>
    </html>
    """)
