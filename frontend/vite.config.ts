import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    vueDevTools(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
  server: {
    port: 5173,
    host: true,
    // 移除 historyApiFallback，在Vite中不需要
    // 添加更多配置来处理SPA路由
    fs: {
      allow: ['..']
    }
  },
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['vue', 'vue-router'],
        },
      },
    },
  },
  // 添加预览配置
  preview: {
    port: 5173,
    host: true,
    // 移除 historyApiFallback，在Vite中不需要
  }
})
