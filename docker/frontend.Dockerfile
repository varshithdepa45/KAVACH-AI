# KAVACH AI — frontend image. Build context is the repo root.
# Fonts are fetched at BUILD time and self-hosted into the bundle, so the
# RUNNING container makes no external font requests (air-gapped runtime).
FROM node:20-slim AS build

WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install --no-audit --no-fund

COPY frontend/ ./
RUN npm run build

FROM node:20-slim AS run
WORKDIR /app/frontend
ENV NODE_ENV=production \
    NEXT_PUBLIC_API_BASE=http://localhost:8000
COPY --from=build /app/frontend ./
EXPOSE 3000
CMD ["npm", "run", "start"]
