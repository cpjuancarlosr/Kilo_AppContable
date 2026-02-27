# syntax=docker/dockerfile:1
FROM node:20-alpine AS base

WORKDIR /app

ENV NODE_ENV=development \
    NEXT_TELEMETRY_DISABLED=1

FROM base AS builder

COPY package.json package-lock.json* yarn.lock* ./

RUN --mount=type=cache,target=/root/.npm \
    --mount=type=cache,target=/root/.yarn \
    if [ -f yarn.lock ]; then yarn install --frozen-lockfile; else npm install; fi

COPY . .

RUN SKIP_ENV_VALIDATION=1 npm run build

FROM node:20-alpine AS runner

WORKDIR /app

ENV NODE_ENV=production \
    NEXT_TELEMETRY_DISABLED=1 \
    PORT=3000

RUN addgroup -g 1001 -S nodejs && adduser -S nextjs -u 1001

COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static
COPY --from=builder --chown=nextjs:nodejs /app/public ./public

USER nextjs

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD node -e "require('http').get('http://localhost:3000', (r) => {if (r.statusCode !== 200) throw new Error(r.statusCode)})" || exit 1

CMD ["node", "server.js"]
