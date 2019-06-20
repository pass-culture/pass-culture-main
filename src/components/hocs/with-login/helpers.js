export const DEFAULT_TYPEFORM_LOCATION = '/typeform'

export const getRedirectToCurrentLocationOrTypeform = ({
  currentUser,
  location,
}) => {
  const { needsToFillCulturalSurvey } = currentUser || {}
  const currentLocation = `${location.pathname}${location.search}`
  return needsToFillCulturalSurvey ? DEFAULT_TYPEFORM_LOCATION : currentLocation
}

export const getRedirectToCurrentLocationOrDiscovery = ({
  currentUser,
  location,
}) => {
  const { needsToFillCulturalSurvey } = currentUser || {}
  const currentLocation = `${location.pathname}${location.search}`
  return needsToFillCulturalSurvey ? currentLocation : '/decouverte'
}
