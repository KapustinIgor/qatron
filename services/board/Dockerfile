FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files
COPY package.json package-lock.json* ./

# Install dependencies
# Use npm ci if package-lock.json exists, otherwise fall back to npm install
RUN if [ -f package-lock.json ]; then npm ci; else npm install; fi

# Copy source code
COPY . .

# Use /api/v1 when served behind nginx proxy (same origin); override with build-arg if needed
ARG VITE_API_URL=/api/v1
ENV VITE_API_URL=$VITE_API_URL

# Build application
RUN npm run build

# Production stage
FROM nginx:alpine

# Install curl for healthcheck
RUN apk add --no-cache curl

# Copy built assets
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost/healthz || exit 1

CMD ["nginx", "-g", "daemon off;"]
