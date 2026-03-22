FROM node:22-alpine AS base

# Install pnpm
RUN npm install -g pnpm

WORKDIR /app

# ---- Dependencies ----
FROM base AS deps
COPY package.json pnpm-lock.yaml* ./
RUN pnpm install --frozen-lockfile

# ---- Build ----
FROM base AS builder
COPY --from=deps /app/node_modules ./node_modules
COPY . .

# Build args for runtime config
ARG NUXT_PUBLIC_API_BASE=http://localhost:8000/api/v1
ARG NUXT_PUBLIC_WS_BASE=ws://localhost:8000

ENV NUXT_PUBLIC_API_BASE=$NUXT_PUBLIC_API_BASE
ENV NUXT_PUBLIC_WS_BASE=$NUXT_PUBLIC_WS_BASE
ENV NODE_ENV=production

RUN pnpm build

# ---- Production ----
FROM node:22-alpine AS runner

WORKDIR /app

ENV NODE_ENV=production
ENV HOST=0.0.0.0
ENV PORT=3000

# Copy built output
COPY --from=builder /app/.output ./

EXPOSE 3000

CMD ["node", "server/index.mjs"]
