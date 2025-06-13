# Use Python 3.9 slim image as base
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install Chrome and its dependencies
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list \
    && apt-get update \
    && apt-get install -y \
    google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create directory for Chrome user data
RUN mkdir -p /chrome-data

# Set environment variables
ENV PYTHONPATH=/app/src
ENV CHROME_DEBUG_PORT=9222
ENV CHROME_USER_DATA_DIR=/chrome-data

# Create entrypoint script
RUN echo '#!/bin/bash\n\
google-chrome --remote-debugging-port=$CHROME_DEBUG_PORT \
--user-data-dir=$CHROME_USER_DATA_DIR \
--no-sandbox \
--headless \
--disable-gpu \
--disable-dev-shm-usage &\n\
sleep 5\n\
if [ "$1" = "analyze" ]; then\n\
  python src/analyze_profiles.py\n\
else\n\
  python src/main.py\n\
fi' > /app/entrypoint.sh \
&& chmod +x /app/entrypoint.sh

# Set the entrypoint
ENTRYPOINT ["/app/entrypoint.sh"] 