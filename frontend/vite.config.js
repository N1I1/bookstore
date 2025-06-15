import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

export default defineConfig({
  plugins: [vue()]
  // server: {
  //   proxy: {
  //     '/api': {
  //       target: 'http://127.0.0.1:5000', // Flask 后端地址
  //       changeOrigin: true,
  //       rewrite: path => path.replace(/^\/api/, '/api')
  //     }
  //   }
  // }
})
