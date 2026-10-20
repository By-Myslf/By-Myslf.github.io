// Small helpers used by the pages. You don't need to edit this file.

const base = import.meta.env.BASE_URL.replace(/\/$/, '');

/** Builds a link that works wherever the site is published. url('catalogue/') → /your-repo/catalogue/ */
export function url(path = ''): string {
  return `${base}/${path.replace(/^\//, '')}`;
}

/** Link to a photo in public/images/<folder>/ */
export function img(folder: string, file: string): string {
  return url(`images/${folder}/${file}`);
}

/** 21 October 2026 */
export function formatDate(date: Date): string {
  return date.toLocaleDateString('en-GB', { day: 'numeric', month: 'long', year: 'numeric' });
}

/** A mailto: link with the subject already filled in */
export function mailto(email: string, subject?: string): string {
  return subject ? `mailto:${email}?subject=${encodeURIComponent(subject)}` : `mailto:${email}`;
}
