// @ts-check
import { defineConfig } from 'astro/config';

// You normally don't need to touch this file.
// When the site is published, GitHub fills in SITE and BASE automatically
// (see .github/workflows/deploy.yml), so the links work whether your
// repository is called "yourname.github.io" or something else.
export default defineConfig({
  site: process.env.SITE || 'http://localhost:4321',
  base: process.env.BASE || '/',
});
