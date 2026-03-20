export const getVolunteeringUrlError = (url: string): string | undefined => {
  // ensures the url path is exactly /organisations/{slug} with an optional trailing slash
  const organizationPathRegex = /^\/organisations\/[^/]+\/?$/

  const INVALID_URL_MSG =
    'Veuillez renseigner une URL valide. Ex : https://exemple.com'
  const WRONG_HOST_MSG =
    'Veuillez renseigner une URL provenant de la plateforme jeveuxaider.gouv'
  const WRONG_PATH_MSG =
    'Veuillez renseigner l’URL de votre page organisation. Ex : https://www.jeveuxaider.gouv.fr/organisations/exemple'

  if (!url?.trim()) {
    return undefined
  }

  try {
    const parsed = new URL(url)
    const host = parsed.hostname.toLowerCase()
    if (host !== 'www.jeveuxaider.gouv.fr' && host !== 'jeveuxaider.gouv.fr') {
      return WRONG_HOST_MSG
    }
    const path = parsed.pathname.toLowerCase()
    if (!organizationPathRegex.test(path)) {
      return WRONG_PATH_MSG
    }
    return undefined
  } catch {
    return INVALID_URL_MSG
  }
}
