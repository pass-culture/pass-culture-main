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
    '/profil/email',
  ]

  return !RegExp(`(${pathsWithoutNavBar.join('|')})$`).test(path)
}
