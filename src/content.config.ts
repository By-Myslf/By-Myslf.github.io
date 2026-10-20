// This file describes the three kinds of content on the site and which
// details each one has. If you add a new detail (say, "provenance"),
// add it here too, otherwise the build will complain.

import { defineCollection } from 'astro:content';
import { glob } from 'astro/loaders';
import { z } from 'astro/zod';

// One Markdown file per object in src/content/catalogue/
const catalogue = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/catalogue' }),
  schema: z.object({
    title: z.string(),
    // Your own inventory number, e.g. "014" (keep the quotes to keep the zeros)
    number: z.coerce.string(),
    // Used for the filter on the catalogue page, e.g. "Ceramics"
    category: z.string(),
    date: z.coerce.string(), // free text: "c. 1880", "Late 18th century"
    maker: z.string().optional(),
    origin: z.string().optional(),
    materials: z.string().optional(),
    dimensions: z.string().optional(),
    // Photo file names inside public/images/catalogue/ — the first one is the main photo
    images: z.array(z.string()).default([]),
    // true = shown on the home page
    featured: z.boolean().default(false),
  }),
});

// Your own posts: news, finds, visits — in src/content/journal/
const journal = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/journal' }),
  schema: z.object({
    title: z.string(),
    date: z.coerce.date(),
    summary: z.string(),
    image: z.string().optional(), // file name inside public/images/journal/
    draft: z.boolean().default(false), // true = hidden from the website
  }),
});

// Longer pieces by you or invited specialists — in src/content/articles/
const articles = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/articles' }),
  schema: z.object({
    title: z.string(),
    date: z.coerce.date(),
    summary: z.string(),
    author: z.string(),
    authorRole: z.string().optional(), // e.g. "Ceramics specialist"
    draft: z.boolean().default(false),
  }),
});

export const collections = { catalogue, journal, articles };
