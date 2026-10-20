// Fetches content in a consistent order. You don't need to edit this file.
import { getCollection } from 'astro:content';

/** All catalogue objects, ordered by inventory number */
export async function getObjects() {
  const items = await getCollection('catalogue');
  return items.sort((a, b) =>
    a.data.number.localeCompare(b.data.number, 'en', { numeric: true }),
  );
}

/** Published journal posts, newest first */
export async function getPosts() {
  const posts = await getCollection('journal', ({ data }) => !data.draft);
  return posts.sort((a, b) => b.data.date.getTime() - a.data.date.getTime());
}

/** Published articles, newest first */
export async function getArticles() {
  const articles = await getCollection('articles', ({ data }) => !data.draft);
  return articles.sort((a, b) => b.data.date.getTime() - a.data.date.getTime());
}
