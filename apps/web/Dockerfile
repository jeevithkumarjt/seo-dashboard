FROM node:22-alpine
WORKDIR /app
RUN corepack enable
COPY package.json pnpm-lock.yaml* pnpm-workspace.yaml turbo.json ./
COPY apps/web/package.json apps/web/package.json
RUN pnpm install --filter web...
COPY . .
RUN pnpm --filter web build
CMD ["pnpm","--filter","web","start"]
