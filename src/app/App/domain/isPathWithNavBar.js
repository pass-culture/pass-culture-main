export const isPathWithNavBar = path => {
  const pathsWithoutNavBar = [
    '/',
    '/reservation',
    '/informations',
    '/mot-de-passe',
    '/mentions-legales',
    '/criteres-(.*)',
    '/filtres(.*)',
    '/bienvenue',
    '/typeform',
  ]

  return !RegExp(`(${pathsWithoutNavBar.join('|')})$`).test(path)
}
