/// <reference types="cypress" />

// ==== Paramètres login ====
const LOGIN_PATH = '/connexion'
const LOGIN_EMAIL = 'retention_structures@example.com'
const LOGIN_PASSWORD = 'user@AZERTY123'
const SELECTOR_EMAIL = 'input[type="email"], input[name="email"], #email'
const SELECTOR_PASSWORD =
  'input[type="password"], input[name="password"], #password'
const SELECTOR_SUBMIT = 'button[type="submit"], [data-testid="submit"]'

// ==== Pages spéciales ====
const SPECIAL_CRAWL_PAGE = '/offre/individuelle/1779/recapitulatif/details'
const AFTER_SWITCH_PAGE = '/offre/163/collectif/recapitulatif'
const TARGET_STRUCTURE_NAME = 'eac_2_lieu [BON EAC]'

// ==== Utilitaires ====
const isHtmlLike = (url: string) =>
  !/\.(png|jpe?g|gif|svg|webp|pdf|zip|mp4|css|js|ico)(\?|#|$)/i.test(url)

// Convertit une URL absolue ou un path relatif en path "/xxx?y"
const toPath = (s: string) => {
  try {
    const u = new URL(s)
    return (u.pathname || '/') + (u.search || '')
  } catch {
    return s.startsWith('/') ? s : `/${s}`
  }
}

// Convertit une URL absolue ou path en absolue basée sur BASE
const toAbsUrl = (s: string) => {
  try {
    const u = new URL(s)
    return u.toString()
  } catch {
    return `${BASE}${s.startsWith('/') ? '' : '/'}${s}`
  }
}

const normalizeUrl = (u: string) => {
  try {
    const url = new URL(u)
    url.hash = ''
    return url.toString()
  } catch {
    return u
  }
}

const uniq = <T>(arr: T[]) => Array.from(new Set(arr))

type PageRow = {
  url: string
  finalUrl: string
  status?: number
  title: string
  h1: string[]
  h2: string[]
  h3: string[]
  h4: string[]
  h5: string[]
  h6: string[]
  lang: string
  flags: string[]
  redirect: boolean
  renderedMs: number
}

const rows: PageRow[] = []
let BASE = ''

// ==== Audit rules ====
const flagRules = (row: Omit<PageRow, 'flags'>): string[] => {
  const flags: string[] = []
  if (!row.title || !row.title.trim()) flags.push('TITLE_EMPTY')
  if (!row.lang || row.lang.trim().toLowerCase() !== 'fr')
    flags.push('LANG_NOT_FR')
  if (row.h1.length === 0) flags.push('NO_H1')
  if (row.h1.length > 1) flags.push('MULTIPLE_H1')
  const allHeadings = [
    ...row.h1,
    ...row.h2,
    ...row.h3,
    ...row.h4,
    ...row.h5,
    ...row.h6,
  ]
  if (allHeadings.some((t) => !t || !t.trim())) flags.push('EMPTY_HEADING')
  const len = (row.title || '').trim().length
  if (len > 0 && len < 10) flags.push('TITLE_TOO_SHORT')
  if (len > 60) flags.push('TITLE_TOO_LONG')
  if (row.redirect) flags.push('REDIRECT')
  if (row.renderedMs > 3000) flags.push('SLOW_RENDER')
  return uniq(flags)
}

const collectFromDoc = (doc: Document) => {
  const getTexts = (sel: string) =>
    Array.from(doc.querySelectorAll(sel))
      .map((el) => (el as HTMLElement).innerText.replace(/\s+/g, ' ').trim())
      .filter(Boolean)

  const links = Array.from(doc.querySelectorAll('a[href]'))
    .map((a) => (a as HTMLAnchorElement).href)
    .filter((href) => {
      try {
        const u = new URL(href)
        return u.origin === BASE && isHtmlLike(u.pathname)
      } catch {
        return false
      }
    })

  return {
    title: doc.title || '',
    h1: getTexts('h1'),
    h2: getTexts('h2'),
    h3: getTexts('h3'),
    h4: getTexts('h4'),
    h5: getTexts('h5'),
    h6: getTexts('h6'),
    lang: (doc.documentElement.getAttribute('lang') || '').trim(),
    links,
  }
}

// ==== Cookies banner ====
const acceptCookies = () => {
  cy.get('body').then(($body) => {
    const hasBanner = /Respect de votre vie privée|cookies/i.test($body.text())
    if (!hasBanner) return

    const $btn = $body
      .find('button, [role="button"]')
      .filter((_, el) => /Tout accepter/i.test(Cypress.$(el).text()))
      .filter(':visible')
      .first()

    if ($btn.length) {
      cy.wrap($btn).click({ force: true })
    }
  })
}
// ==== Attente SPA ====
const waitForAppReady = (
  readySel?: string,
  loaderSel?: string,
  extraWait = 0
) => {
  if (readySel) cy.get(readySel, { timeout: 15000 }).should('exist')
  if (loaderSel) {
    cy.get('body').then(($body) => {
      if ($body.find(loaderSel).length) {
        cy.get(loaderSel, { timeout: 15000 }).should('not.exist')
      }
    })
  }
  if (extraWait > 0) cy.wait(extraWait)
}

// ==== Visit + collect ====
const visitAndCollect = (
  path: string
): Cypress.Chainable<PageRow & { links: string[] }> => {
  const url = toAbsUrl(path)
  const startedAt = Date.now()
  let finalUrl = url
  let cfg: any
  cy.readFile('cypress/fixtures/headings.seeds.json').then((c) => {
    cfg = c
  })

  let inFlight = 0
  const markIdle = () =>
    cy.window({ log: false }).then(
      () =>
        new Cypress.Promise<void>((resolve) => {
          const start = Date.now()
          const check = () => {
            if (inFlight === 0 && Date.now() - start > 300) return resolve()
            setTimeout(check, 100)
          }
          check()
        })
    )

  return cy
    .visit(url, {
      retryOnStatusCodeFailure: true,
      retryOnNetworkFailure: true,
      onBeforeLoad(win) {
        const origFetch = win.fetch.bind(win)
        // @ts-expect-error
        win.fetch = (...args) => {
          inFlight++
          return origFetch(...args).finally(() => {
            inFlight--
          })
        }
        const OrigXHR = win.XMLHttpRequest
        // @ts-expect-error
        function WrappedXHR(this: any) {
          const xhr = new OrigXHR()
          xhr.addEventListener('loadstart', () => {
            inFlight++
          })
          xhr.addEventListener('loadend', () => {
            inFlight--
          })
          return xhr
        }
        // @ts-expect-error
        win.XMLHttpRequest = WrappedXHR
      },
    })
    .then(() => {
      finalUrl = window.location.href
      cy.document().its('readyState').should('eq', 'complete')
      return markIdle().then(() => markIdle())
    })
    .then(() => {
      waitForAppReady(
        cfg?.readySelector,
        cfg?.loaderSelector,
        cfg?.extraWaitMs || 0
      )
      const renderedMs = Date.now() - startedAt
      cy.document().then((doc) => {
        const data = collectFromDoc(doc)
        const redirect = normalizeUrl(finalUrl) !== normalizeUrl(url)
        const baseRow = {
          url,
          finalUrl,
          status: undefined,
          title: data.title,
          h1: data.h1,
          h2: data.h2,
          h3: data.h3,
          h4: data.h4,
          h5: data.h5,
          h6: data.h6,
          lang: data.lang,
          redirect,
          renderedMs,
        }
        const flags = flagRules(baseRow)
        const row: PageRow & { links: string[] } = {
          ...baseRow,
          flags,
          links: data.links,
        }
        rows.push(row)
        return row
      })
    })
}

// ==== Rapport ====
const writeReports = () => {
  cy.writeFile('cypress/outputs/headings-report.json', rows, { log: false })
  const esc = (v: string) => `"${(v || '').replace(/"/g, '""')}"`
  const toLine = (r: PageRow) =>
    [
      esc(r.url),
      esc(r.finalUrl),
      r.status ?? '',
      esc(r.title),
      esc(r.h1.join(' | ')),
      esc(r.h2.join(' | ')),
      esc(r.h3.join(' | ')),
      esc(r.h4.join(' | ')),
      esc(r.h5.join(' | ')),
      esc(r.h6.join(' | ')),
      esc(r.lang),
      esc(r.flags.join(' | ')),
      r.redirect ? '1' : '0',
      r.renderedMs,
    ].join(',')
  const header =
    'url,finalUrl,status,title,h1,h2,h3,h4,h5,h6,lang,flags,redirect,renderedMs'
  const csv = [header, ...rows.map(toLine)].join('\n')
  cy.writeFile('cypress/outputs/headings-report.csv', csv, { log: false })
}

// ==== Login ====
const loginOnce = () => {
  cy.session(
    'pro-login-v1',                           // clé stable
    () => {
      cy.visit(toAbsUrl(LOGIN_PATH))
      // (si tu as l’acceptation des cookies « une fois » au début, ne refais pas ici)
      cy.get(SELECTOR_EMAIL, { timeout: 10000 }).clear().type(LOGIN_EMAIL)
      cy.get(SELECTOR_PASSWORD, { timeout: 10000 }).clear().type(LOGIN_PASSWORD)
      cy.get(SELECTOR_SUBMIT).first().click()
      cy.location('pathname', { timeout: 15000 }).should((p) => expect(p).not.to.eq(LOGIN_PATH))
      cy.get('main, [role="main"], #root', { timeout: 10000 }).should('exist')
    },
    {
      cacheAcrossSpecs: true,
      validate() {
        // petite page rapide qui nécessite d'être connecté
        cy.visit(toAbsUrl('/accueil'))
        // remplace par un sélecteur qui n’existe QUE connecté (ex: le menu de structure)
        cy.get('[data-testid="offerer-select"]', { timeout: 5000 }).should('be.visible')
      },
    }
  )
}


// ==== Switch structure ====
const switchStructure = (name: string) => {
  cy.get('[data-testid="offerer-select"]', { timeout: 10000 }).click({
    force: true,
  })
  cy.contains(
    'button[role="menuitem"], [data-radix-collection-item]',
    /^Changer$/i,
    { timeout: 10000 }
  )
    .first()
    .click({ force: true })
  cy.contains(
    'span, [role="menuitem"], li, button, [data-radix-collection-item]',
    name,
    { timeout: 10000 }
  )
    .first()
    .click({ force: true })
  cy.contains(name, { timeout: 10000 }).should('exist')
}

// ==== Test ====
describe('Extraction titres & headings (local, SPA, FR)', () => {
  let seeds: any
  before(() => {
		cy.visit(BASE || 'http://localhost:3001')
		cy.findAllByRole('heading',{name: "Connectez-vous"})
		acceptCookies()
    cy.readFile('cypress/fixtures/headings.seeds.json').then((cfg) => {
      seeds = cfg
      BASE = (cfg.baseUrl || 'http://localhost:3001').replace(/\/$/, '')
    })
  })

  it('Public → Auth → Page spéciale → Switch → Page finale', () => {
    const visited = new Set<string>()
    const queue: string[] = []

    // PUBLIC avant login
    seeds.public.forEach((p: string) => queue.push(toPath(p)))

    const processQueue = (): Cypress.Chainable<void> => {
      const next = queue.shift()
      if (!next) return cy.wrap(undefined)
      const norm = normalizeUrl(toAbsUrl(next))
      if (visited.has(norm)) return processQueue()
      visited.add(norm)
      if (
        seeds.excludePathStartsWith?.some((pref: string) =>
          norm.includes(`${BASE}${pref}`)
        )
      )
        return processQueue()
      return visitAndCollect(next).then((res) => {
        let links = res.links.map(toPath)
        if (
          seeds.maxCrawlLinksPerPage &&
          links.length > seeds.maxCrawlLinksPerPage
        )
          links = links.slice(0, seeds.maxCrawlLinksPerPage)
        const pathOnly = new URL(res.finalUrl).pathname
        if (seeds.crawlFrom.includes(pathOnly)) {
          links.forEach((lnk) => {
            const n = normalizeUrl(toAbsUrl(lnk))
            if (!visited.has(n)) queue.push(lnk)
          })
        }
        return processQueue()
      })
    }

    processQueue()
      .then(() => {
        loginOnce()
        seeds.auth.forEach((p: string) => queue.push(toPath(p)))
        return processQueue()
      })
      .then(() => {
        return visitAndCollect(SPECIAL_CRAWL_PAGE).then((res) => {
          res.links.forEach((lnk) => {
            const p = toPath(lnk)
            const n = normalizeUrl(toAbsUrl(p))
            if (!visited.has(n)) queue.push(p)
          })
          return processQueue()
        })
      })
      .then(() => {
        switchStructure(TARGET_STRUCTURE_NAME)
        return visitAndCollect(AFTER_SWITCH_PAGE)
      })
  })

  after(() => {
    const titles = new Map<string, number>()
    rows.forEach((r) => {
      const key = (r.title || '').trim()
      if (key) titles.set(key, (titles.get(key) || 0) + 1)
    })
    const duplicated = new Set<string>(
      [...titles.entries()].filter(([, c]) => c > 1).map(([t]) => t)
    )
    rows.forEach((r) => {
      if (duplicated.has((r.title || '').trim()))
        r.flags = uniq([...r.flags, 'TITLE_DUPLICATE'])
    })
    cy.log(`Pages scannées: ${rows.length}`)
    const counts = rows
      .flatMap((r) => r.flags)
      .reduce<Record<string, number>>((acc, f) => {
        acc[f] = (acc[f] || 0) + 1
        return acc
      }, {})
    cy.log(`Flags: ${JSON.stringify(counts, null, 2)}`)
    writeReports()
  })
})
