// This file describes the kinds of content on the site and which details
// each one has. If you add a new detail (say, "provenance"), add it here
// too, otherwise the build will complain.
//
// Each kind of content has a Hungarian twin in a "hu" folder inside it,
// e.g. src/content/catalogue/hu/. A Hungarian file has the SAME file name
// as its English partner and only holds the words: title, a few text
// details and the description. Numbers, dates, photos and so on are taken
// from the English file, so you only enter them once.

import { defineCollection } from 'astro:content';
import { glob } from 'astro/loaders';
import { z } from 'astro/zod';

// One Markdown file per object in src/content/catalogue/
const catalogue = defineCollection({
  loader: glob({ pattern: '*.md', base: './src/content/catalogue' }),
  schema: z.object({
    title: z.string(),
    // Your own inventory number, e.g. "014" (keep the quotes to keep the zeros)
    number: z.coerce.string(),
    // The item type, used for the "Item type" filter, e.g. "Glassware"
    // (its Hungarian name is in src/i18n.ts)
    category: z.string(),
    // The champagne house or brand, used for the "Brand" filter, e.g. "Unbranded"
    brand: z.string().optional(),
    date: z.coerce.string(), // free text: "c. 1880", "Late 18th century"
    // Approximate year it was made, as a number, for the "Made between" filter: 1885
    year: z.number().int().optional(),
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

// Hungarian words for an object — in src/content/catalogue/hu/
// Leave out any line you don't need: the English one is used instead.
const catalogueHu = defineCollection({
  loader: glob({ pattern: '*.md', base: './src/content/catalogue/hu' }),
  schema: z.object({
    title: z.string().optional(),
    date: z.coerce.string().optional(),
    maker: z.string().optional(),
    origin: z.string().optional(),
    materials: z.string().optional(),
    dimensions: z.string().optional(),
  }),
});

// Your own posts: news, finds, visits — in src/content/journal/
const journal = defineCollection({
  loader: glob({ pattern: '*.md', base: './src/content/journal' }),
  schema: z.object({
    title: z.string(),
    date: z.coerce.date(),
    summary: z.string(),
    image: z.string().optional(), // file name inside public/images/journal/
    draft: z.boolean().default(false), // true = hidden from the website
  }),
});

// Hungarian version of a post — in src/content/journal/hu/
const journalHu = defineCollection({
  loader: glob({ pattern: '*.md', base: './src/content/journal/hu' }),
  schema: z.object({
    title: z.string().optional(),
    summary: z.string().optional(),
  }),
});

// The Collector's guide: longer pieces by you or invited specialists — in src/content/articles/
const articles = defineCollection({
  loader: glob({ pattern: '*.md', base: './src/content/articles' }),
  schema: z.object({
    title: z.string(),
    date: z.coerce.date(),
    summary: z.string(),
    author: z.string(),
    authorRole: z.string().optional(), // e.g. "Ceramics specialist"
    draft: z.boolean().default(false),
  }),
});

// Hungarian version of a guide — in src/content/articles/hu/
const articlesHu = defineCollection({
  loader: glob({ pattern: '*.md', base: './src/content/articles/hu' }),
  schema: z.object({
    title: z.string().optional(),
    summary: z.string().optional(),
    author: z.string().optional(),
    authorRole: z.string().optional(),
  }),
});

export const collections = { catalogue, catalogueHu, journal, journalHu, articles, articlesHu };
