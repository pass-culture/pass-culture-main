export const DEFAULT_TYPEFORM_LOCATION = '/typeform'

export const getRedirectToCurrentLocationOrTypeform = ({
  currentUser,
  location,
}) => {
  const { hasFilledCulturalSurvey } = currentUser || {}
  const currentLocation = `${location.pathname}${location.search}`
  return hasFilledCulturalSurvey ? currentLocation : DEFAULT_TYPEFORM_LOCATION
}

export const getRedirectToCurrentLocationOrDiscovery = ({
  currentUser,
  location,
}) => {
  const { hasFilledCulturalSurvey } = currentUser || {}
  const currentLocation = `${location.pathname}${location.search}`
  return hasFilledCulturalSurvey ? '/decouverte' : currentLocation
}
