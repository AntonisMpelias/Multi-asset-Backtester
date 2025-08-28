# 1. Base image with Python
FROM python:3.13-slim

# 2. Set working directory and Python path
WORKDIR /app
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# 3. Copy requirements file first (for caching)
COPY requirements.txt .

# 4. Install dependencies
RUN python -m pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# 5. Copy the rest of your project
COPY . .

# 7. Command to run your main script
CMD ["python", "-m", "engine.runner"]
