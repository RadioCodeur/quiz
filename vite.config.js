import { defineConfig } from 'vite';
import { fileURLToPath } from 'node:url';
export default defineConfig({
  base: './',
  build: {
    rollupOptions: {
      input: {
        quiz: fileURLToPath(new URL('./index.html', import.meta.url)),
        cours: fileURLToPath(new URL('./cours.html', import.meta.url)),
      },
    },
  },
});
