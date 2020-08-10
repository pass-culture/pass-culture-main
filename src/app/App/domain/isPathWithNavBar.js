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
  ]

  return !RegExp(`(${pathsWithoutNavBar.join('|')})$`).test(path)
}
