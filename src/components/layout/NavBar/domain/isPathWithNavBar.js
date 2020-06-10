export const isPathWithNavBar = path => {
  const pathsWithoutNavBar = [
    '/',
    '/reservation',
    '/informations',
    '/mot-de-passe',
    '/mentions-legales',
    '/criteres-(.*)',
    '/tri',
    '/filtres(.*)',
    '/bienvenue',
    '/typeform',
    '/beta',
    '/connexion',
    '/mot-de-passe-perdu(.*)',
    '/activation/(.*)',
    '/inscription',
  ]

  return !RegExp(`(${pathsWithoutNavBar.join('|')})$`).test(path)
}
