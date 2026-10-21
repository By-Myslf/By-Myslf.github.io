// Fetches content in a consistent order, in either language.
// You don't need to edit this file.
//
// For Hungarian, each item takes its words from the Hungarian twin file
// (same file name, in the "hu" folder) and everything else from the English
// file. Anything not translated yet falls back to English.
import { getCollection, type CollectionEntry } from 'astro:content';
import { huTerms, type Lang } from '../i18n';

type Catalogue = CollectionEntry<'catalogue'>;
type Journal = CollectionEntry<'journal'>;
type Articles = CollectionEntry<'articles'>;

/** One item, ready to show in one language */
export interface Localized<Data, Entry> {
  id: string;
  /** The details in the page's language (English where there's no translation) */
  data: Data;
  /** The original English details, used for filters and links */
  en: Data;
  /** The file whose description is shown (Hungarian if it has one) */
  entry: Entry;
  /** false when a Hungarian page has to show the English description */
  textTranslated: boolean;
}

export type LocalObject = Localized<Catalogue['data'], Catalogue | CollectionEntry<'catalogueHu'>>;
export type LocalPost = Localized<Journal['data'], Journal | CollectionEntry<'journalHu'>>;
export type LocalArticle = Localized<Articles['data'], Articles | CollectionEntry<'articlesHu'>>;

/** Keeps only the details that were actually filled in */
function filledIn<T extends object>(data: T | undefined): Partial<T> {
  if (!data) return {};
  return Object.fromEntries(
    Object.entries(data).filter(([, v]) => v !== undefined && v !== ''),
  ) as Partial<T>;
}

function localize<Data extends object, Entry extends { id: string; data: Data; body?: string }, HuEntry extends { id: string; data: object; body?: string }>(
  items: Entry[],
  translations: HuEntry[],
  lang: Lang,
  extra: (data: Data) => Partial<Data> = () => ({}),
): Localized<Data, Entry | HuEntry>[] {
  const byId = new Map(translations.map((t) => [t.id, t]));
  return items.map((item) => {
    if (lang === 'en') {
      return { id: item.id, data: item.data, en: item.data, entry: item, textTranslated: true };
    }
    const hu = byId.get(item.id);
    const hasText = Boolean(hu?.body?.trim());
    return {
      id: item.id,
      data: { ...item.data, ...extra(item.data), ...(filledIn(hu?.data) as Partial<Data>) },
      en: item.data,
      entry: hasText && hu ? hu : item,
      textTranslated: hasText,
    };
  });
}

/** Item type or brand in Hungarian, from the list in src/i18n.ts */
export function term(value: string, lang: Lang): string;
export function term(value: string | undefined, lang: Lang): string | undefined;
export function term(value: string | undefined, lang: Lang) {
  if (!value || lang === 'en') return value;
  return huTerms[value] ?? value;
}

/** All catalogue objects, ordered by inventory number */
export async function getObjects(lang: Lang = 'en'): Promise<LocalObject[]> {
  const items = (await getCollection('catalogue')).sort((a, b) =>
    a.data.number.localeCompare(b.data.number, 'en', { numeric: true }),
  );
  const hu = lang === 'hu' ? await getCollection('catalogueHu') : [];
  return localize(items, hu, lang, (d) => ({
    category: term(d.category, lang),
    brand: term(d.brand, lang),
  }));
}

/** Published journal posts, newest first */
export async function getPosts(lang: Lang = 'en'): Promise<LocalPost[]> {
  const posts = (await getCollection('journal', ({ data }) => !data.draft)).sort(
    (a, b) => b.data.date.getTime() - a.data.date.getTime(),
  );
  const hu = lang === 'hu' ? await getCollection('journalHu') : [];
  return localize(posts, hu, lang);
}

/** Published articles, newest first */
export async function getArticles(lang: Lang = 'en'): Promise<LocalArticle[]> {
  const articles = (await getCollection('articles', ({ data }) => !data.draft)).sort(
    (a, b) => b.data.date.getTime() - a.data.date.getTime(),
  );
  const hu = lang === 'hu' ? await getCollection('articlesHu') : [];
  return localize(articles, hu, lang);
}

// ── Page lists for the object, journal and guide pages ─────────

export async function objectPaths(lang: Lang) {
  const objects = await getObjects(lang);
  return objects.map((item, i) => ({
    params: { id: item.id },
    props: { item, prev: objects[i - 1], next: objects[i + 1] },
  }));
}

export async function postPaths(lang: Lang) {
  const posts = await getPosts(lang);
  return posts.map((post) => ({ params: { id: post.id }, props: { post } }));
}

export async function articlePaths(lang: Lang) {
  const articles = await getArticles(lang);
  return articles.map((article) => ({ params: { id: article.id }, props: { article } }));
}
