#!/bin/bash
set -e

# 1. Check for npm
if ! command -v npm &> /dev/null; then
  echo "[ERROR] npm is not installed. Please install Node.js and npm first." >&2
  exit 1
fi

# 2. Install dependencies if missing
if [ ! -d "node_modules/tailwindcss" ]; then
  echo "[INFO] Installing Tailwind CSS, PostCSS, and Autoprefixer..."
  npm install -D tailwindcss postcss autoprefixer
fi

# 3. Ensure tailwind.config.js exists
if [ ! -f "tailwind.config.js" ]; then
  echo "[INFO] Creating tailwind.config.js..."
  cat > tailwind.config.js << 'EOF'
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./frontend/public/**/*.html",
    "./frontend/public/**/*.js",
    "./frontend/public/index.html"
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
EOF
fi

# 4. Ensure entry CSS file exists
ENTRY_CSS="frontend/public/styles/input.css"
if [ ! -f "$ENTRY_CSS" ]; then
  echo "[INFO] Creating $ENTRY_CSS..."
  mkdir -p frontend/public/styles
  cat > "$ENTRY_CSS" << 'EOF'
@tailwind base;
@tailwind components;
@tailwind utilities;
EOF
fi

# 5. Build Tailwind CSS
OUT_CSS="frontend/public/assets/tailwind.prod.css"
echo "[INFO] Building production Tailwind CSS..."
npx tailwindcss -i "$ENTRY_CSS" -o "$OUT_CSS" --minify

if [ -f "$OUT_CSS" ]; then
  echo "[SUCCESS] Production Tailwind CSS built at $OUT_CSS"
  echo "[INFO] File size: $(du -h "$OUT_CSS" | cut -f1)"
else
  echo "[ERROR] Failed to build Tailwind CSS." >&2
  exit 2
fi 