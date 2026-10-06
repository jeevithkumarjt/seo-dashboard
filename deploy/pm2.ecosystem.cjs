module.exports = {
  apps: [
    { name: "seo-web", cwd: "./apps/web", script: "pnpm", args: "start", env: { NODE_ENV: "production" } },
    { name: "seo-api", cwd: "./apps/api", script: ".venv/bin/uvicorn", args: "app.main:app --host 127.0.0.1 --port 8000" }
  ]
};
