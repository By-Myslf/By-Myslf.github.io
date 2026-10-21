// ─────────────────────────────────────────────────────────────
//  THE SITE'S WORDING IN BOTH LANGUAGES
//  Menu, buttons, labels and short texts that appear on many pages.
//  Change the text between the quotes. Keep the two lists in step:
//  every line in "en" has a partner with the same name in "hu".
//
//  Longer page texts (home page, About, Contact, I buy) are at the
//  top of their own files in src/views/.
// ─────────────────────────────────────────────────────────────

export const languages = { en: 'English', hu: 'Magyar' } as const;
export type Lang = keyof typeof languages;

const en = {
  // Menu and frame
  menu: {
    catalogue: 'Catalogue',
    journal: 'Journal',
    guide: "Collector's guide",
    buying: 'I buy',
    about: 'About',
    contact: 'Contact',
  },
  mainMenu: 'Main',
  languageMenu: 'Language',
  skipToContent: 'Skip to content',
  getInTouch: 'Get in touch',

  // Shown on a Hungarian page when its text hasn't been translated yet
  notTranslated: '',

  // Catalogue labels
  no: 'No.',
  facts: {
    category: 'Item type',
    brand: 'Brand',
    date: 'Date',
    maker: 'Maker',
    origin: 'Origin',
    materials: 'Materials',
    dimensions: 'Dimensions',
  },

  // Catalogue page
  catalogue: {
    title: 'Catalogue',
    description: 'Every object in the collection, with photographs and descriptions.',
    intro: 'Every object in the collection, numbered in the order it was acquired.',
    empty: 'The catalogue is being prepared. Objects will appear here soon.',
    filterLabel: 'Filter the catalogue',
    search: 'Search',
    searchPlaceholder: 'Name, maker, place…',
    allTypes: 'All types',
    allBrands: 'All brands',
    madeBetween: 'Made between',
    from: 'From',
    to: 'To',
    and: 'and',
    after: '', // a word after the second date, if the language needs one
    decade: (d: number) => `${d}s`,
    count: '{total} objects',
    countFiltered: 'Showing {shown} of {total} objects',
    clear: 'Clear filters',
    noMatches: 'Nothing matches these filters. Try a shorter word, or clear the filters.',
  },

  // One object's page
  object: {
    back: 'Back to the catalogue',
    morePhotos: 'More photos',
    photoOf: (i: number, n: number) => `Photo ${i} of ${n}`,
    enquire: 'Write to me about this piece',
    enquirySubject: (no: string, title: string) => `About No. ${no}: ${title}`,
    otherObjects: 'Other objects',
    previous: 'Previous',
    next: 'Next',
  },

  // Journal
  journal: {
    title: 'Journal',
    description: 'Notes from the collector: new arrivals, visits, auctions and discoveries.',
    intro: 'New arrivals, visits, auctions and the occasional discovery.',
    empty: 'No posts yet.',
    byline: (date: string, owner: string) => `${date}, by ${owner}`,
    back: 'All journal posts',
    allPosts: 'All posts',
  },

  // Collector's guide
  guide: {
    title: "Collector's guide",
    description:
      'Guides to champagne glasses, buckets, stoppers, muselets and labels, for new and experienced collectors.',
    intro:
      'Practical guides to champagne objects: how to date them, care for them and build a collection. Written by specialists and by me.',
    empty: 'No guides yet.',
    by: 'By',
    published: 'Published',
    back: "Back to the Collector's guide",
    allGuides: 'All guides',
  },
};

type Words = typeof en;

