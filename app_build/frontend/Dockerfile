FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

# --server.address=0.0.0.0 - żeby Docker mógł wyeksponować port
CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=8501"]
