const http = require("node:http");
const fs = require("node:fs");
const path = require("node:path");

const root = __dirname;
const port = Number(process.env.PORT || 8765);

const contentTypes = {
  ".html": "text/html; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".json": "application/json; charset=utf-8",
  ".svg": "image/svg+xml",
  ".png": "image/png",
  ".jpg": "image/jpeg",
  ".jpeg": "image/jpeg",
  ".ico": "image/x-icon",
};

function resolveRequestPath(requestUrl) {
  const url = new URL(requestUrl, `http://localhost:${port}`);
  const decoded = decodeURIComponent(url.pathname);
  const normalized = path.normalize(decoded).replace(/^(\.\.[/\\])+/, "");
  const relativePath = normalized === "/" ? "index.html" : normalized.replace(/^[/\\]/, "");
  const filePath = path.resolve(root, relativePath);

  if (!filePath.startsWith(root)) {
    return null;
  }
  return filePath;
}

function send(response, status, body, headers = {}) {
  response.writeHead(status, {
    "Cache-Control": "no-store",
    ...headers,
  });
  response.end(body);
}

const server = http.createServer((request, response) => {
  if (request.method !== "GET" && request.method !== "HEAD") {
    send(response, 405, "Method Not Allowed", {"Content-Type": "text/plain; charset=utf-8"});
    return;
  }

  if (request.url === "/healthz") {
    send(response, 200, "ok", {"Content-Type": "text/plain; charset=utf-8"});
    return;
  }

  const filePath = resolveRequestPath(request.url || "/");
  if (!filePath) {
    send(response, 403, "Forbidden", {"Content-Type": "text/plain; charset=utf-8"});
    return;
  }

  fs.readFile(filePath, (error, data) => {
    if (error) {
      send(response, 404, "Not Found", {"Content-Type": "text/plain; charset=utf-8"});
      return;
    }

    const ext = path.extname(filePath).toLowerCase();
    response.writeHead(200, {
      "Content-Type": contentTypes[ext] || "application/octet-stream",
      "Cache-Control": "no-store",
    });
    if (request.method === "HEAD") {
      response.end();
    } else {
      response.end(data);
    }
  });
});

server.listen(port, "0.0.0.0", () => {
  console.log(`D4D Resilient Maritime COP demo listening on ${port}`);
});
