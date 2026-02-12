import { defineConfig, type UserConfig } from "vite";
import react from "@vitejs/plugin-react-swc";
import path from "path";

/**
 * Vite configuration for Food Science Toolbox Teaching Assistant
 * 
 * This configuration provides:
 * - React with SWC for fast compilation
 * - Path aliases for cleaner imports
 * - API proxy for development
 * - Optimized production builds with code splitting
 * 
 * @see https://vitejs.dev/config/
 */
export default defineConfig(({ mode }): UserConfig => {
  const isDevelopment = mode === "development";
  const isProduction = mode === "production";

  return {
    server: {
      host: "::", // Listen on all network interfaces
      port: 8080,
      proxy: {
        '/api': {
          target: process.env.VITE_API_BASE_URL || 'http://localhost:8000',
          changeOrigin: true,
          secure: false,
          rewrite: (path) => path.replace(/^\/api/, '/api'), // Keep /api prefix
          // Proxy configuration for development API requests
        },
      },
    },
    plugins: [
      react({
        // Use SWC for faster compilation
      }),
    ],
    resolve: {
      alias: {
        "@": path.resolve(__dirname, "./src"),
      },
    },
    build: {
      outDir: 'dist',
      sourcemap: isDevelopment,
      minify: isProduction ? 'esbuild' : false,
      chunkSizeWarningLimit: 1000,
      rollupOptions: {
        output: {
          // Code splitting strategy for optimal bundle sizes
          manualChunks: {
            'react-vendor': ['react', 'react-dom', 'react-router-dom'],
            'ui-vendor': [
              '@radix-ui/react-dialog',
              '@radix-ui/react-dropdown-menu',
              '@radix-ui/react-tabs',
              '@radix-ui/react-toast',
            ],
            'api-vendor': ['axios'],
          },
        },
      },
    },
    define: {
      'process.env': {},
    },
  };
});
