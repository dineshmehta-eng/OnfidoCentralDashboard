import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const root = path.resolve(path.dirname(__filename), "..");
const src = path.join(root, "frontend");
const dist = path.join(root, "dist");
const publicDir = path.join(root, "public");

const backendUrl = (process.env.DASHBOARD_API_BASE ?? "").replace(/\/+$/, "");

function copyDir(from, to) {
  fs.mkdirSync(to, { recursive: true });
  for (const entry of fs.readdirSync(from, { withFileTypes: true })) {
    const srcPath = path.join(from, entry.name);
    const destPath = path.join(to, entry.name);
    if (entry.isDirectory()) {
      copyDir(srcPath, destPath);
    } else {
      fs.copyFileSync(srcPath, destPath);
    }
  }
}

fs.rmSync(dist, { recursive: true, force: true });
fs.rmSync(publicDir, { recursive: true, force: true });
copyDir(src, dist);
copyDir(src, publicDir);

for (const indexPath of [path.join(dist, "index.html"), path.join(publicDir, "index.html")]) {
  let html = fs.readFileSync(indexPath, "utf8");
  const configScript = `<script>window.DASHBOARD_API_BASE=${JSON.stringify(backendUrl)};</script>\n`;
  if (!html.includes("window.DASHBOARD_API_BASE")) {
    html = html.replace('<script src="/fastapi_bridge.js', configScript + '<script src="/fastapi_bridge.js');
  }
  fs.writeFileSync(indexPath, html);
}

console.log(`Built Vercel frontend in ${dist} and ${publicDir}`);
console.log(`Backend API base: ${backendUrl || "(same origin)"}`);