const hu: Words = {
  menu: {
    catalogue: 'Katalógus',
    journal: 'Napló',
    guide: 'Gyűjtői kalauz',
    buying: 'Felvásárlás',
    about: 'Rólam',
    contact: 'Kapcsolat',
  },
  mainMenu: 'Főmenü',
  languageMenu: 'Nyelv',
  skipToContent: 'Ugrás a tartalomra',
  getInTouch: 'Kapcsolat',

  notTranslated: 'Ez a szöveg egyelőre csak angolul olvasható.',

  no: 'Ltsz.',
  facts: {
    category: 'Tárgytípus',
    brand: 'Márka',
    date: 'Datálás',
    maker: 'Készítő',
    origin: 'Származás',
    materials: 'Anyag',
    dimensions: 'Méretek',
  },

  catalogue: {
    title: 'Katalógus',
    description: 'A gyűjtemény összes tárgya, fényképekkel és leírásokkal.',
    intro: 'A gyűjtemény összes tárgya, a beszerzés sorrendjében számozva.',
    empty: 'A katalógus készül. A tárgyak hamarosan megjelennek itt.',
    filterLabel: 'A katalógus szűrése',
    search: 'Keresés',
    searchPlaceholder: 'Név, készítő, hely…',
    allTypes: 'Minden típus',
    allBrands: 'Minden márka',
    madeBetween: 'Készült',
    from: 'Ettől',
    to: 'Eddig',
    and: 'és',
    after: 'évek között',
    decade: (d: number) => `${d}-${huDecadeEnding(d)}`,
    count: '{total} tárgy',
    countFiltered: '{total} tárgyból {shown} látható',
    clear: 'Szűrők törlése',
    noMatches: 'Egy tárgy sem felel meg a szűrőknek. Próbáljon rövidebb szót, vagy törölje a szűrőket.',
  },

  object: {
    back: 'Vissza a katalógushoz',
    morePhotos: 'További fényképek',
    photoOf: (i: number, n: number) => `${i}. fénykép (összesen ${n})`,
    enquire: 'Írjon nekem erről a tárgyról',
    enquirySubject: (no: string, title: string) => `Ltsz. ${no}: ${title}`,
    otherObjects: 'További tárgyak',
    previous: 'Előző',
    next: 'Következő',
  },

  journal: {
    title: 'Napló',
    description: 'A gyűjtő jegyzetei: új szerzemények, látogatások, árverések és felfedezések.',
    intro: 'Új szerzemények, látogatások, árverések és olykor egy-egy felfedezés.',
    empty: 'Még nincs bejegyzés.',
    byline: (date: string, owner: string) => `${date} · ${owner}`,
    back: 'Az összes naplóbejegyzés',
    allPosts: 'Összes bejegyzés',
  },

  guide: {
    title: 'Gyűjtői kalauz',
    description:
      'Útmutatók pezsgőspoharakról, pezsgőhűtőkről, dugókról, pezsgőkupakokról és címkékről, kezdő és tapasztalt gyűjtőknek.',
    intro:
      'Gyakorlati útmutatók a pezsgő tárgyi emlékeiről: hogyan datáljuk és ápoljuk őket, és hogyan építsünk belőlük gyűjteményt. Szakértők és a magam írásai.',
    empty: 'Még nincs útmutató.',
    by: 'Szerző:',
    published: 'Megjelent:',
    back: 'Vissza a Gyűjtői kalauzhoz',
    allGuides: 'Összes útmutató',
  },
};

/** "1920" → "as", "1950" → "es": "1920-as", "1950-es" (followed by "évek között") */
function huDecadeEnding(decade: number): string {
  const tens = decade % 100;
  if (tens === 0) return decade % 1000 === 0 ? 'es' : 'as'; // kétezres, kilencszázas
  return [20, 30, 60, 80].includes(tens) ? 'as' : 'es';
}

export const ui: Record<Lang, Words> = { en, hu };

/**
 * Item types and brands in Hungarian. The English name (left) must match the
 * "category" or "brand" in the object files exactly. When you start using a new
 * item type or brand, add a line here; until you do, it shows in English.
 */
export const huTerms: Record<string, string> = {
  Glassware: 'Poharak',
  'Ice buckets': 'Pezsgőhűtők',
  Stoppers: 'Pezsgőzárók',
  Muselets: 'Pezsgőkupakok',
  'Bottle coasters': 'Palackalátétek',
  Ephemera: 'Nyomtatványok',
  'Openers & taps': 'Nyitók és csapok',
  Unbranded: 'Márka nélkül',
  'Various houses': 'Különböző pezsgőházak',
};
