export const shouldStatusBarBeColored = pathname => {
  const pathWithColoredHeader = [
    '/accueil',
    '/recherche/criteres-categorie',
    '/recherche/criteres-localisation',
    '/recherche/criteres-localisation/place',
    '/recherche/resultats/details/(.+)',
    '/recherche/resultats/filtres',
    '/recherche/resultats/filtres/localisation',
    '/recherche/resultats/filtres/localisation/place',
    '/reservations/details/(.+)',
    '/reservations/details/(.+)/qrcode',
    '/reservations/details/(.+)/reservation/annulation/confirmation',
    '/favoris/details/(.+)/(.+)',
    '/favoris/details/(.+)/(.+)/reservation',
    '/favoris/details/(.+)/(.+)/reservation/(.+)/annulation/confirmation',
  ]

  return RegExp(`(${pathWithColoredHeader.join('|')})$`).test(pathname)
}
