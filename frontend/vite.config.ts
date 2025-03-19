import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// https://vite.dev/config/
// base should be set to the repo for github pages https://vite.dev/guide/static-deploy.html#gitlab-pages-and-gitlab-ci
export default defineConfig({
  plugins: [react()],
  base: '/yoga-with-friends/',
});
