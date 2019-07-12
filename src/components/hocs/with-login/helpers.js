export const DEFAULT_TYPEFORM_LOCATION = '/typeform'

export const getRedirectToSignin = ({ pathname, search }) => {
  const fromUrl = encodeURIComponent(`${pathname}${search}`)
  return `/connexion?de=${fromUrl}`
}

export const getRedirectToCurrentLocationOrTypeform = ({ currentUser, pathname, search }) => {
  const { needsToFillCulturalSurvey } = currentUser || {}
  const currentLocation = `${pathname}${search}`
  return needsToFillCulturalSurvey ? DEFAULT_TYPEFORM_LOCATION : currentLocation
}

export const getRedirectToCurrentLocationOrDiscovery = ({ currentUser, pathname, search }) => {
  const { needsToFillCulturalSurvey } = currentUser || {}
  const currentLocation = `${pathname}${search}`
  return needsToFillCulturalSurvey ? currentLocation : '/decouverte'
}
