export const shouldStatusBarBeColored = pathname => {
  const pathWithColoredHeader = [
    '/accueil',
    '/accueil/details/(.+)',
    '/accueil/details/(.+)',
    '/recherche/criteres-categorie',
    '/recherche/criteres-localisation',
    '/recherche/criteres-localisation/place',
    '/recherche/criteres-tri',
    '/recherche/resultats/tri',
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
    '/profil/informations',
    '/profil/mot-de-passe',
    '/profil/mentions-legales',
  ]

  return RegExp(`(${pathWithColoredHeader.join('|')})$`).test(pathname)
}
