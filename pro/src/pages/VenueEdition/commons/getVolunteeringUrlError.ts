export const getVolunteeringUrlError = (url: string): string | undefined => {
  // ensures the url path is exactly /organisations/{slug} with an optional trailing slash
  const organizationPathRegex = /^\/organisations\/[^/]+\/?$/

  if (!url?.trim()) {
    return undefined
  }

  try {
    const parsed = new URL(url)

    const host = parsed.hostname.toLowerCase()
    if (host !== 'www.jeveuxaider.gouv.fr' && host !== 'jeveuxaider.gouv.fr') {
      return 'Veuillez renseigner une URL provenant de la plateforme jeveuxaider.gouv'
    }

    const path = parsed.pathname.toLowerCase()
    if (!organizationPathRegex.test(path)) {
      return 'Veuillez renseigner l’URL de votre page organisation. Ex : https://www.jeveuxaider.gouv.fr/organisations/exemple'
    }

    return undefined
  } catch {
    return 'Veuillez renseigner une URL valide. Ex : https://exemple.com'
  }
}
