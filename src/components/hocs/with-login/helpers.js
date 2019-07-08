export const DEFAULT_TYPEFORM_LOCATION = '/typeform'

export const getRedirectToSignin = ({ pathname, search }) => {
  const fromUrl = encodeURIComponent(`${pathname}${search}`)
  return `/connexion?de=${fromUrl}`
}

export const getRedirectToCurrentLocationOrTypeform = ({ currentUser }) => {
  const { needsToFillCulturalSurvey } = currentUser || {}
  if (needsToFillCulturalSurvey) {
    return DEFAULT_TYPEFORM_LOCATION
  }
  return undefined
}

export const getRedirectToCurrentLocationOrDiscovery = ({ currentUser }) => {
  const { needsToFillCulturalSurvey } = currentUser || {}
  if (!needsToFillCulturalSurvey) {
    return '/decouverte'
  }
  return undefined
}
