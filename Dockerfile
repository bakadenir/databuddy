FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies (tanpa supabase dulu)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install supabase terpisah (workaround konflik zhipuai vs supabase-auth soal pyjwt)
RUN pip install --no-cache-dir supabase>=2.31.0

# Copy application code
COPY . .

# Expose Streamlit port
EXPOSE 8501

# Run the application
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
