FROM node:22-alpine AS base

WORKDIR /app
COPY package*.json ./
RUN npm ci

COPY . .

# Development
FROM base AS dev
EXPOSE 3000
CMD ["npm", "run", "dev"]

# Production build
FROM base AS builder
RUN npm run build

FROM node:22-alpine AS production
WORKDIR /app
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public
EXPOSE 3000
CMD ["node", "server.js"]
