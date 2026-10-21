// Small helpers used by the pages. You don't need to edit this file.
import type { Lang } from '../i18n';

const base = import.meta.env.BASE_URL.replace(/\/$/, '');

/**
 * Builds a link that works wherever the site is published.
 * url('catalogue/') → /catalogue/    url('catalogue/', 'hu') → /hu/catalogue/
 */
export function url(path = '', lang: Lang = 'en'): string {
  const prefix = lang === 'hu' ? 'hu/' : '';
  return `${base}/${prefix}${path.replace(/^\//, '')}`;
}

/** Link to a photo in public/images/<folder>/ (photos are shared by both languages) */
export function img(folder: string, file: string): string {
  return url(`images/${folder}/${file}`);
}

/** The same page in each language: /hu/catalogue/ ↔ /catalogue/ */
export function translations(pathname: string): Record<Lang, string> {
  let path = pathname.startsWith(base) ? pathname.slice(base.length) : pathname;
  path = path.replace(/^\/+/, '');
  if (path === 'hu' || path.startsWith('hu/')) path = path.slice(2).replace(/^\/+/, '');
  return { en: url(path, 'en'), hu: url(path, 'hu') };
}

/** 21 October 2026  ·  2026. október 21. */
export function formatDate(date: Date, lang: Lang = 'en'): string {
  return date.toLocaleDateString(lang === 'hu' ? 'hu-HU' : 'en-GB', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  });
}

/** A mailto: link with the subject already filled in */
export function mailto(email: string, subject?: string): string {
  return subject ? `mailto:${email}?subject=${encodeURIComponent(subject)}` : `mailto:${email}`;
}
