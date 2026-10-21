# Champagne Club Budapest website

A website for a private collection of antiques and art: a catalogue with photos, a journal, expert articles, an about page and a contact page. It's built with [Astro](https://astro.build) and published free with GitHub Pages.

You never need to write code to add content. Each object, post and article is one small text file.

---

## 1. Put the site on GitHub (once)

1. Create a new **public** repository on GitHub. Don't tick "Add a README".
   - Name it `yourusername.github.io` for the address `https://yourusername.github.io`,
   - or give it any name (e.g. `collection`) for `https://yourusername.github.io/collection`.
2. On the empty repository page, click **uploading an existing file**.
3. Open the unzipped `collection-site` folder, select **everything inside it**, and drag it into the browser window. Click **Commit changes**.
4. Check that a folder called **`.github`** appears in the file list. Computers often hide folders whose names start with a dot, so it may have been left out. If it's missing:
   - Click **Add file → Create new file**.
   - In the name box type `.github/workflows/deploy.yml` (the slashes create the folders).
   - Paste in the contents of `deploy.yml` from the zip (open it with a text editor), then commit.
5. Go to **Settings → Pages**. Under **Source**, choose **GitHub Actions**. (Not "Deploy from a branch". Astro needs GitHub to build the site first.)
6. Open the **Actions** tab. You'll see "Publish website" running. When it shows a green tick (about a minute), your site is live. The address is shown under **Settings → Pages**.

From now on, **every commit publishes the site again automatically.**

If the run shows a red cross, click it, then click the failed step to see the message. It's almost always a typo in one of your content files; the message names the file.

---

## 2. Change your name, email and site title

Open **`src/site.config.ts`**, click the pencil icon, change the text between the quotes, and commit.

The email address there is used by every "Write to me" button. It will be visible on the website, so you may prefer a separate address just for the collection.

---

## 3. Add an object to the catalogue

**Step 1. Upload the photos.** Go to `public/images/catalogue/`, click **Add file → Upload files**, and add the photos.

- Use simple file names without spaces: `009-vase.jpg`, `009-vase-back.jpg`.
- Resize photos to about 1600 pixels on the longest side before uploading. Phone photos are often 4000+ pixels and make pages slow.

**Step 2. Create the description.** Go to `src/content/catalogue/`, click **Add file → Create new file**, name it e.g. `009-zsolnay-vase.md` (the name becomes the web address), and paste:

```markdown
---
title: Vase with iridescent glaze
number: "009"
category: Ceramics
date: c. 1900
maker: Zsolnay
origin: Pécs, Hungary
materials: Earthenware with eosin glaze
dimensions: Height 24 cm
images:
  - 009-vase.jpg
  - 009-vase-back.jpg
featured: false
---

Write the description here. Several paragraphs are fine.
A blank line starts a new paragraph.
```

Commit, and the object appears in the catalogue and gets its own page.

Notes:

- The part between the two `---` lines is the **details**; below it is the **description**.
- Keep `number` in quotes so leading zeros stay (`"009"`, not `9`). The catalogue is sorted by number.
- `category` creates the filter buttons on the catalogue page. Spell each category exactly the same way every time.
- Leave out any line you don't need (for example `maker` or `dimensions`).
- `featured: true` shows the object on the home page. The first featured object hangs on the green wall at the top.
- No photos yet? Write `images: []`. The object shows a "Photo to follow" mount.

---

## 4. Write a journal post

Create a new file in `src/content/journal/`, e.g. `2026-11-autumn-auction.md`:

```markdown
---
title: An autumn auction
date: 2026-11-03
summary: One or two sentences shown in the list of posts.
image: autumn-auction.jpg
---

Your post here.

## A subheading

More text. **Bold**, *italic*, and [a link](https://example.com) all work.

> A quotation looks like this.
```

- `image` is optional. Upload it to `public/images/journal/`.
- Add `draft: true` to hide a post until it's ready.

## 5. Publish an expert article

Same as a journal post, but in `src/content/articles/`, with the author's details:

```markdown
---
title: Reading the marks on old silver
date: 2026-08-20
summary: One or two sentences about the article.
author: Dr Anna Kovács
authorRole: Silver specialist
---

The article text.
```

## 6. Edit the About and Contact pages

The text is in `src/pages/about.astro` and `src/pages/contact.astro`. Edit the sentences between the `<p>` and `</p>` tags and leave the tags themselves alone.

---

## Removing the sample content

The sample objects, posts and articles are there to show how things look. Delete their files from `src/content/...` and `public/images/...` once you've added your own. (Open a file, click **⋯ → Delete file**, then commit.) Keep the `HOW-TO-ADD.txt` file in each folder: GitHub removes folders that have no files in them.

With no content at all, the site still works: the catalogue says it is being prepared, and the Journal and Articles pages say there is nothing yet.

## Where things are

| What | Where |
| --- | --- |
| Name, email, site description | `src/site.config.ts` |
| Catalogue objects | `src/content/catalogue/` |
| Journal posts | `src/content/journal/` |
| Articles | `src/content/articles/` |
| Photos | `public/images/catalogue/` and `public/images/journal/` |
| About and Contact text | `src/pages/about.astro`, `src/pages/contact.astro` |
| Colours and fonts | top of `src/styles/global.css` |
| Home page wording | `src/pages/index.astro` |
| Publishing settings | `.github/workflows/deploy.yml` (no need to touch) |

## Working on your own computer (optional)

If you later want to preview changes before publishing: install [Node.js](https://nodejs.org) (version 22 or newer), open a terminal in this folder, and run:

```bash
npm install
npm run dev
```

Then open http://localhost:4321 in your browser. The page updates as you save files.
