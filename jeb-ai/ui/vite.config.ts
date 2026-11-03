import { defineConfig } from "vite";
import cesium from "vite-plugin-cesium";
import { resolve } from "path";

export default defineConfig({
  plugins: [cesium()],
  clearScreen: false,
  build: { rollupOptions: { input: { main: resolve(__dirname, "index.html"), notch: resolve(__dirname, "notch.html") } }, chunkSizeWarningLimit: 6000 },
});
