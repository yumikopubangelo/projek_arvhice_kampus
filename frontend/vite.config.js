import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  
  // CSS config
  css: {
    postcss: './postcss.config.js',
  },
  
  // Dev server config
  server: {
    port: 5173,
    host: true, // Allow external access
    strictPort: true,
  },
  
  // Build config
  build: {
    outDir: "dist",
    sourcemap: false,
    minify: 'esbuild',
    rollupOptions: {
      output: {
        manualChunks: {
          'react-vendor': ['react', 'react-dom', 'react-router-dom'],
        },
      },
    },
  },
  
  // Resolve config
  resolve: {
    alias: {
      '@': '/src',
    },
  },
});