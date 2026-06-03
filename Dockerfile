# Stage 1: Build the React frontend
FROM node:20-alpine AS frontend-builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# Stage 2: Build the FastAPI backend and serve unified
FROM python:3.11-slim
WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8080

# asyncpg 빌드에 필요한 C 컴파일러 설치 후 삭제하여 이미지 크기 최소화
RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install backend dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && apt-get purge -y --auto-remove gcc libpq-dev \
    || true

# Copy backend code
COPY backend/ .

# Copy built frontend assets from stage 1 to backend's dist folder
COPY --from=frontend-builder /app/dist ./dist

# Run the application
CMD uvicorn main:app --host 0.0.0.0 --port $PORT
